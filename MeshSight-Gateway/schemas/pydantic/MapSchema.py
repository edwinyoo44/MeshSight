from typing import List, Optional
from pydantic import BaseModel
from .NodeSchema import InfoItem, PostionItem


class MapCoordinatesItem(BaseModel):
    id: int  # ID
    info: Optional[InfoItem]  # 資訊
    positions: List[PostionItem]  # 節點座標


class MapCoordinatesResponse(BaseModel):
    items: List[MapCoordinatesItem]
