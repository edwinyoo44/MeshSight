import logging
import math
import os
import traceback
from datetime import datetime
from redis import Redis
from redis.exceptions import RedisError
from app.utils.ConfigUtil import ConfigUtil

logger = logging.getLogger(__name__)


class OtherUtil:
    _redis_client = None
    _redis_disabled = False

    # 檢查並處理 NaN 值
    def sanitize_value(value):
        if isinstance(value, float) and math.isnan(value):
            return None
        return value

    def _cache_config():
        return ConfigUtil().read_config()["cache"]

    def _cache_ttl():
        return int(OtherUtil._cache_config().get("ttl", 3600))

    def _cache_key_prefix():
        return OtherUtil._cache_config().get("keyPrefix", "meshsight:cache")

    def _cache_key(filename: str):
        return f"{OtherUtil._cache_key_prefix()}:{filename}"

    def _build_redis_client():
        cache_config = OtherUtil._cache_config()
        redis_config = cache_config.get("redis", {})
        return Redis(
            host=redis_config.get("host", "meshsight-gateway-garnet"),
            port=int(redis_config.get("port", 6379)),
            db=int(redis_config.get("db", 0)),
            username=redis_config.get("username") or None,
            password=redis_config.get("password") or None,
            socket_timeout=float(redis_config.get("socketTimeout", 2)),
            decode_responses=True,
        )

    def _get_redis_client():
        if OtherUtil._redis_disabled:
            return None
        cache_config = OtherUtil._cache_config()
        redis_config = cache_config.get("redis", {})
        if not redis_config.get("enabled", False):
            return None
        if OtherUtil._redis_client is None:
            try:
                OtherUtil._redis_client = OtherUtil._build_redis_client()
                OtherUtil._redis_client.ping()
                logger.info("Redis cache backend enabled.")
            except RedisError:
                stacktrace = traceback.format_exc()
                logger.warning("Redis cache unavailable, fallback to file cache.")
                logger.debug(stacktrace)
                OtherUtil._redis_disabled = True
                OtherUtil._redis_client = None
        return OtherUtil._redis_client

    def _read_cache_json_file(filename: str) -> str:
        cache_file_path = f"{OtherUtil._cache_config()['path']}/{filename}.json"
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        if not os.path.exists(cache_file_path):
            return None
        if os.path.getmtime(cache_file_path) < datetime.now().timestamp() - OtherUtil._cache_ttl():
            return None
        with open(cache_file_path, "r") as cache_file:
            content = cache_file.read()
            if not content:
                return None
            return content

    def _write_cache_json_file(filename: str, data: str):
        cache_file_path = f"{OtherUtil._cache_config()['path']}/{filename}.json"
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, "w") as cache_file:
            cache_file.write(data)

    def read_cache_json(filename: str) -> str:
        try:
            redis_client = OtherUtil._get_redis_client()
            if redis_client is not None:
                return redis_client.get(OtherUtil._cache_key(filename))
            return OtherUtil._read_cache_json_file(filename)
        except Exception as e:
            stacktrace = traceback.format_exc()
            logger.info(stacktrace)
            raise e

    def write_cache_json(filename: str, data: str):
        try:
            redis_client = OtherUtil._get_redis_client()
            if redis_client is not None:
                redis_client.setex(OtherUtil._cache_key(filename), OtherUtil._cache_ttl(), data)
                return
            OtherUtil._write_cache_json_file(filename, data)
        except RedisError:
            logger.warning("Redis write failed, fallback to file cache.")
            OtherUtil._write_cache_json_file(filename, data)
        except Exception as e:
            stacktrace = traceback.format_exc()
            logger.info(stacktrace)
            raise e

    def clear_cache():
        redis_client = OtherUtil._get_redis_client()
        if redis_client is not None:
            total_deleted = 0
            for key in redis_client.scan_iter(match=f"{OtherUtil._cache_key_prefix()}:*"):
                total_deleted += redis_client.delete(key)
            return ("redis", total_deleted)

        cache_path = OtherUtil._cache_config()["path"]
        total_deleted = 0
        for filename in os.listdir(cache_path):
            file_path = os.path.join(cache_path, filename)
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                if file_time < datetime.now().timestamp() - 86400:
                    os.remove(file_path)
                    total_deleted += 1
        return ("file", total_deleted)
