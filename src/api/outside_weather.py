import os
import json
import requests
import time

from requests.exceptions import HTTPError, Timeout, ConnectionError, RequestException
from src.logger import Logger
from pathlib import Path
from dotenv import load_dotenv

class CurrentWeather():
    def __init__(self, main_logger: Logger):
        load_dotenv()

        self.main_logger = main_logger
        self.CURRENT_WEATHER_API = os.getenv("CURRENT_WEATHER_API")
        self.CACHE_FILE = "src/api/weather_cache.json"
        self.CACHE_TIME_LIMIT = 1800

    
    def _get_current_weather_data(self):
        try:
            response = requests.get(self.CURRENT_WEATHER_API, timeout=5)
            response.raise_for_status()

            data = response.json()
            weather_items = data.get("weather") or []
            weather_main = weather_items[0].get("main") if weather_items else None

            return {
                "temp": data["main"]["temp"],
                "weather": weather_main,
            }
        except Timeout as time_out:
            self.main_logger.exception(time_out)
        except ConnectionError as connection_error:
            self.main_logger.exception(connection_error)
        except HTTPError as http_err:
            self.main_logger.error(f"HTTP error: {http_err} Status code: {response.status_code}")
        except Exception as e:
            self.main_logger.exception(e)

        return {
            "temp": 0,
            "weather": "Unkown",
        }

    
    def return_weather_data(self):
        if os.path.exists(self.CACHE_FILE):
            file_age = time.time() - os.path.getmtime(self.CACHE_FILE)

            if file_age < self.CACHE_TIME_LIMIT:
                with open(self.CACHE_FILE, "r") as f:
                    return json.load(f)

            
        api_weather_call_data = self._get_current_weather_data()

        with open(self.CACHE_FILE, "w") as f:
            json.dump(api_weather_call_data, f)

        return api_weather_call_data

    