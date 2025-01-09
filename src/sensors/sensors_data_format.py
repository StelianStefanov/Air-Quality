class SensorsDataFormat:

    def _temperature(self, value: float) -> str:
        formatted_temperature = round(value, 2)
        if value <= 15.0:
            formatted_temperature = f"[dodger_blue1]{formatted_temperature}°C[/dodger_blue1]"
        elif 15.0 < value <= 25.0:
            formatted_temperature = f"[green]{formatted_temperature}°C[/green]"
        elif 25.0 < value <= 30.0:
            formatted_temperature = f"[yellow]{formatted_temperature}°C[/yellow]"
        else:
            formatted_temperature = f"[red]{formatted_temperature}°C[/red]"

        return f"Temperature: {formatted_temperature}"

    def _pressure(self, value: float) -> str:
        formatted_pressure = round(value, 1)
        if value <= 950.0:
            formatted_pressure = f"[dodger_blue1]{formatted_pressure}HPa[/dodger_blue1]"
        elif 950.0 < value <= 1000.0:
            formatted_pressure = f"[green]{formatted_pressure}HPa[/green]"
        elif 1050.0 < value <= 1100.0:
            formatted_pressure = f"[yellow]{formatted_pressure}HPa[/yellow]"
        else:
            formatted_pressure = f"[red]{formatted_pressure}HPa[/red]"

        return f"Pressure: {formatted_pressure}"

    def _humidity(self, value: float) -> str:
        formatted_humidity = round(value, 1)
        if value <= 20.0:
            formatted_humidity = f"[dodger_blue1]{formatted_humidity}%[/dodger_blue1]"
        elif 20.0 < value <= 40.0:
            formatted_humidity = f"[green]{formatted_humidity}%[/green]"
        elif 40.0 < value <= 60.0:
            formatted_humidity = f"[yellow]{formatted_humidity}%[/yellow]"
        else:
            formatted_humidity = f"[red]{formatted_humidity}%[/red]"

        return f"Humidity: {formatted_humidity}"

    def _smoke(self, value: int) -> str:
        formatted_smoke = round(value, 1)
        if value <= 15.0:
            formatted_smoke = f"[dodger_blue1]{formatted_smoke}µg/m³[/dodger_blue1]"
        elif 15.0 < value <= 30.0:
            formatted_smoke = f"[green]{formatted_smoke}µg/m³[/green]"
        elif 30.0 < value <= 100.0:
            formatted_smoke = f"[yellow]{formatted_smoke}µg/m³[/yellow]"
        elif 100.0 < value <= 300.0:
            formatted_smoke = f"[orange_red1]{formatted_smoke}µg/m³[/orange_red1]"
        else:
            formatted_smoke = f"[red]{formatted_smoke}µg/m³[/red]"

        return f"Smoke: \n{formatted_smoke}"

    def _metals(self, value: int) -> str:
        formatted_metals = round(value, 1)
        if value <= 12.0:
            formatted_metals = f"[dodger_blue1]{formatted_metals}µg/m³[/dodger_blue1]"
        elif 12.0 < value <= 35.0:
            formatted_metals = f"[green]{formatted_metals}µg/m³[/green]"
        elif 35.0 < value <= 60.0:
            formatted_metals = f"[yellow]{formatted_metals}µg/m³[/yellow]"
        elif 60.0 < value <= 100.0:
            formatted_metals = f"[orange_red1]{formatted_metals}µg/m³[/orange_red1]"
        else:
            formatted_metals = f"[red]{formatted_metals}µg/m³[/red]"

        return f"Metals: {formatted_metals}"

    def _dust(self, value: int) -> str:
        formatted_dust = round(value, 1)
        if value <= 54.0:
            formatted_dust = f"[dodger_blue1]{formatted_dust}µg/m³[/dodger_blue1]"
        elif 54.0 < value <= 155.0:
            formatted_dust = f"[green]{formatted_dust}µg/m³[/green]"
        elif 155.0 < value <= 255.0:
            formatted_dust = f"[yellow]{formatted_dust}µg/m³[/yellow]"
        elif 255.0 < value <= 354.0:
            formatted_dust = f"[orange_red1]{formatted_dust}µg/m³[/orange_red1]"
        else:
            formatted_dust = f"[red]{formatted_dust}µg/m³[/red]"

        return f"Dust: \n{formatted_dust}"

    def _mikro(self, value: float) -> str:
        formatted_mikro = round(value, 1)

        if value <= 2000.0:
            formatted_mikro = f"[dodger_blue1]{formatted_mikro}/0.1L[/dodger_blue1]"
        elif 2000.0 < value <= 10000.0:
            formatted_mikro = f"[green]{formatted_mikro}/0.1L[/green]"
        elif 10000.0 < value <= 50000.0:
            formatted_mikro = f"[yellow]{formatted_mikro}/0.1L[/yellow]"
        elif 50000.0 < value <= 100000.0:
            formatted_mikro = f"[orange_red1]{formatted_mikro}/0.1L[/orange_red1]"
        else:
            formatted_mikro = f"[red]{formatted_mikro}/0.1L[/red]"

        return f"Micro: {formatted_mikro}"

    def _small(self, value: float) -> str:
        formatted_small = round(value, 1)

        if value <= 2000.0:
            formatted_small = f"[dodger_blue1]{formatted_small}/0.1L[/dodger_blue1]"
        elif 2000.0 < value <= 5000.0:
            formatted_small = f"[green]{formatted_small}/0.1L[/green]"
        elif 5000.0 < value <= 10000.0:
            formatted_small = f"[yellow]{formatted_small}/0.1L[/yellow]"
        elif 10000.0 < value <= 20000.0:
            formatted_small = f"[orange_red1]{formatted_small}/0.1L[/orange_red1]"
        else:
            formatted_small = f"[red]{formatted_small}/0.1L[/red]"

        return f"Small: {formatted_small}"

    def _medium(self, value: float) -> str:
        formatted_medium = round(value, 1)

        if value <= 1000.0:
            formatted_medium = f"[dodger_blue1]{formatted_medium}/0.1L[/dodger_blue1]"
        elif 1000.0 < value <= 2000.0:
            formatted_medium = f"[green]{formatted_medium}/0.1L[/green]"
        elif 2000.0 < value <= 3000.0:
            formatted_medium = f"[yellow]{formatted_medium}/0.1L[/yellow]"
        elif 3000.0 < value <= 4000.0:
            formatted_medium = f"[orange_red1]{formatted_medium}/0.1L[/orange_red1]"
        else:
            formatted_medium = f"[red]{formatted_medium}/0.1L[/red]"

        return f"Medium: {formatted_medium}"

    def _oxide(self, value: float) -> str:
        formatted_oxide = round(value, 2)

        if value <= 10.0:
            formatted_oxide = f"[dodger_blue1]{formatted_oxide}K0[/dodger_blue1]"
        elif 10.0 < value <= 25.0:
            formatted_oxide = f"[green]{formatted_oxide}K0[/green]"
        elif 25.0 < value <= 40.0:
            formatted_oxide = f"[yellow]{formatted_oxide}K0[/yellow]"
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
            formatted_reduce = f"[green]{formatted_reduce}K0[/green]"
        elif 100.0 < value <= 200.0:
            formatted_reduce = f"[yellow]{formatted_reduce}K0[/yellow]"
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
            formatted_nh3 = f"[green]{formatted_nh3}K0[/green]"
        elif 100.0 < value <= 200.0:
            formatted_nh3 = f"[yellow]{formatted_nh3}K0[/yellow]"
        elif 200.0 < value <= 400.0:
            formatted_nh3 = f"[orange_red1]{formatted_nh3}K0[/orange_red1]"
        else:
            formatted_nh3 = f"[red]{formatted_nh3}K0[/red]"

        return f"Amonia: {formatted_nh3}"

    def do_format(self, type_: str, value: int | float) -> str:
        data_format_method = getattr(self, f"_{type_}")

        return data_format_method(value)
