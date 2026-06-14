from weathercli import theme

WEATHER_CODES = {
    0: {"ko": "맑음", "en": "Clear sky", "color": theme.WARNING},
    1: {"ko": "대체로 맑음", "en": "Mainly clear", "color": theme.WARNING},
    2: {"ko": "구름 조금", "en": "Partly cloudy", "color": theme.TEXT_SECONDARY},
    3: {"ko": "흐림", "en": "Overcast", "color": theme.TEXT_SECONDARY},
    45: {"ko": "안개", "en": "Fog", "color": theme.TEXT_SECONDARY},
    48: {"ko": "짙은 안개", "en": "Dense fog", "color": theme.TEXT_SECONDARY},
    51: {"ko": "약한 이슬비", "en": "Light drizzle", "color": theme.PRIMARY_DIM},
    53: {"ko": "이슬비", "en": "Drizzle", "color": theme.PRIMARY_DIM},
    55: {"ko": "강한 이슬비", "en": "Dense drizzle", "color": theme.PRIMARY},
    56: {"ko": "약한 어는 이슬비", "en": "Light freezing drizzle", "color": theme.INFO_CYAN},
    57: {"ko": "어는 이슬비", "en": "Freezing drizzle", "color": theme.INFO_CYAN},
    61: {"ko": "약한 비", "en": "Slight rain", "color": theme.PRIMARY_DIM},
    63: {"ko": "비", "en": "Rain", "color": theme.PRIMARY},
    65: {"ko": "강한 비", "en": "Heavy rain", "color": theme.ERROR},
    66: {"ko": "약한 어는 비", "en": "Light freezing rain", "color": theme.INFO_CYAN},
    67: {"ko": "어는 비", "en": "Freezing rain", "color": theme.INFO_CYAN},
    71: {"ko": "약한 눈", "en": "Slight snow fall", "color": theme.INFO_CYAN},
    73: {"ko": "눈", "en": "Snow fall", "color": theme.INFO_CYAN},
    75: {"ko": "강한 눈", "en": "Heavy snow fall", "color": theme.PRIMARY_DIM},
    77: {"ko": "싸락눈", "en": "Snow grains", "color": theme.INFO_CYAN},
    80: {"ko": "약한 소나기", "en": "Slight rain showers", "color": theme.PRIMARY_DIM},
    81: {"ko": "소나기", "en": "Rain showers", "color": theme.PRIMARY},
    82: {"ko": "강한 소나기", "en": "Violent rain showers", "color": theme.ERROR},
    85: {"ko": "약한 눈 소나기", "en": "Slight snow showers", "color": theme.INFO_CYAN},
    86: {"ko": "강한 눈 소나기", "en": "Heavy snow showers", "color": theme.PRIMARY_DIM},
    95: {"ko": "뇌우", "en": "Thunderstorm", "color": theme.ERROR},
    96: {"ko": "약한 우박을 동반한 뇌우", "en": "Thunderstorm with slight hail", "color": theme.ERROR},
    99: {"ko": "강한 우박을 동반한 뇌우", "en": "Thunderstorm with heavy hail", "color": theme.ERROR},
}

FALLBACK = {"ko": "알 수 없음", "en": "Unknown", "color": theme.TEXT_SECONDARY}


def describe(code: int, lang: str) -> str:
    entry = WEATHER_CODES.get(code, FALLBACK)
    return entry.get(lang, entry["en"])


def color_for(code: int) -> str:
    entry = WEATHER_CODES.get(code, FALLBACK)
    return entry["color"]
