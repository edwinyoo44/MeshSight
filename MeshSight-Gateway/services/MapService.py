import inspect
import logging
from typing import List
import pytz
from exceptions.BusinessLogicException import BusinessLogicException
from datetime import datetime
from fastapi import Depends
from schemas.pydantic.MapSchema import MapCoordinatesItem, MapCoordinatesResponse
from schemas.pydantic.NodeSchema import InfoItem, PostionItem
from repositories.NodeInfoRepository import NodeInfoRepository
from repositories.NodePositionRepository import NodePositionRepository
from utils.ConfigUtil import ConfigUtil


class MapService:

    def __init__(
        self,
        nodeInfoRepository: NodeInfoRepository = Depends(),
        nodePositionRepository: NodePositionRepository = Depends(),
    ) -> None:
        self.config = ConfigUtil.read_config()
        self.logger = logging.getLogger(__name__)
        self.nodeInfoRepository = nodeInfoRepository
        self.nodePositionRepository = nodePositionRepository

    async def coordinates(self, start: str, end: str) -> MapCoordinatesResponse:
        try:
            try:
                start_time = datetime.fromisoformat(start)
                end_time = datetime.fromisoformat(end)
            except ValueError:
                raise BusinessLogicException("查詢日期格式錯誤")

            # 取得時間區間更新的節點 ID
            node_ids = await self.nodePositionRepository.fetch_node_ids_by_time_range(
                start_time, end_time
            )

            # 取得節點座標資料
            items: List[MapCoordinatesItem] = []
            for node_id in node_ids:
                node_info: InfoItem = (
                    await self.nodeInfoRepository.fetch_node_info_by_node_id(node_id)
                )
                node_positions: List[PostionItem] = (
                    await self.nodePositionRepository.fetch_node_position_by_node_id(
                        node_id, 3
                    )
                )
                items.append(
                    MapCoordinatesItem(
                        id=node_id,
                        info=node_info,
                        positions=node_positions,
                    )
                )

            return MapCoordinatesResponse(items=items)
        except BusinessLogicException as e:
            raise Exception(f"{str(e)}")
        except Exception as e:
            self.logger.error(f"{inspect.currentframe().f_code.co_name}: {str(e)}")
            raise Exception("內部伺服器錯誤，請稍後再試")
