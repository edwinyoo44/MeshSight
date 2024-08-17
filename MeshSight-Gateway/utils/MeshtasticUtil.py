import logging

logger = logging.getLogger(__name__)


class MeshtasticUtil:

    def convert_node_id_from_int_to_hex(id: int):
        id_hex = f"{id:08x}"
        return id_hex

    def convert_node_id_from_hex_to_int(id: str):
        if id.startswith("!"):
            id = id.replace("!", "")
        return int(id, 16)
