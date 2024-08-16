from configs.Database import (
    get_db_connection,
    get_db_connection_async,
)
from typing import List
from fastapi import Depends
from models.NodeInfoModel import NodeInfo
from schemas.pydantic.AnalysisSchema import AnalysisHardwareStatisticsItem
from sqlalchemy import desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


class NodeInfoRepository:
    db: Session
    db_async: AsyncSession

    def __init__(
        self,
        db: Session = Depends(get_db_connection),
        db_async: AsyncSession = Depends(get_db_connection_async),
    ) -> None:
        self.db = db
        self.db_async = db_async

    async def fetch_hardware_statistics(self) -> List[AnalysisHardwareStatisticsItem]:
        query = await self.db_async.execute(
            select(NodeInfo.hw_model, func.count(NodeInfo.hw_model).label("count"))
            .group_by(NodeInfo.hw_model)
            .order_by(desc("count"))
        )
        items: List[AnalysisHardwareStatisticsItem] = []
        for x in query:
            items.append(
                AnalysisHardwareStatisticsItem(
                    hardware=x[0],
                    count=x[1],
                )
            )
        return items
