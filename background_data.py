import json
import time 

from src.sensors.enviro_gas import EnviroGas
from src.sensors.enviro_sensor import EnviroSensor
from src.sensors.pms_sensor import PmsSensor
from src.logger import Logger
from src.redis_database import RedisDatabase
from src.utilities import Utilities



class BackgroundData:
    def __init__(self, logger: Logger):
        self.logger = logger
        
        self.enviro_sensor = EnviroSensor(self.logger)
        self.pms_sensor = PmsSensor(self.logger)
        self.enviro_gas_sensor = EnviroGas(self.logger)
        self.redis_db = RedisDatabase(self.logger)

    def _get_all_sensors_data(self) -> dict:
        try:
            enviro_data = self.enviro_sensor.get_data()
            pms_data = self.pms_sensor.get_data()
            enviro_gas_data = self.enviro_gas_sensor.get_data()
            
            overall_quality = Utilities.get_overall_quality(enviro_data, pms_data, enviro_gas_data)
            
            
            data = {
                "temperature": enviro_data["temperature"],
                "pressure": enviro_data["pressure"],
                "humidity": enviro_data["humidity"],
                "smoke": pms_data["smoke"],
                "metals": pms_data["metals"],
                "dust": pms_data["dust"],
                "mikro": pms_data["mikro"],
                "small": pms_data["small"],
                "medium": pms_data["medium"],
                "oxide": enviro_gas_data["oxide"],
                "reduce": enviro_gas_data["reduce"],
                "nh3": enviro_gas_data["nh3"],
            }
            
            self.redis_db.save_sensor_data(
                    "sensor_data_background", {**data, "quality": overall_quality}
                )
            
            self.redis_db.db.set("running_service", "background")
        except Exception as e:
            self.logger.exception(e)
        

def main():
    background_data = BackgroundData(Logger)
    while True:
        background_data._get_all_sensors_data()
        time.sleep(1.5)

if __name__ == "__main__":
    main()
    