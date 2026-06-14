import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.text import Text

from weathercli import theme

BUILTIN_LOGOS_DIR = Path(__file__).resolve().parent / "logos"

TOKEN_PATTERN = re.compile(r"\$([1-9])")


def _build_builtin_index() -> Dict[str, Path]:
    index: Dict[str, Path] = {}
    if not BUILTIN_LOGOS_DIR.is_dir():
        return index
    for file in sorted(BUILTIN_LOGOS_DIR.iterdir()):
        if file.suffix == ".txt":
            index[file.stem.lower()] = file
    return index


_builtin_index_cache: Optional[Dict[str, Path]] = None


def builtin_index() -> Dict[str, Path]:
    global _builtin_index_cache
    if _builtin_index_cache is None:
        _builtin_index_cache = _build_builtin_index()
    return _builtin_index_cache


def is_builtin(name: str) -> bool:
    return name.strip().lower() in builtin_index()


def custom_logos(config: Dict[str, Any]) -> Dict[str, str]:
    return config.get("custom_logos", {})


def list_logo_names(config: Dict[str, Any]) -> List[str]:
    names = set(builtin_index().keys())
    names.update(custom_logos(config).keys())
    return sorted(names)


def logo_exists(name: str, config: Dict[str, Any]) -> bool:
    normalized = name.strip().lower()
    if not normalized:
        return False
    return normalized in builtin_index() or normalized in custom_logos(config)


def parse_logo_line(line: str) -> Text:
    palette = theme.LOGO_PALETTE
    text = Text()
    current_color = palette[0]
    position = 0
    for match in TOKEN_PATTERN.finditer(line):
        if match.start() > position:
            text.append(line[position:match.start()], style=current_color)
        color_index = int(match.group(1)) - 1
        current_color = palette[color_index % len(palette)]
        position = match.end()
    if position < len(line):
        text.append(line[position:], style=current_color)
    return text


def load_logo_lines(name: str, config: Dict[str, Any]) -> Optional[List[Text]]:
    normalized = name.strip().lower()
    if not normalized:
        return None

    custom = custom_logos(config)
    if normalized in custom:
        content = custom[normalized]
        return [parse_logo_line(line) for line in content.splitlines()]

    path = builtin_index().get(normalized)
    if path is None:
        return None
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return [parse_logo_line(line) for line in content.splitlines()]
