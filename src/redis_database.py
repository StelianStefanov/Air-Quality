import redis
import json


class RedisDatabase:
    def __init__(self, logger) -> None:
        self.db = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)
        self.logger = logger

    def save_sensor_data(self, data_key: str, data: dict) -> None:
        try:
            json_data = json.dumps(data)
            self.db.set(data_key, json_data)
        except Exception as e:
            self.logger.exception(e)

    def get_sensor_data(self, data_key: str) -> dict:
        default_data = {
            "temperature": 0,
            "pressure": 0,
            "humidity": 0,
            "smoke": 0,
            "metals": 0,
            "dust": 0,
            "oxide": 0,
            "reduce": 0,
            "nh3": 0,
            "mikro": 0,
            "small": 0,
            "medium": 0,
            "quality": "",
        }
        try:
            get_data = self.db.get(data_key)
            return json.loads(get_data)
        except Exception as e:
            self.logger.exception(e)
            return default_data
