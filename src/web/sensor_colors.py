class SensorColors:

    @staticmethod
    def temperature(value: float) -> str:

        if value <= 15.0:
            temp_color = "text-blue-600"
        elif 15.0 < value <= 25.0:
            temp_color = "text-green-600"
        elif 25.0 < value <= 30.0:
            temp_color = "text-yellow-400"
        else:
            temp_color = "text-red-600"
        return temp_color

    @staticmethod
    def pressure(value: float) -> str:

        if value <= 950.0:
            pressure_color = "text-blue-600"
        elif 950.0 < value <= 1000.0:
            pressure_color = "text-green-600"
        elif 1050.0 < value <= 1100.0:
            pressure_color = "text-yellow-400"
        else:
            pressure_color = "text-red-600"
        return pressure_color

    @staticmethod
    def humidity(value: float) -> str:

        if value <= 20.0:
            humidity_color = "text-blue-600"
        elif 20.0 < value <= 40.0:
            humidity_color = "text-green-600"
        elif 40.0 < value <= 60.0:
            humidity_color = "text-yellow-400"
        else:
            humidity_color = "text-red-600"

        return humidity_color

    @staticmethod
    def smoke(value: int) -> str:

        if value <= 5.0:
            smoke_color = "text-blue-600"
        elif 5.0 < value <= 20.0:
            smoke_color = "text-green-600"
        elif 20.0 < value <= 40.0:
            smoke_color = "text-yellow-400"
        elif 40.0 < value <= 60.0:
            smoke_color = "text-orange-600"
        else:
            smoke_color = "text-red-600"

        return smoke_color

    @staticmethod
    def metals(value: int) -> str:

        if value <= 10.0:
            metals_color = "text-blue-600"
        elif 10.0 < value <= 25.0:
            metals_color = "text-green-600"
        elif 25.0 < value <= 50.0:
            metals_color = "text-yellow-400"
        elif 50.0 < value <= 100.0:
            metals_color = "text-orange-600"
        else:
            metals_color = "text-red-600"

        return metals_color

    @staticmethod
    def dust(value: int) -> str:
        if value <= 30.0:
            dust_color = "text-blue-600"
        elif 30.0 < value <= 50.0:
            dust_color = "text-green-600"
        elif 50.0 < value <= 100.0:
            dust_color = "text-yellow-400"
        elif 100.0 < value <= 150.0:
            dust_color = "text-orange-600"
        else:
            dust_color = "text-red-600"

        return dust_color

    @staticmethod
    def mikro(value: float) -> str:

        if value <= 100.0:
            mikro_color = "text-blue-600"
        elif 100.0 < value <= 250.0:
            mikro_color = "text-green-600"
        elif 250.0 < value <= 500.0:
            mikro_color = "text-yellow-400"
        elif 500.0 < value <= 1000.0:
            mikro_color = "text-orange-600"
        else:
            mikro_color = "text-red-600"

        return mikro_color

    @staticmethod
    def small(value: float) -> str:

        if value <= 100.0:
            small_color = "text-blue-600"
        elif 100.0 < value <= 200.0:
            small_color = "text-green-600"
        elif 200.0 < value <= 400.0:
            small_color = "text-yellow-400"
        elif 400.0 < value <= 800.0:
            small_color = "text-orange-600"
        else:
            small_color = "text-red-600"

        return small_color

    @staticmethod
    def medium(value: float) -> str:

        if value <= 50.0:
            medium_color = "text-blue-600"
        elif 50.0 < value <= 100.0:
            medium_color = "text-green-600"
        elif 100.0 < value <= 200.0:
            medium_color = "text-yellow-400"
        elif 200.0 < value <= 400.0:
            medium_color = "text-orange-600"
        else:
            medium_color = "text-red-600"

        return medium_color
