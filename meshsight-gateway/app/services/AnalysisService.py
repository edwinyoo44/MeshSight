import inspect
import json
import logging
import pytz
from app.exceptions.BusinessLogicException import BusinessLogicException
from datetime import datetime
from fastapi import Depends
from app.schemas.pydantic.AnalysisSchema import (
    AnalysisActiveHourlyRecordsItem,
    AnalysisActiveHourlyRecordsResponse,
    AnalysisDistributionResponse,
)
from app.repositories.AnalysisDeviceActiveHourlyRepository import (
    AnalysisDeviceActiveHourlyRepository,
)
from app.repositories.NodeInfoRepository import NodeInfoRepository
from app.utils.ConfigUtil import ConfigUtil
from app.utils.OtherUtil import OtherUtil


class AnalysisService:

    def __init__(
        self,
        analysisDeviceActiveHourlyRepository: AnalysisDeviceActiveHourlyRepository = Depends(),
        nodeInfoRepository: NodeInfoRepository = Depends(),
    ) -> None:
        self.analysisDeviceActiveHourlyRepository = analysisDeviceActiveHourlyRepository
        self.config = ConfigUtil().read_config()
        self.logger = logging.getLogger(__name__)
        self.nodeInfoRepository = nodeInfoRepository

    async def active_hourly_records(
        self, start: str, end: str
    ) -> AnalysisActiveHourlyRecordsResponse:
        try:
            try:
                start_time = datetime.fromisoformat(start)
                end_time = datetime.fromisoformat(end)
            except ValueError:
                raise BusinessLogicException("查詢日期格式錯誤")

            cache_name = (
                "AnalysisService.active_hourly_records/"
                f"{start_time.strftime('%Y%m%d%H%M%S')}_{end_time.strftime('%Y%m%d%H%M%S')}"
            )
            cache_json = OtherUtil.read_cache_json(cache_name)
            if cache_json:
                return AnalysisActiveHourlyRecordsResponse.parse_raw(cache_json)

            active_hourly_records = (
                self.analysisDeviceActiveHourlyRepository.fetch_active_hourly_records(
                    start_time, end_time
                )
            )
            items: list[AnalysisActiveHourlyRecordsItem] = []
            for x in active_hourly_records:
                items.append(
                    AnalysisActiveHourlyRecordsItem(
                        knownCount=x.known_count,
                        unknownCount=x.unknown_count,
                        timestamp=x.hourly.astimezone(
                            pytz.timezone(self.config["timezone"])
                        ).isoformat(),
                    )
                )
            response = AnalysisActiveHourlyRecordsResponse(items=items)
            OtherUtil.write_cache_json(cache_name, json.dumps(response.dict(), default=str))
            return response
        except BusinessLogicException as e:
            raise Exception(f"{str(e)}")
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name}: {str(e)}")
            raise Exception("內部伺服器錯誤，請稍後再試")

    async def distribution(self, type: str) -> AnalysisDistributionResponse:
        try:
            cache_name = f"AnalysisService.distribution/{type}"
            cache_json = OtherUtil.read_cache_json(cache_name)
            if cache_json:
                return AnalysisDistributionResponse.parse_raw(cache_json)

            if type == "hardware":
                items = await self.nodeInfoRepository.fetch_distribution_hardware()
            elif type == "firmware":
                items = await self.nodeInfoRepository.fetch_distribution_firmware()
            elif type == "role":
                items = await self.nodeInfoRepository.fetch_distribution_role()
            else:
                raise BusinessLogicException("不支援的分布類型")
            response = AnalysisDistributionResponse(items=items)
            OtherUtil.write_cache_json(cache_name, json.dumps(response.dict(), default=str))
            return response
        except BusinessLogicException as e:
            raise Exception(f"{str(e)}")
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name}: {str(e)}")
            raise Exception("內部伺服器錯誤，請稍後再試")
