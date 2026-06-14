import re
from typing import Any, Dict, List, Tuple, Union

import questionary
from questionary import Separator, Style
from rich.console import Console
from rich.text import Text

from weathercli import art, config as config_module
from weathercli import geocoding, logos, theme
from weathercli.display import location_label
from weathercli.i18n import t
from weathercli.textwidth import display_width

QUESTIONARY_STYLE = Style(list(theme.QUESTIONARY_STYLE_MAP.items()))

UNIT_LABEL_KEYS = {
    "celsius": "unit_celsius",
    "fahrenheit": "unit_fahrenheit",
    "both": "unit_both",
}

LANGUAGE_LABEL_KEYS = {
    "ko": "language_ko",
    "en": "language_en",
}

DISPLAY_ITEMS = [
    ("condition", "item_condition"),
    ("feels_like", "item_feels_like"),
    ("humidity", "item_humidity"),
    ("wind", "item_wind"),
    ("precipitation", "item_precipitation"),
    ("sun", "item_sun"),
    ("uv", "item_uv"),
]

LOGO_NAME_PATTERN = re.compile(r"^[a-z0-9_-]{1,32}$")


def menu_title(label: str, current_label: str, value: str) -> List[Tuple[str, str]]:
    return [
        ("", f"{label}   ("),
        ("class:text", f"{current_label}: "),
        ("class:current-value", value),
        ("", ")"),
    ]


def print_message(console: Console, message: str, color: str) -> None:
    console.print()
    console.print(Text(message, style=f"bold {color}"))


def print_success(console: Console, message: str) -> None:
    print_message(console, message, theme.SUCCESS)


def print_warning(console: Console, message: str) -> None:
    print_message(console, message, theme.WARNING)


def print_error(console: Console, title: str, body: str) -> None:
    console.print()
    console.print(Text(title, style=f"bold {theme.ERROR}"))
    console.print(Text(body, style=theme.TEXT_SECONDARY))


def handle_location(config: Dict[str, Any], console: Console) -> None:
    lang = config["language"]

    method = questionary.select(
        t("location_method_title", lang),
        choices=[
            questionary.Choice(t("location_method_quick", lang), value="quick"),
            questionary.Choice(t("location_method_search", lang), value="search"),
            questionary.Choice(t("location_method_back", lang), value="back"),
        ],
        style=QUESTIONARY_STYLE,
    ).ask()

    if method in (None, "back"):
        return

    if method == "quick":
        regions = geocoding.quick_regions()
        choices = [
            questionary.Choice(
                title=region["name_ko"] if lang == "ko" else region["name_en"],
                value=index,
            )
            for index, region in enumerate(regions)
        ]
        selected_index = questionary.select(
            t("location_quick_title", lang), choices=choices, style=QUESTIONARY_STYLE
        ).ask()
        if selected_index is None:
            return
        region = regions[selected_index]
        config["location"] = {
            "name_ko": region["name_ko"],
            "name_en": region["name_en"],
            "admin_ko": region["admin_ko"],
            "admin_en": region["admin_en"],
            "latitude": region["latitude"],
            "longitude": region["longitude"],
            "timezone": region["timezone"],
        }
        config_module.save_config(config)
        print_success(console, t("location_saved", lang))
        return

    query = questionary.text(
        t("location_search_prompt", lang), style=QUESTIONARY_STYLE
    ).ask()

    if query is None:
        return
    query = query.strip()
    if not query:
        print_warning(console, t("location_search_empty", lang))
        return

    results = []
    with console.status(f"{t('location_search_searching', lang)}...", spinner="dots"):
        try:
            results = geocoding.search_locations(query, lang)
        except Exception:
            results = None

    if results is None:
        print_error(console, t("error_network_title", lang), t("error_network_body", lang))
        return

    if not results:
        print_warning(console, t("location_search_no_results", lang))
        return

    choices = []
    for result in results:
        title = result["name"]
        if result["admin_label"]:
            title = f"{title}  ·  {result['admin_label']}"
        choices.append(questionary.Choice(title=title, value=result))

    selected = questionary.select(
        t("location_search_pick", lang), choices=choices, style=QUESTIONARY_STYLE
    ).ask()
    if selected is None:
        return

    admin_label = selected["admin_label"] or ("대한민국" if selected["country_code"] == "KR" else "")
    config["location"] = {
        "name_ko": selected["name"],
        "name_en": selected["name"],
        "admin_ko": admin_label,
        "admin_en": admin_label,
        "latitude": selected["latitude"],
        "longitude": selected["longitude"],
        "timezone": selected["timezone"],
    }
    config_module.save_config(config)
    print_success(console, t("location_saved", lang))


