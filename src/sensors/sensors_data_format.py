class SensorsDataFormat:
    """It formats the data depending on its value and colorizes the data.
    Also, it returns the data as a formatted string."""

    def _temperature(self, value: float) -> str:
        formatted_temperature = round(value, 2)
        if value <= 15.0:
            formatted_temperature = f"[dodger_blue1]{formatted_temperature}°C[/dodger_blue1]"
        elif 15.0 < value <= 25.0:
            formatted_temperature = f"[green3]{formatted_temperature}°C[/green3]"
        elif 25.0 < value <= 30.0:
            formatted_temperature = f"[yellow3]{formatted_temperature}°C[/yellow3]"
        else:
            formatted_temperature = f"[red]{formatted_temperature}°C[/red]"

        return f"Temp: {formatted_temperature}"

    def _pressure(self, value: float) -> str:
        formatted_pressure = round(value, 1)
        if value <= 950.0:
            formatted_pressure = f"[dodger_blue1]{formatted_pressure}HPa[/dodger_blue1]"
        elif 950.0 < value <= 1000.0:
            formatted_pressure = f"[green3]{formatted_pressure}HPa[/green3]"
        elif 1050.0 < value <= 1100.0:
            formatted_pressure = f"[yellow3]{formatted_pressure}HPa[/yellow3]"
        else:
            formatted_pressure = f"[red]{formatted_pressure}HPa[/red]"

        return f"Pressure: {formatted_pressure}"

    def _humidity(self, value: float) -> str:
        formatted_humidity = round(value, 1)
        if value <= 20.0:
            formatted_humidity = f"[dodger_blue1]{formatted_humidity}%[/dodger_blue1]"
        elif 20.0 < value <= 40.0:
            formatted_humidity = f"[green3]{formatted_humidity}%[/green3]"
        elif 40.0 < value <= 60.0:
            formatted_humidity = f"[yellow3]{formatted_humidity}%[/yellow3]"
        else:
            formatted_humidity = f"[red]{formatted_humidity}%[/red]"

        return f"Humidity: {formatted_humidity}"

    def _smoke(self, value: int) -> str:
        formatted_smoke = round(value, 1)
        if value <= 15.0:
            formatted_smoke = f"[dodger_blue1]{formatted_smoke}µg/m³[/dodger_blue1]"
        elif 15.0 < value <= 30.0:
            formatted_smoke = f"[green3]{formatted_smoke}µg/m³[/green3]"
        elif 30.0 < value <= 100.0:
            formatted_smoke = f"[yellow3]{formatted_smoke}µg/m³[/yellow3]"
        elif 100.0 < value <= 300.0:
            formatted_smoke = f"[orange_red1]{formatted_smoke}µg/m³[/orange_red1]"
        else:
            formatted_smoke = f"[red]{formatted_smoke}µg/m³[/red]"

        return f"PM 1.0: {formatted_smoke}"

    def _metals(self, value: int) -> str:
        formatted_metals = round(value, 1)
        if value <= 12.0:
            formatted_metals = f"[dodger_blue1]{formatted_metals}µg/m³[/dodger_blue1]"
        elif 12.0 < value <= 35.0:
            formatted_metals = f"[green3]{formatted_metals}µg/m³[/green3]"
        elif 35.0 < value <= 60.0:
            formatted_metals = f"[yellow3]{formatted_metals}µg/m³[/yellow3]"
        elif 60.0 < value <= 100.0:
            formatted_metals = f"[orange_red1]{formatted_metals}µg/m³[/orange_red1]"
        else:
            formatted_metals = f"[red]{formatted_metals}µg/m³[/red]"

        return f"PM 2.5: {formatted_metals}"

    def _dust(self, value: int) -> str:
        formatted_dust = round(value, 1)
        if value <= 54.0:
            formatted_dust = f"[dodger_blue1]{formatted_dust}µg/m³[/dodger_blue1]"
        elif 54.0 < value <= 155.0:
            formatted_dust = f"[green3]{formatted_dust}µg/m³[/green3]"
        elif 155.0 < value <= 255.0:
            formatted_dust = f"[yellow3]{formatted_dust}µg/m³[/yellow3]"
        elif 255.0 < value <= 354.0:
            formatted_dust = f"[orange_red1]{formatted_dust}µg/m³[/orange_red1]"
        else:
            formatted_dust = f"[red]{formatted_dust}µg/m³[/red]"

        return f"PM 10: {formatted_dust}"

    def _mikro(self, value: float) -> str:
        formatted_mikro = round(value, 1)

        if value <= 2000.0:
            formatted_mikro = f"[dodger_blue1]{formatted_mikro}/0.1L[/dodger_blue1]"
        elif 2000.0 < value <= 10000.0:
            formatted_mikro = f"[green3]{formatted_mikro}/0.1L[/green3]"
        elif 10000.0 < value <= 50000.0:
            formatted_mikro = f"[yellow3]{formatted_mikro}/0.1L[/yellow3]"
        elif 50000.0 < value <= 100000.0:
            formatted_mikro = f"[orange_red1]{formatted_mikro}/0.1L[/orange_red1]"
        else:
            formatted_mikro = f"[red]{formatted_mikro}/0.1L[/red]"

        return f"PM 0.3: {formatted_mikro}"

    def _small(self, value: float) -> str:
        formatted_small = round(value, 1)

        if value <= 2000.0:
            formatted_small = f"[dodger_blue1]{formatted_small}/0.1L[/dodger_blue1]"
        elif 2000.0 < value <= 5000.0:
            formatted_small = f"[green3]{formatted_small}/0.1L[/green3]"
        elif 5000.0 < value <= 10000.0:
            formatted_small = f"[yellow3]{formatted_small}/0.1L[/yellow3]"
        elif 10000.0 < value <= 20000.0:
            formatted_small = f"[orange_red1]{formatted_small}/0.1L[/orange_red1]"
        else:
            formatted_small = f"[red]{formatted_small}/0.1L[/red]"

        return f"PM 0.5: {formatted_small}"

    def _medium(self, value: float) -> str:
        formatted_medium = round(value, 1)

        if value <= 1000.0:
            formatted_medium = f"[dodger_blue1]{formatted_medium}/0.1L[/dodger_blue1]"
        elif 1000.0 < value <= 2000.0:
            formatted_medium = f"[green3]{formatted_medium}/0.1L[/green3]"
        elif 2000.0 < value <= 3000.0:
            formatted_medium = f"[yellow3]{formatted_medium}/0.1L[/yellow3]"
        elif 3000.0 < value <= 4000.0:
            formatted_medium = f"[orange_red1]{formatted_medium}/0.1L[/orange_red1]"
        else:
            formatted_medium = f"[red]{formatted_medium}/0.1L[/red]"

        return f"PM 1.0: {formatted_medium}"

    def _oxide(self, value: float) -> str:
        formatted_oxide = round(value, 2)

        if value <= 10.0:
            formatted_oxide = f"[dodger_blue1]{formatted_oxide}K0[/dodger_blue1]"
        elif 10.0 < value <= 25.0:
            formatted_oxide = f"[green3]{formatted_oxide}K0[/green3]"
        elif 25.0 < value <= 40.0:
            formatted_oxide = f"[yellow3]{formatted_oxide}K0[/yellow3]"
        elif 50.0 < value <= 100.0:
            formatted_oxide = f"[orange_red1]{formatted_oxide}K0[/orange_red1]"
        else:
            formatted_oxide = f"[red]{formatted_oxide}K0[/red]"

        return f"Oxidation: {formatted_oxide}"

    def _reduce(self, value: float) -> str:
        formatted_reduce = round(value, 2)

        if value <= 50.0:
            formatted_reduce = f"[dodger_blue1]{formatted_reduce}K0[/dodger_blue1]"
        elif 50.0 < value <= 100.0:
            formatted_reduce = f"[green3]{formatted_reduce}K0[/green3]"
        elif 100.0 < value <= 200.0:
            formatted_reduce = f"[yellow3]{formatted_reduce}K0[/yellow3]"
        elif 200.0 < value <= 400.0:
            formatted_reduce = f"[orange_red1]{formatted_reduce}K0[/orange_red1]"
        else:
            formatted_reduce = f"[red]{formatted_reduce}K0[/red]"

        return f"Reduce: {formatted_reduce}"

    def _nh3(self, value: float) -> str:
        formatted_nh3 = round(value, 2)

        if value <= 50.0:
            formatted_nh3 = f"[dodger_blue1]{formatted_nh3}K0[/dodger_blue1]"
        elif 50.0 < value <= 100.0:
            formatted_nh3 = f"[green3]{formatted_nh3}K0[/green3]"
        elif 100.0 < value <= 200.0:
            formatted_nh3 = f"[yellow3]{formatted_nh3}K0[/yellow3]"
        elif 200.0 < value <= 400.0:
            formatted_nh3 = f"[orange_red1]{formatted_nh3}K0[/orange_red1]"
        else:
            formatted_nh3 = f"[red]{formatted_nh3}K0[/red]"

        return f"Amonia: {formatted_nh3}"

    def _overall_quaility(self, value: str) -> str:
        formatted_overall_quality = ""

        if value == " Good":
            formatted_overall_quality = f"[green3]{value}[/green3]"
        elif value == " Normal":
            formatted_overall_quality = f"[yellow3]{value}[/yellow3]"
        elif value == " Bad":
            formatted_overall_quality = f"[red]{value}[/red]"

        return f"Air Quality:{formatted_overall_quality}"

    def do_format(self, type_: str, value: int | float) -> str:
        data_format_method = getattr(self, f"_{type_}")

        return data_format_method(value)
