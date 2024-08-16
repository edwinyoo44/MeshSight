from datetime import datetime
import logging
import inspect

import pytz
from exceptions.BusinessLogicException import BusinessLogicException
from fastapi import Depends
from schemas.pydantic.AnalysisSchema import (
    AnalysisActiveHourlyRecordsItem,
    AnalysisActiveHourlyRecordsResponse,
)
from repositories.AnalysisDeviceActiveHourlyRepository import (
    AnalysisDeviceActiveHourlyRepository,
)
from utils.ConfigUtil import ConfigUtil


class AnalysisService:

    def __init__(
        self,
        analysisDeviceActiveHourlyRepository: AnalysisDeviceActiveHourlyRepository = Depends(),
    ) -> None:
        self.analysisDeviceActiveHourlyRepository = analysisDeviceActiveHourlyRepository
        self.config = ConfigUtil.read_config()
        self.logger = logging.getLogger(__name__)

    async def active_hourly_records(
        self, start: str, end: str
    ) -> AnalysisActiveHourlyRecordsResponse:
        try:
            start_time = datetime.fromisoformat(start)
            end_time = datetime.fromisoformat(end)
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
            return AnalysisActiveHourlyRecordsResponse(items=items)
        except BusinessLogicException as e:
            raise Exception(f"{str(e)}")
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name}: {str(e)}")
            raise Exception("內部伺服器錯誤，請稍後再試")
