PRIMARY = "#3385FF"
PRIMARY_DIM = "#5B9BFF"
SUCCESS = "#00C07F"
WARNING = "#FFA31A"
ERROR = "#FF5E56"
INFO_CYAN = "#5EEAD4"

TEXT = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
TEXT_TERTIARY = "#64748B"

SURFACE = "#0F172A"
SURFACE_SECONDARY = "#1E293B"
SURFACE_TERTIARY = "#334155"

CARD_BG = "on #16213A"
CARD_BG_ALT = "on #1B2A47"

TEMP_FREEZING = "#7DD3FC"
TEMP_COLD = "#5EEAD4"
TEMP_MILD = "#34D399"
TEMP_WARM = "#FBBF24"
TEMP_HOT = "#FB7185"
TEMP_EXTREME = "#F43F5E"

ACCENT = "#F2B8A2"

LOGO_PALETTE = [
    PRIMARY,
    SUCCESS,
    WARNING,
    ERROR,
    INFO_CYAN,
    ACCENT,
    TEXT,
    TEXT_SECONDARY,
]


def temperature_color(celsius: float) -> str:
    if celsius <= 0:
        return TEMP_FREEZING
    if celsius <= 10:
        return TEMP_COLD
    if celsius <= 20:
        return TEMP_MILD
    if celsius <= 28:
        return TEMP_WARM
    if celsius <= 33:
        return TEMP_HOT
    return TEMP_EXTREME


def humidity_color(percent: float) -> str:
    if percent < 30:
        return WARNING
    if percent <= 60:
        return SUCCESS
    if percent <= 80:
        return PRIMARY_DIM
    return ERROR


def precipitation_color(mm: float) -> str:
    if mm <= 0:
        return TEXT_SECONDARY
    if mm < 1:
        return INFO_CYAN
    if mm < 5:
        return PRIMARY
    return ERROR


def uv_color(index: float) -> str:
    if index < 3:
        return SUCCESS
    if index < 6:
        return WARNING
    if index < 8:
        return "#FB923C"
    return ERROR


def wind_color(speed_ms: float) -> str:
    if speed_ms < 4:
        return SUCCESS
    if speed_ms < 9:
        return WARNING
    return ERROR


QUESTIONARY_STYLE_MAP = {
    "qmark": f"fg:{PRIMARY} bold",
    "question": "bold",
    "answer": f"fg:{PRIMARY} bold",
    "pointer": f"fg:{PRIMARY} bold",
    "highlighted": f"fg:{PRIMARY} bold",
    "selected": f"fg:{SUCCESS}",
    "separator": f"fg:{TEXT_TERTIARY}",
    "instruction": f"fg:{TEXT_TERTIARY}",
    "text": f"fg:{TEXT}",
    "disabled": f"fg:{TEXT_TERTIARY} italic",
    "current-value": f"fg:{ACCENT} bold",
}