def handle_unit(config: Dict[str, Any], console: Console) -> None:
    lang = config["language"]
    choices = [
        questionary.Choice(t("unit_celsius", lang), value="celsius"),
        questionary.Choice(t("unit_fahrenheit", lang), value="fahrenheit"),
        questionary.Choice(t("unit_both", lang), value="both"),
    ]
    selected = questionary.select(
        t("unit_title", lang),
        choices=choices,
        default=next((c for c in choices if c.value == config["unit"]), choices[0]),
        style=QUESTIONARY_STYLE,
    ).ask()
    if selected is None:
        return
    config["unit"] = selected
    config_module.save_config(config)
    print_success(console, t("unit_saved", lang))


def handle_display(config: Dict[str, Any], console: Console) -> None:
    lang = config["language"]
    display_config = config["display"]
    choices = [
        questionary.Choice(
            title=t(label_key, lang),
            value=key,
            checked=bool(display_config.get(key, True)),
        )
        for key, label_key in DISPLAY_ITEMS
    ]
    selected = questionary.checkbox(
        t("display_title", lang), choices=choices, style=QUESTIONARY_STYLE
    ).ask()
    if selected is None:
        return
    if not selected:
        print_warning(console, t("display_min_warning", lang))
        return
    for key, _ in DISPLAY_ITEMS:
        display_config[key] = key in selected
    config_module.save_config(config)
    print_success(console, t("display_saved", lang))


def handle_language(config: Dict[str, Any], console: Console) -> None:
    lang = config["language"]
    choices = [
        questionary.Choice(t("language_ko", lang), value="ko"),
        questionary.Choice(t("language_en", lang), value="en"),
    ]
    selected = questionary.select(
        t("language_title", lang),
        choices=choices,
        default=next((c for c in choices if c.value == lang), choices[0]),
        style=QUESTIONARY_STYLE,
    ).ask()
    if selected is None:
        return
    config["language"] = selected
    config_module.save_config(config)
    print_success(console, t("language_saved", selected))


def handle_header(config: Dict[str, Any], console: Console) -> None:
    lang = config["language"]
    current = config.get("header_text") or "weather@cli"

    answer = questionary.text(
        t("header_prompt", lang), default=current, style=QUESTIONARY_STYLE
    ).ask()
    if answer is None:
        return

    answer = answer.strip()
    config["header_text"] = answer if answer else "weather@cli"
    config_module.save_config(config)
    print_success(console, t("header_saved", lang))


def handle_art(config: Dict[str, Any], console: Console) -> None:
    lang = config["language"]

    choice = questionary.select(
        t("art_title", lang),
        choices=[
            questionary.Choice(t("art_default", lang), value="default"),
            questionary.Choice(t("art_custom", lang), value="custom_ascii"),
            questionary.Choice(t("art_image", lang), value="image"),
            questionary.Choice(t("art_logo", lang), value="logo"),
            questionary.Choice(t("art_logo_add", lang), value="logo_add"),
            questionary.Choice(t("art_logo_remove", lang), value="logo_remove"),
            questionary.Choice(t("location_method_back", lang), value="back"),
        ],
        style=QUESTIONARY_STYLE,
    ).ask()

    if choice in (None, "back"):
        return

    if choice == "default":
        config["art"]["mode"] = "default"
        config_module.save_config(config)
        print_success(console, t("art_saved", lang))
        return

    if choice == "custom_ascii":
        text_value = questionary.text(
            t("art_custom_prompt", lang),
            multiline=True,
            style=QUESTIONARY_STYLE,
        ).ask()
        if text_value is None:
            return
        if not text_value.strip():
            print_warning(console, t("art_custom_empty", lang))
            return
        config["art"]["mode"] = "custom_ascii"
        config["art"]["custom_ascii"] = text_value
        config_module.save_config(config)
        print_success(console, t("art_saved", lang))
        return

    if choice == "image":
        path_value = questionary.text(
            t("art_image_prompt", lang), style=QUESTIONARY_STYLE
        ).ask()
        if path_value is None:
            return
        path_value = path_value.strip()
        if not path_value or not art.is_valid_image(path_value):
            print_warning(console, t("art_image_error", lang))
            return
        config["art"]["mode"] = "image"
        config["art"]["image_path"] = path_value
        config_module.save_config(config)
        print_success(console, t("art_saved", lang))
        return

    if choice == "logo":
        logo_name = questionary.autocomplete(
            t("logo_search_prompt", lang),
            choices=logos.list_logo_names(config),
            style=QUESTIONARY_STYLE,
        ).ask()
        if logo_name is None:
            return
        logo_name = logo_name.strip()
        if not logo_name or not logos.logo_exists(logo_name, config):
            print_warning(console, t("logo_not_found", lang))
            return
        config["art"]["mode"] = "logo"
        config["art"]["logo_name"] = logo_name.lower()
        config_module.save_config(config)
        print_success(console, t("art_saved", lang))
        return

    if choice == "logo_add":
        name_value = questionary.text(
            t("logo_name_prompt", lang), style=QUESTIONARY_STYLE
        ).ask()
        if name_value is None:
            return
        name_value = name_value.strip().lower()
        if not LOGO_NAME_PATTERN.match(name_value):
            print_warning(console, t("logo_name_invalid", lang))
            return
        if logos.logo_exists(name_value, config):
            print_warning(console, t("logo_name_exists", lang))
            return

        art_text = questionary.text(
            t("logo_art_prompt", lang), multiline=True, style=QUESTIONARY_STYLE
        ).ask()
        if art_text is None:
            return
        if not art_text.strip():
            print_warning(console, t("art_custom_empty", lang))
            return

        config.setdefault("custom_logos", {})[name_value] = art_text
        config_module.save_config(config)
        print_success(console, t("logo_added", lang))
        return

    if choice == "logo_remove":
        custom = config.get("custom_logos", {})
        if not custom:
            print_warning(console, t("logo_remove_empty", lang))
            return

        target = questionary.select(
            t("logo_remove_title", lang),
            choices=[questionary.Choice(name, value=name) for name in sorted(custom.keys())],
            style=QUESTIONARY_STYLE,
        ).ask()
        if target is None:
            return

        del config["custom_logos"][target]
        if config["art"].get("mode") == "logo" and config["art"].get("logo_name") == target:
            config["art"]["mode"] = "default"
            config["art"]["logo_name"] = ""
        config_module.save_config(config)
        print_success(console, t("logo_removed", lang))


