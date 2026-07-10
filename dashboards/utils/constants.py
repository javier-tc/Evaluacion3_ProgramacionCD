POLLUTANTS = ["CO", "MP10", "MP25", "NO2", "O3"]

POLLUTANT_LABELS = {
    "CO": "CO",
    "MP10": "MP10",
    "MP25": "MP2.5",
    "NO2": "NO2",
    "O3": "O3",
}

UNIT_DISPLAY = {
    "ppm": "ppm",
    "ug/m3": "μg/m³",
    "ppb": "ppb",
}

WEATHER_VAR_MAP = {
    "temp_max": "Temperatura",
    "temp_min": "Temp. min",
    "rain_sum": "Lluvia",
    "precipitation_sum": "Precipitacion",
    "wind_speed_max": "Viento",
    "wind_gusts_max": "Rafagas",
    "precip_prob_max": "Prob. lluvia",
}

CORRELATION_VARS = ["CO", "MP10", "MP25", "NO2", "O3", "temp_max", "rain_sum", "wind_speed_max"]

CORRELATION_LABELS = {
    "CO": "CO",
    "MP10": "MP10",
    "MP25": "MP2.5",
    "NO2": "NO2",
    "O3": "O3",
    "temp_max": "Temperatura",
    "rain_sum": "Lluvia",
    "wind_speed_max": "Viento",
}
