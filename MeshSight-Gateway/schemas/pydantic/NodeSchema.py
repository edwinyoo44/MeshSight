from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class InfoItem(BaseModel):
    nodeId: int  # node ID
    longName: str  # 長名稱
    shortName: str  # 短名稱
    hardware: Optional[str]  # 硬體
    isLicensed: bool  # 執照狀態
    role: str  # 角色
    firmware: Optional[str]  # 韌體
    loraRegion: Optional[str]  # LoRa 區域
    loraModemPreset: Optional[str]  # LoRa Modem preset
    hasDefaultChannel: bool  # 是否有預設頻道
    numOnlineLocalNodes: int  # 本地節點數
    updateAt: datetime  # 更新時間
    channel: str  # 頻道


class PostionItem(BaseModel):
    nodeId: int  # node ID
    latitude: float  # 緯度
    longitude: float  # 經度
    altitude: Optional[float]  # 高度
    precisionBit: Optional[int]  # 精度
    satsInView: Optional[int]  # 可見衛星數
    updateAt: datetime  # 更新時間
    viaId: int  # 來源 node ID
    viaIdHex: str  # 來源 node ID HEX
    channel: str  # 頻道
