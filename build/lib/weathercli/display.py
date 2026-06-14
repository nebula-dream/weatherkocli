from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console, Group, RenderableType
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from weathercli import art, compass, theme, weathercodes
from weathercli.i18n import t
from weathercli.textwidth import display_width

MONTH_ABBR_EN = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

WEEKDAY_SHORT = {
    "ko": ["월", "화", "수", "목", "금", "토", "일"],
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
}


def parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError:
        return None


def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9.0 / 5.0 + 32.0


def format_datetime(value: Optional[datetime], lang: str) -> str:
    if value is None:
        return "--"
    weekday = WEEKDAY_SHORT[lang][value.weekday()]
    hour24 = value.hour
    hour12 = hour24 % 12
    if hour12 == 0:
        hour12 = 12
    minute = value.minute
    if lang == "ko":
        period = "오전" if hour24 < 12 else "오후"
        return f"{value.month}월 {value.day}일 ({weekday}) {period} {hour12}:{minute:02d}"
    period = "AM" if hour24 < 12 else "PM"
    month = MONTH_ABBR_EN[value.month - 1]
    return f"{month} {value.day} ({weekday}) {hour12}:{minute:02d} {period}"


def format_clock(value: Optional[datetime], lang: str) -> str:
    if value is None:
        return "--:--"
    hour24 = value.hour
    hour12 = hour24 % 12
    if hour12 == 0:
        hour12 = 12
    minute = value.minute
    if lang == "ko":
        period = "오전" if hour24 < 12 else "오후"
        return f"{period} {hour12}:{minute:02d}"
    period = "AM" if hour24 < 12 else "PM"
    return f"{hour12}:{minute:02d} {period}"


def format_temperature_pair(celsius: float, unit: str) -> str:
    rounded_c = round(celsius)
    rounded_f = round(celsius_to_fahrenheit(celsius))
    if unit == "fahrenheit":
        return f"{rounded_f}°F"
    if unit == "both":
        return f"{rounded_c}°C / {rounded_f}°F"
    return f"{rounded_c}°C"


