import asyncio
import logging
import multiprocessing
import uvicorn
from alembic.config import Config
from alembic import command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from fastapi.middleware.cors import CORSMiddleware
from services.AnalyzeService import AnalyzeService
from services.MqttListenerService import MqttListenerService
from utils.ConfigUtil import ConfigUtil

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 設定檔讀取
config = ConfigUtil.read_config()


# FastAPI app 設定
app = FastAPI()

# CORS middleware 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO 路由設定
# app.include_router(HellWorldRouter.router)


async def start_api():
    logger.info("API 服務正在啟動...")
    process = await asyncio.create_subprocess_exec(
        "gunicorn",
        "main:app",
        "--bind",
        "0.0.0.0:80",
        "--workers",
        f"{multiprocessing.cpu_count() * 2 + 1}",
        "--worker-class",
        "uvicorn.workers.UvicornWorker",
        "--forwarded-allow-ips",
        "*",
        "--proxy-protocol",
    )
    await process.communicate()
    logger.info("API 服務已啟動")


async def start_mqtt_listener():
    logger.info("MQTT Linstener 正在啟動...")
    task_job = asyncio.create_task(MqttListenerService().start())
    logger.info("MQTT Linstener 已啟動")


def start_scheduler_job():
    logger.info("正在啟動排程任務......")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(AnalyzeService().analyze_active_device, CronTrigger(minute=0))
    scheduler.start()


async def main():
    logger.info("MeshSight-Gateway is running...")
    logger.info("正在初始化資料模型屬性...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    # 啟動排程任務
    start_scheduler_job()
    logger.info("正在啟動子服務......")
    api_task = asyncio.create_task(start_api())
    mqtt_listener_task = asyncio.create_task(start_mqtt_listener())
    # 並行運行子服務
    await asyncio.gather(asyncio.Future(), api_task, mqtt_listener_task)


# 啟動應用程式
if __name__ == "__main__":
    # 修改 uvicorn 存取日誌時間格式，加上時間戳，方便查看
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"][
        "fmt"
    ] = "%(asctime)s - %(levelname)s - %(message)s"
    # fastapi 日誌，無 handler，加一個
    ch = logging.StreamHandler(stream=None)
    fastapi_logger.addHandler(ch)
    fastapi_logger.setLevel(logging.DEBUG)
    asyncio.run(main())
else:
    # 取得 gunicorn 日誌
    gunicorn_error_logger = logging.getLogger("gunicorn.error")  # 預設是info
    # uvicorn 日誌, 可以考慮註解，提高性能
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
    uvicorn_access_logger.setLevel(gunicorn_error_logger.level)
    # fastapi 日誌
    fastapi_logger.handlers = gunicorn_error_logger.handlers
    fastapi_logger.setLevel(gunicorn_error_logger.level)
