import sys
from typing import Any, Dict, Optional

from rich.console import Console
from rich.text import Text

from weathercli import config as config_module
from weathercli import display, logos, theme
from weathercli.i18n import t
from weathercli.settings import run_settings
from weathercli.textwidth import display_width
from weathercli.weatherapi import WeatherFetchError, fetch_current_weather

SETTINGS_KEYWORDS = {"setting", "settings", "set", "config", "configure"}

HELP_TEXT = {
    "ko": (
        "사용법\n"
        "  wt                   현재 날씨를 보여줍니다\n"
        "  wt set               날씨 설정을 변경합니다\n"
        "  wt --logo list       사용 가능한 로고 목록을 보여줍니다\n"
        "  wt --logo <이름>     해당 로고로 한 번만 날씨를 보여줍니다\n"
        "  wt --logopin <이름>  해당 로고를 기본 아트로 고정합니다\n"
        "  weather              wt와 동일하게 동작합니다\n"
        "  weather set          wt set 과 동일하게 동작합니다"
    ),
    "en": (
        "Usage\n"
        "  wt                   Show the current weather\n"
        "  wt set               Change weather settings\n"
        "  wt --logo list       List available logos\n"
        "  wt --logo <name>     Show the weather once with that logo\n"
        "  wt --logopin <name>  Pin that logo as the default art\n"
        "  weather              Same as wt\n"
        "  weather set          Same as wt set"
    ),
}


def apply_calibration(data: Dict[str, Any], config: Dict[str, Any]) -> None:
    offset = config.get("calibration", {}).get("temperature_offset", 0.0)
    if not offset:
        return
    for key in ("temperature", "apparent_temperature", "temperature_max", "temperature_min"):
        if data.get(key) is not None:
            data[key] = data[key] + offset


def fetch_weather_data(config: Dict[str, Any], console: Console) -> Optional[Dict[str, Any]]:
    lang = config["language"]
    location = config["location"]

    try:
        with console.status(f"{t('loading', lang)}...", spinner="dots"):
            data = fetch_current_weather(
                location["latitude"], location["longitude"], location["timezone"]
            )
    except WeatherFetchError:
        console.print()
        console.print(Text(t("error_network_title", lang), style=f"bold {theme.ERROR}"))
        console.print(Text(t("error_network_body", lang), style=theme.TEXT_SECONDARY))
        console.print()
        return None

    apply_calibration(data, config)
    return data


def show_weather(config: Dict[str, Any], logo_name: Optional[str] = None) -> int:
    console = Console()
    lang = config["language"]

    art_override = None
    if logo_name is not None:
        art_override = logos.load_logo_lines(logo_name, config)
        if art_override is None:
            console.print()
            console.print(Text(t("logo_not_found", lang), style=f"bold {theme.ERROR}"))
            console.print(Text(t("logo_not_found_hint", lang), style=theme.TEXT_SECONDARY))
            console.print()
            return 1

    data = fetch_weather_data(config, console)
    if data is None:
        return 1

    display.render_weather(data, config, console=console, art_override=art_override)
    return 0


def show_logo_list(config: Dict[str, Any]) -> int:
    console = Console()
    lang = config["language"]

    title = t("logo_list_title", lang)
    console.print()
    console.print(Text(title, style=f"bold {theme.ACCENT}"))
    console.print(Text("-" * display_width(title), style=theme.TEXT_TERTIARY))
    console.print()

    names = logos.list_logo_names(config)
    builtin = logos.builtin_index()
    for name in names:
        suffix = "" if name in builtin else f"  ({t('art_logo_add', lang)})"
        console.print(Text(f"  {name}{suffix}", style=theme.TEXT))

    console.print()
    console.print(Text(t("logo_list_hint", lang), style=f"italic {theme.TEXT_TERTIARY}"))
    console.print()
    return 0


def pin_logo(config: Dict[str, Any], logo_name: str) -> int:
    console = Console()
    lang = config["language"]

    if not logos.logo_exists(logo_name, config):
        console.print()
        console.print(Text(t("logo_not_found", lang), style=f"bold {theme.ERROR}"))
        console.print(Text(t("logo_not_found_hint", lang), style=theme.TEXT_SECONDARY))
        console.print()
        return 1

    config["art"]["mode"] = "logo"
    config["art"]["logo_name"] = logo_name.lower()
    config_module.save_config(config)

    return show_weather(config)


def show_help(config: Dict[str, Any]) -> int:
    console = Console()
    lang = config["language"]
    console.print()
    console.print(Text(HELP_TEXT[lang], style=theme.TEXT))
    console.print()
    return 0


def main() -> int:
    config = config_module.load_config()
    args = [arg.lower() for arg in sys.argv[1:]]

    if args and args[0] in {"-h", "--help", "help"}:
        return show_help(config)

    if args and args[0] in SETTINGS_KEYWORDS:
        run_settings(config)
        return 0

    if args and args[0] == "--logo":
        if len(args) < 2:
            return show_help(config)
        if args[1] == "list":
            return show_logo_list(config)
        return show_weather(config, logo_name=args[1])

    if args and args[0] == "--logopin":
        if len(args) < 2:
            return show_help(config)
        return pin_logo(config, args[1])

    return show_weather(config)


if __name__ == "__main__":
    sys.exit(main())
