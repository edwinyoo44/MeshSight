import logging
import math

logger = logging.getLogger(__name__)


class OtherUtil:

    # 檢查並處理 NaN 值
    def sanitize_value(value):
        if isinstance(value, float) and math.isnan(value):
            return None
        return value
