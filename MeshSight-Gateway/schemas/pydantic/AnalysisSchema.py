from datetime import datetime
from typing import List
from pydantic import BaseModel


class AnalysisActiveHourlyRecordsItem(BaseModel):
    knownCount: int  # 已知節點數量
    unknownCount: int  # 未知節點數量
    timestamp: datetime  # 時間戳記


class AnalysisActiveHourlyRecordsResponse(BaseModel):
    items: List[AnalysisActiveHourlyRecordsItem]
