from pydantic import BaseModel
import uuid


class CameraDataResponse(BaseModel):
    uuid: uuid.UUID  # UUID
    name: str  # 名稱
    rtspMainStream: str | None  # 原始 RTSP 影像主串流
