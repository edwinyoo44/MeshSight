from datetime import datetime, timedelta
import inspect
import logging
import pytz
from configs.Database import (
    get_db_connection,
    get_db_connection_async,
)
from typing import List, Tuple
from fastapi import Depends
from models.NodeNeighborEdgeModel import NodeNeighborEdge
from models.NodeNeighborInfoModel import NodeNeighborInfo
from schemas.pydantic.NodeSchema import PostionItem
from sqlalchemy import desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, Session
from utils.ConfigUtil import ConfigUtil
from utils.MeshtasticUtil import MeshtasticUtil


class NodeNeighborInfoRepository:
    db: Session
    db_async: AsyncSession

    def __init__(
        self,
        db: Session = Depends(get_db_connection),
        db_async: AsyncSession = Depends(get_db_connection_async),
    ) -> None:
        self.config = ConfigUtil.read_config()
        self.db = db
        self.db_async = db_async
        self.logger = logging.getLogger(__name__)

    # 取得時間區間更新的 node_neighbor_info
    async def fetch_node_node_neighbor_info_by_time_range(
        self, start: datetime, end: datetime
    ) -> List[Tuple[NodeNeighborInfo, NodeNeighborEdge]]:
        try:
            query = await self.db_async.execute(
                select(NodeNeighborInfo, NodeNeighborEdge)
                .where(
                    NodeNeighborInfo.update_at
                    >= datetime.now()
                    - timedelta(
                        hours=int(
                            self.config["meshtastic"]["neighborinfo"]["maxQueryPeriod"]
                        )
                    )
                )  # 限制最大查詢天數
                .join(NodeNeighborEdge, NodeNeighborInfo.node_id == NodeNeighborEdge.node_id)
                .where(NodeNeighborInfo.update_at.between(start, end))
            )
            result = query.fetchall()
            return result
        except Exception as e:
            raise Exception(f"{inspect.currentframe().f_code.co_name}: {str(e)}")