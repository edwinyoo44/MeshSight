import pytz
from datetime import date, datetime, time
from fastapi import APIRouter, Depends
from schemas.pydantic.BaseSchema import BaseResponse
from services.AnalysisService import AnalysisService
from schemas.pydantic.AnalysisSchema import (
    AnalysisActiveHourlyRecordsResponse,
    AnalysisHardwareStatisticsResponse,
)
from utils.ConfigUtil import ConfigUtil

config_timezone = pytz.timezone(ConfigUtil.read_config()["timezone"])

router = APIRouter(prefix="/v1/analysis", tags=["analysis"])


@router.get(
    "/active-hourly-records",
    response_model=BaseResponse[AnalysisActiveHourlyRecordsResponse],
)
async def get_active_hourly_records(
    start: str = datetime.combine(date.today(), time())
    .astimezone(config_timezone)
    .isoformat(),
    end: str = datetime.combine(date.today(), time(23, 59, 59))
    .astimezone(config_timezone)
    .isoformat(),
    analysisService: AnalysisService = Depends(),
):
    try:
        return BaseResponse(
            status="success",
            message="success",
            data=await analysisService.active_hourly_records(start, end),
        )

    except Exception as e:
        return BaseResponse(
            status="error",
            message=str(e),
            data=None,
        )


# 取得硬體統計
@router.get(
    "/hardware-statistics",
    response_model=BaseResponse[AnalysisHardwareStatisticsResponse],
)
async def get_hardware_statistics(analysisService: AnalysisService = Depends()):
    try:
        return BaseResponse(
            status="success",
            message="success",
            data=await analysisService.hardware_statistics(),
        )

    except Exception as e:
        return BaseResponse(
            status="error",
            message=str(e),
            data=None,
        )
