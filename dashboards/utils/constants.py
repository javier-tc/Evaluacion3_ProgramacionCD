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

HYPOTHESIS_PAIRS = [
    {"var_x": "temp_max", "var_y": "O3", "expected": "positive", "label": "Temperatura ↔ O3"},
    {"var_x": "rain_sum", "var_y": "MP25", "expected": "negative", "label": "Lluvia ↔ MP2.5"},
    {"var_x": "rain_sum", "var_y": "MP10", "expected": "negative", "label": "Lluvia ↔ MP10"},
    {"var_x": "wind_speed_max", "var_y": "CO", "expected": "negative", "label": "Viento ↔ CO"},
    {"var_x": "wind_speed_max", "var_y": "NO2", "expected": "negative", "label": "Viento ↔ NO2"},
]
