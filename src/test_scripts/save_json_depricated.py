def save_json(self, pms_data: dict, enviro_data: dict, enviro_gas_data: dict, overall_quality: str) -> None:
    """
    Saves sensor data to a shared memory file as a JSON byte stream.

    It saves the json into a shared file in the memory of the linux system.

    Args:
        pms_data (dict): Data collected from the PMS sensor.
        enviro_data (dict): Data collected from the Enviro sensor.
        enviro_gas_data (dict): Data collected from the EnviroGas sensor.
    """

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
    }

    try:
        data_to_write = json.dumps({**enviro_data, **pms_data, **enviro_gas_data, "quality": overall_quality})
    except Exception as e:
        data_to_write = json.dumps(default_data)

    try:
        with open("/dev/shm/sensors_memory", "w") as f:
            f.write(data_to_write)
    except Exception as e:
        self.logger.exception(e)
