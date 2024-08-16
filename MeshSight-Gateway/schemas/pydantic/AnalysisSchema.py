from datetime import datetime
from typing import List
from pydantic import BaseModel


class AnalysisActiveHourlyRecordsItem(BaseModel):
    knownCount: int  # 已知節點數量
    unknownCount: int  # 未知節點數量
    timestamp: datetime  # 時間戳記


class AnalysisActiveHourlyRecordsResponse(BaseModel):
    items: List[AnalysisActiveHourlyRecordsItem]


class AnalysisHardwareStatisticsItem(BaseModel):
    hardware: str  # 硬體名稱
    count: int  # 硬體數量


class AnalysisHardwareStatisticsResponse(BaseModel):
    items: List[AnalysisHardwareStatisticsItem]
