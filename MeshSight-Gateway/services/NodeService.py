from datetime import datetime
import inspect
import logging
from exceptions.BusinessLogicException import BusinessLogicException
from fastapi import Depends
from schemas.pydantic.NodeSchema import NodeInfoResponse, NodeTelemetryDeviceResponse
from repositories.NodeInfoRepository import NodeInfoRepository
from repositories.NodeTelemetryDeviceRepository import NodeTelemetryDeviceRepository
from utils.ConfigUtil import ConfigUtil
from utils.MeshtasticUtil import MeshtasticUtil


class NodeService:

    def __init__(
        self,
        nodeInfoRepository: NodeInfoRepository = Depends(),
        nodeTelemetryDeviceRepository: NodeTelemetryDeviceRepository = Depends(),
    ) -> None:
        self.config = ConfigUtil.read_config()
        self.logger = logging.getLogger(__name__)
        self.nodeInfoRepository = nodeInfoRepository
        self.nodeTelemetryDeviceRepository = nodeTelemetryDeviceRepository

    async def info(self, node_id: int) -> NodeInfoResponse:
        try:
            return NodeInfoResponse(
                id=node_id,
                idHex=f"!{MeshtasticUtil.convert_node_id_from_int_to_hex(node_id)}",
                item=await self.nodeInfoRepository.fetch_node_info_by_node_id(node_id),
            )
        except BusinessLogicException as e:
            raise Exception(f"{str(e)}")
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name}: {str(e)}")
            raise Exception("內部伺服器錯誤，請稍後再試")

    async def telemetry_device(
        self, node_id: int, start: str, end: str
    ) -> NodeTelemetryDeviceResponse:
        try:
            start_time = datetime.fromisoformat(start).replace(second=0, microsecond=0)
            end_time = datetime.fromisoformat(end).replace(second=0, microsecond=0)
        except ValueError:
            raise BusinessLogicException("查詢日期格式錯誤")
        try:
            self.logger.error(
                f"node_id: {node_id}, start: {start_time}, end: {end_time}"
            )
            response: NodeTelemetryDeviceResponse = NodeTelemetryDeviceResponse(
                id=node_id,
                idHex=f"!{MeshtasticUtil.convert_node_id_from_int_to_hex(node_id)}",
                items=await self.nodeTelemetryDeviceRepository.fetch_data_by_time_range(
                    node_id, start_time, end_time
                ),
            )
            return response
        except BusinessLogicException as e:
            raise Exception(f"{str(e)}")
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name}: {str(e)}")
            raise Exception("內部伺服器錯誤，請稍後再試")