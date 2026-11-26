import redis
import json
from redis.backoff import NoBackoff
from redis.retry import Retry

from src.main_config import main_cnf


class SensorDataUnavailable(RuntimeError):
    """Sensor data could not be read from Redis."""


class RedisDatabase:
    def __init__(self, logger) -> None:
        self.db = redis.StrictRedis(
            host="localhost",
            port=6379,
            decode_responses=True,
            socket_connect_timeout=main_cnf.redis_connect_timeout,
            socket_timeout=main_cnf.redis_socket_timeout,
            retry=Retry(NoBackoff(), 0),
            max_connections=main_cnf.redis_max_connections,
        )
        self.logger = logger

    def save_sensor_data(self, data_key: str, data: dict) -> None:
        try:
            json_data = json.dumps(data)
            self.db.set(data_key, json_data)
        except Exception as e:
            self.logger.exception(e)

    def get_running_service(self) -> str:
        try:
            return self.db.get("running_service") or "background"
        except redis.RedisError as error:
            self.logger.exception(error)
            raise SensorDataUnavailable("Sensor data is temporarily unavailable") from error

    def get_sensor_data(self, data_key: str) -> dict:
        try:
            get_data = self.db.get(data_key)
            data = json.loads(get_data)
            if not isinstance(data, dict) or not data:
                raise ValueError("Missing sensor data")
            return data
        except (redis.RedisError, TypeError, ValueError) as error:
            self.logger.exception(error)
            raise SensorDataUnavailable("Sensor data is temporarily unavailable") from error
