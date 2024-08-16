import logging
import traceback
import yaml

logger = logging.getLogger(__name__)


class ConfigUtil:
    def read_config():
        try:
            with open("/workspace/config/config.yaml", "r") as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            stacktrace = traceback.format_exc()
            logger.info(stacktrace)
            raise e
