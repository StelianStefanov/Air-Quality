import os
import json
import requests
import time

from pathlib import Path
from dotenv import load_dotenv

class CurrentWeather():
    def __init__(self):
        load_dotenv()
        self.CURRENT_WEATHER_API = os.getenv("CURRENT_WEATHER_API")
        self.CACHE_FILE = "src/api/weather_cache.json"
        self.CACHE_TIME_LIMIT = 1800

    
    def _get_current_weather_data(self):
        response = requests.get(self.CURRENT_WEATHER_API)
        response.raise_for_status()

        data = response.json()
        weather_items = data.get("weather") or []
        weather_main = weather_items[0].get("main") if weather_items else None

        return {
            "temp": data["main"]["temp"],
            "weather": weather_main,
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

    