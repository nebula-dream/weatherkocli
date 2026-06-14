DIRECTIONS = {
    "ko": [
        "북", "북북동", "북동", "동북동",
        "동", "동남동", "남동", "남남동",
        "남", "남남서", "남서", "서남서",
        "서", "서북서", "북서", "북북서",
    ],
    "en": [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ],
}


def degrees_to_direction(degrees: float, lang: str) -> str:
    normalized = degrees % 360
    index = int((normalized / 22.5) + 0.5) % 16
    labels = DIRECTIONS.get(lang, DIRECTIONS["en"])
    return labels[index]
