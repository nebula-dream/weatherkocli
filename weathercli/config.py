import json
import os
from pathlib import Path
from typing import Any, Dict

CONFIG_DIR = Path(os.environ.get("WEATHERCLI_CONFIG_DIR", str(Path.home() / ".config" / "weathercli")))
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "location": {
        "name_ko": "서울특별시",
        "name_en": "Seoul",
        "admin_ko": "대한민국",
        "admin_en": "South Korea",
        "latitude": 37.5665,
        "longitude": 126.9780,
        "timezone": "Asia/Seoul",
    },
    "unit": "celsius",
    "language": "ko",
    "header_text": "weather@cli",
    "art": {
        "mode": "default",
        "custom_ascii": "",
        "image_path": "",
        "logo_name": "",
    },
    "display": {
        "condition": True,
        "feels_like": True,
        "humidity": True,
        "wind": True,
        "precipitation": True,
        "sun": True,
        "uv": False,
    },
    "calibration": {
        "temperature_offset": 0.0,
    },
    "custom_logos": {},
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as handle:
            stored = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return json.loads(json.dumps(DEFAULT_CONFIG))
    return _deep_merge(DEFAULT_CONFIG, stored)


def save_config(config: Dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2)
