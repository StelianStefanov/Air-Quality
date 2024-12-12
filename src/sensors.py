sensors = {
    "NH3": {
        "limits": [1, 100, 150, 200, 250, 300, 1000],
        "colors_range": {
            "light_blue": (0, 255, 255),
            "yellow": (179, 209, 46),
            "darker_yellow": (255, 255, 0),
            "orange": (255, 145, 0),
            "red": (255, 0, 0),
            "dark_red": (77, 0, 0),
        },
        "unit": "kO",
        "text_position": (20, 25),
    },
    "Temperature": {
        "limits": [15, 20, 25, 30],
        "colors_range": {
            "light_blue": (0, 255, 255),
            "yellow": (179, 209, 46),
            "green": (0, 255, 0),
            "orange": (255, 145, 0),
            "red": (255, 0, 0),
        },
        "unit": "°C",
        "text_position": (40, 25),
    },
    "Pressure": {
        "limits": [1000, 1013, 1030],
        "colors_range": {
            "light_blue": (0, 255, 255),
            "yellow": (255, 255, 0),
            "red": (225, 0, 0),
        },
        "unit": "hPa",
        "text_position": (17, 25),
    },
    "Humidity": {
        "limits": [30, 60],
        "colors_range": {
            "light_blue": (0, 255, 255),
            "yellow": (255, 255, 0),
            "red": (255, 0, 0),
        },
        "unit": "%",
        "text_position": (40, 25),
    },
}