def location_label(config: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    location = config["location"]
    lang = config["language"]
    if lang == "ko":
        name = location.get("name_ko") or location.get("name_en") or ""
        admin = location.get("admin_ko") or location.get("admin_en")
    else:
        name = location.get("name_en") or location.get("name_ko") or ""
        admin = location.get("admin_en") or location.get("admin_ko")
    return name, admin


def header_text(config: Dict[str, Any]) -> str:
    value = (config.get("header_text") or "").strip()
    return value or "weather@cli"


def build_header_block(config: Dict[str, Any]) -> List[RenderableType]:
    title = header_text(config)
    underline = "-" * display_width(title)
    return [
        Text(title, style=f"bold {theme.ACCENT}"),
        Text(underline, style=theme.TEXT_TERTIARY),
        Text(""),
    ]


def make_info_line(label: str, value: str, value_color: str) -> Text:
    line = Text()
    line.append(label, style=f"bold {theme.ACCENT}")
    line.append(": ", style=theme.TEXT_TERTIARY)
    line.append(value, style=value_color)
    return line


def build_info_lines(data: Dict[str, Any], config: Dict[str, Any]) -> List[Text]:
    lang = config["language"]
    unit = config["unit"]
    display_config = config["display"]
    lines: List[Text] = []

    name, admin = location_label(config)
    location_value = f"{name} · {admin}" if admin else name
    lines.append(make_info_line(t("label_location", lang), location_value, theme.TEXT))

    now = parse_iso_datetime(data.get("time"))
    lines.append(make_info_line(t("label_time", lang), format_datetime(now, lang), theme.TEXT))

    if display_config.get("condition", True) and data.get("weather_code") is not None:
        condition_text = weathercodes.describe(data["weather_code"], lang)
        condition_color = weathercodes.color_for(data["weather_code"])
        lines.append(make_info_line(t("label_condition", lang), condition_text, condition_color))

    if data.get("temperature") is not None:
        temperature_value = format_temperature_pair(data["temperature"], unit)
        if display_config.get("feels_like", True) and data.get("apparent_temperature") is not None:
            feels = format_temperature_pair(data["apparent_temperature"], unit)
            temperature_value += f"  ({t('feels_like_short', lang)} {feels})"
        lines.append(make_info_line(
            t("label_temperature", lang),
            temperature_value,
            theme.temperature_color(data["temperature"]),
        ))

    if data.get("temperature_max") is not None and data.get("temperature_min") is not None:
        high = format_temperature_pair(data["temperature_max"], unit)
        low = format_temperature_pair(data["temperature_min"], unit)
        lines.append(make_info_line(t("label_high_low", lang), f"{high} · {low}", theme.TEXT))

    if display_config.get("humidity", True) and data.get("humidity") is not None:
        humidity = data["humidity"]
        lines.append(make_info_line(
            t("label_humidity", lang),
            f"{round(humidity)}%",
            theme.humidity_color(humidity),
        ))

    if display_config.get("wind", True) and data.get("wind_speed") is not None:
        direction = compass.degrees_to_direction(data.get("wind_direction") or 0, lang)
        suffix = t("wind_direction_suffix", lang)
        speed = data["wind_speed"]
        lines.append(make_info_line(
            t("label_wind", lang),
            f"{speed:.1f} m/s {direction}{suffix}",
            theme.wind_color(speed),
        ))

    if display_config.get("precipitation", True) and data.get("precipitation") is not None:
        precipitation = data["precipitation"]
        lines.append(make_info_line(
            t("label_precipitation", lang),
            f"{precipitation:.1f} mm",
            theme.precipitation_color(precipitation),
        ))

    if display_config.get("uv", False) and data.get("uv_index_max") is not None:
        uv = data["uv_index_max"]
        lines.append(make_info_line(
            t("label_uv", lang),
            f"{uv:.1f}",
            theme.uv_color(uv),
        ))

    if display_config.get("sun", True):
        sunrise = parse_iso_datetime(data.get("sunrise"))
        sunset = parse_iso_datetime(data.get("sunset"))
        if sunrise is not None and sunset is not None:
            sun_value = f"{format_clock(sunrise, lang)} / {format_clock(sunset, lang)}"
            lines.append(make_info_line(t("label_sun", lang), sun_value, theme.TEXT))

    return lines


def build_footer(config: Dict[str, Any]) -> RenderableType:
    lang = config["language"]
    return Text(t("hint_settings", lang), style=f"italic {theme.TEXT_TERTIARY}")


def block_width(lines: List[RenderableType]) -> int:
    widest = 0
    for line in lines:
        if isinstance(line, Text):
            widest = max(widest, display_width(line.plain))
    return widest


def render_weather(
    data: Dict[str, Any],
    config: Dict[str, Any],
    console: Optional[Console] = None,
    art_override: Optional[List[RenderableType]] = None,
) -> None:
    console = console or Console()

    header_lines = build_header_block(config)
    info_lines = build_info_lines(data, config)

    right_lines: List[RenderableType] = [*header_lines, *info_lines]
    if art_override is not None:
        art_lines: List[RenderableType] = list(art_override)
    else:
        art_lines = list(art.get_art_lines(config))

    right_block = Group(*right_lines)
    art_block = Group(*art_lines)

    gap = 4
    art_w = block_width(art_lines)
    info_w = block_width(right_lines)

    if console.width >= art_w + info_w + gap:
        grid = Table.grid(padding=(0, gap, 1, 0))
        grid.add_column()
        grid.add_column()
        grid.add_row(art_block, right_block)
        body: RenderableType = grid
    else:
        body = Group(art_block, Text(""), right_block)

    sections: List[RenderableType] = [body, Text(""), build_footer(config)]
    console.print(Padding(Group(*sections), (1, 2)))