def format_offset(value: float) -> str:
    if value == 0:
        return "0"
    text = f"{value:+.1f}".rstrip("0").rstrip(".")
    return text if text not in ("+", "-") else f"{value:+.0f}"


def handle_calibration(config: Dict[str, Any], console: Console) -> None:
    lang = config["language"]
    current = config.get("calibration", {}).get("temperature_offset", 0.0)

    answer = questionary.text(
        t("calibration_prompt", lang),
        default=format_offset(current),
        style=QUESTIONARY_STYLE,
    ).ask()
    if answer is None:
        return

    answer = answer.strip().replace(",", ".")
    if not answer:
        value = 0.0
    else:
        try:
            value = float(answer)
        except ValueError:
            print_warning(console, t("calibration_invalid", lang))
            return

    value = max(-10.0, min(10.0, value))
    config.setdefault("calibration", {})["temperature_offset"] = value
    config_module.save_config(config)
    print_success(console, t("calibration_saved", lang))


def run_settings(config: Dict[str, Any]) -> None:
    console = Console()

    while True:
        lang = config["language"]
        location_name, _ = location_label(config)
        unit_label = t(UNIT_LABEL_KEYS[config["unit"]], lang)
        language_label = t(LANGUAGE_LABEL_KEYS[lang], lang)
        header_value = config.get("header_text") or "weather@cli"
        offset = config.get("calibration", {}).get("temperature_offset", 0.0)
        offset_label = f"{format_offset(offset)}°C"
        current = t("current_label", lang)

        title = t("settings_title", lang)
        console.print()
        console.print(Text(title, style=f"bold {theme.ACCENT}"))
        console.print(Text("-" * display_width(title), style=theme.TEXT_TERTIARY))
        console.print(Text(t("settings_subtitle", lang), style=theme.TEXT_SECONDARY))

        choices: List[Union[questionary.Choice, Separator]] = [
            Separator(f"  {t('settings_section_basic', lang)}"),
            questionary.Choice(
                title=menu_title(t("menu_location", lang), current, location_name),
                value="location",
            ),
            questionary.Choice(
                title=menu_title(t("menu_unit", lang), current, unit_label),
                value="unit",
            ),
            questionary.Choice(title=t("menu_display", lang), value="display"),
            questionary.Choice(
                title=menu_title(t("menu_language", lang), current, language_label),
                value="language",
            ),
            Separator(f"  {t('settings_section_appearance', lang)}"),
            questionary.Choice(
                title=menu_title(t("menu_header", lang), current, header_value),
                value="header",
            ),
            questionary.Choice(title=t("menu_art", lang), value="art"),
            Separator(f"  {t('settings_section_data', lang)}"),
            questionary.Choice(
                title=menu_title(t("menu_calibration", lang), current, offset_label),
                value="calibration",
            ),
            Separator(),
            questionary.Choice(title=t("menu_done", lang), value="done"),
        ]

        choice = questionary.select(
            "", choices=choices, style=QUESTIONARY_STYLE
        ).ask()

        if choice is None:
            console.print()
            console.print(Text(t("keyboard_cancelled", lang), style=theme.TEXT_SECONDARY))
            return

        if choice == "done":
            console.print()
            console.print(Text(t("goodbye", lang), style=theme.TEXT_SECONDARY))
            console.print()
            return

        if choice == "location":
            handle_location(config, console)
        elif choice == "unit":
            handle_unit(config, console)
        elif choice == "display":
            handle_display(config, console)
        elif choice == "language":
            handle_language(config, console)
        elif choice == "header":
            handle_header(config, console)
        elif choice == "art":
            handle_art(config, console)
        elif choice == "calibration":
            handle_calibration(config, console)
