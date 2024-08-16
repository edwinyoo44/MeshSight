from datetime import datetime
from typing import List, Optional, Tuple
from pydantic import BaseModel
import uuid


class TaskDetectObjectSchema(BaseModel):
    type: str  # 類型
    confidence: float  # 信心度


class TaskCreateRequest(BaseModel):
    name: str  # 名稱
    description: str = None  # 描述
    cameraUuid: uuid.UUID  # 相機 UUID
    detectInterval: int = 5  # 偵測間隔 秒
    alertInterval: int = 10  # 警報間隔 分鐘
    enable: bool = True  # 啟用
    roiPercentPoints: List[Tuple[float, float]] = [(0, 0), (1, 1)]  # ROI 百分比範圍
    rodPercentPoints: List[Tuple[float, float]] = []  # ROD 百分比範圍
    detectObjects: List[TaskDetectObjectSchema] = [
        TaskDetectObjectSchema(type="person", confidence=0.78)
    ]  # 偵測物件


class TaskDataResponse(BaseModel):
    uuid: uuid.UUID  # UUID
    name: str  # 名稱
    description: Optional[str] = None
    cameraUuid: uuid.UUID
    detectInterval: int
    alertInterval: int
    enable: bool
    roiPercentPoints: List[Tuple[float, float]]
    rodPercentPoints: List[Tuple[float, float]]
    detectObjects: List[TaskDetectObjectSchema]
    status: str
    lastDetectTime: Optional[datetime] = None


class TaskUpdateRequest(BaseModel):
    uuid: uuid.UUID  # 任務 UUID
    name: Optional[str] = None
    description: Optional[str] = None
    detectInterval: Optional[int] = None
    alertInterval: Optional[int] = None
    enable: Optional[bool] = None
    roiPercentPoints: Optional[List[Tuple[float, float]]] = None
    rodPercentPoints: Optional[List[Tuple[float, float]]] = None
    detectObjects: Optional[List[TaskDetectObjectSchema]] = None
