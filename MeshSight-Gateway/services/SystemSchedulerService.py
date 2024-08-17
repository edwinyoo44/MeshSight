import logging
from configs.Database import get_db_connection_async
from datetime import datetime, timedelta, timezone
from models.AnalysisDeviceActiveHourlyModel import AnalysisDeviceActiveHourly
from models.NodeModel import Node
from models.NodeInfoModel import NodeInfo
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from utils.ConfigUtil import ConfigUtil


class SystemSchedulerService:

    def __init__(self) -> None:
        self.config = ConfigUtil.read_config()
        self.logger = logging.getLogger(__name__)

    # 分析當下小時，前一小時的活躍裝置數量，並存入資料庫
    async def analyze_active_device(self):
        try:
            # 取得前一小時時間
            last_hour = datetime.now(timezone.utc).replace(
                minute=0, second=0, microsecond=0
            ) - timedelta(hours=1)

            async for session in get_db_connection_async():
                try:
                    # 檢查該 hourly 是否已經存在
                    existing_record = await session.execute(
                        select(AnalysisDeviceActiveHourly).filter(
                            AnalysisDeviceActiveHourly.hourly == last_hour
                        )
                    )
                    existing_record = existing_record.scalars().first()

                    if existing_record:
                        self.logger.error(f"記錄已存在於 {last_hour}")
                        return

                    # 取得前一小時的活躍節點，並聯結 NodeInfo 表
                    node_info_alias = aliased(NodeInfo)
                    result = await session.execute(
                        select(Node, node_info_alias.uuid.label("node_info_uuid"))
                        .outerjoin(node_info_alias, Node.id == node_info_alias.node_id)
                        .filter(Node.last_heard_at >= last_hour)
                    )
                    rows = result.all()

                    # 根據如果節點有在 NodeInfo 表，則 known_count + 1 否則 unknown_count + 1
                    known_count = 0
                    unknown_count = 0
                    for row in rows:
                        node, node_info_uuid = row
                        if node_info_uuid:
                            known_count += 1
                        else:
                            unknown_count += 1

                    # 將結果插入到 AnalysisDeviceActiveHourly 表中
                    new_record = AnalysisDeviceActiveHourly(
                        hourly=last_hour,
                        known_count=known_count,
                        unknown_count=unknown_count,
                    )
                    session.add(new_record)
                    await session.commit()
                    self.logger.info(f"成功插入記錄於 {last_hour}")
                except Exception as inner_e:
                    self.logger.error(f"處理資料庫操作時發生錯誤: {inner_e}")
                    await session.rollback()
                finally:
                    await session.close()
        except Exception as e:
            self.logger.error(f"分析活躍裝置數量時發生錯誤: {e}")