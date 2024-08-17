from configs.Database import (
    get_db_connection,
    get_db_connection_async,
)
from typing import List
from fastapi import Depends
from models.NodeInfoModel import NodeInfo
from schemas.pydantic.AnalysisSchema import AnalysisDistributionItem
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

    async def fetch_distribution_firmware(self) -> List[AnalysisDistributionItem]:
        query = await self.db_async.execute(
            select(
                func.coalesce(NodeInfo.firmware_version, "Unknown").label(
                    "firmware_version"
                ),
                func.count(func.coalesce(NodeInfo.firmware_version, "Unknown")).label(
                    "count"
                ),
            )
            .group_by("firmware_version")
            .order_by(desc("count"))
        )
        result = query.fetchall()
        items: List[AnalysisDistributionItem] = [
            AnalysisDistributionItem(name=x.firmware_version, count=x.count)
            for x in result
        ]
        return items

    async def fetch_distribution_hardware(self) -> List[AnalysisDistributionItem]:
        query = await self.db_async.execute(
            select(
                func.coalesce(NodeInfo.hw_model, "Unknown").label("hw_model"),
                func.count(func.coalesce(NodeInfo.hw_model, "Unknown")).label("count"),
            )
            .group_by("hw_model")
            .order_by(desc("count"))
        )
        result = query.fetchall()
        items: List[AnalysisDistributionItem] = [
            AnalysisDistributionItem(name=x.hw_model, count=x.count) for x in result
        ]
        return items

    async def fetch_distribution_role(self) -> List[AnalysisDistributionItem]:
        query = await self.db_async.execute(
            select(
                func.coalesce(NodeInfo.role, "Unknown").label("role"),
                func.count(func.coalesce(NodeInfo.role, "Unknown")).label("count"),
            )
            .group_by("role")
            .order_by(desc("count"))
        )
        result = query.fetchall()
        items: List[AnalysisDistributionItem] = [
            AnalysisDistributionItem(name=x.role, count=x.count) for x in result
        ]
        return items
