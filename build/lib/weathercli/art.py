from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.text import Text

from weathercli import logos, theme

DEFAULT_ART = [
    "                ",
    "       .        ",
    "    \\  |  /     ",
    "  '-.   .-'      ",
    " --( () )--      ",
    "   .-'   '-.     ",
    "    /  |  \\      ",
    "       '        ",
    "                ",
    "    .--.        ",
    " .-(    ).      ",
    "(___.__)__)     ",
    "                ",
]

IMAGE_WIDTH = 22
MAX_CUSTOM_ART_LINES = 30
MAX_CUSTOM_ART_LINE_LENGTH = 60


def default_art_lines() -> List[Text]:
    return [Text(line, style=theme.ACCENT) for line in DEFAULT_ART]


def custom_ascii_lines(raw_text: str) -> List[Text]:
    lines = raw_text.splitlines() or [""]
    lines = lines[:MAX_CUSTOM_ART_LINES]
    lines = [line[:MAX_CUSTOM_ART_LINE_LENGTH] for line in lines]
    return [Text(line, style=theme.ACCENT) for line in lines]


def load_image(path: str) -> "Optional[Any]":
    try:
        from PIL import Image
    except ImportError:
        return None

    image_path = Path(path).expanduser()
    if not image_path.is_file():
        return None

    try:
        image = Image.open(image_path)
        image.load()
        return image.convert("RGB")
    except Exception:
        return None


def image_to_lines(path: str, width: int = IMAGE_WIDTH) -> Optional[List[Text]]:
    image = load_image(path)
    if image is None:
        return None

    source_width, source_height = image.size
    if source_width <= 0 or source_height <= 0:
        return None

    aspect_ratio = source_height / source_width
    target_height = max(1, round(width * aspect_ratio / 2))
    resized = image.resize((width, target_height * 2))

    pixels = resized.load()
    lines: List[Text] = []
    for y in range(0, target_height * 2, 2):
        line = Text()
        for x in range(width):
            top = pixels[x, y]
            bottom = pixels[x, y + 1]
            top_hex = "#{:02x}{:02x}{:02x}".format(*top)
            bottom_hex = "#{:02x}{:02x}{:02x}".format(*bottom)
            line.append("▀", style=f"{top_hex} on {bottom_hex}")
        lines.append(line)
    return lines


def is_valid_image(path: str) -> bool:
    return load_image(path) is not None


def get_art_lines(config: Dict[str, Any]) -> List[Text]:
    art_config = config.get("art", {})
    mode = art_config.get("mode", "default")

    if mode == "custom_ascii":
        custom_text = art_config.get("custom_ascii", "")
        if custom_text.strip():
            return custom_ascii_lines(custom_text)

    if mode == "image":
        image_path = art_config.get("image_path", "")
        if image_path:
            rendered = image_to_lines(image_path)
            if rendered is not None:
                return rendered

    if mode == "logo":
        logo_name = art_config.get("logo_name", "")
        if logo_name:
            rendered = logos.load_logo_lines(logo_name, config)
            if rendered is not None:
                return rendered

    return default_art_lines()
