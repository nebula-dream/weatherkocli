from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 8

HOURLY_FIELDS = ",".join([
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation",
    "weather_code",
    "wind_speed_10m",
    "wind_direction_10m",
    "is_day",
])

DAILY_FIELDS = ",".join([
    "sunrise",
    "sunset",
    "uv_index_max",
    "temperature_2m_max",
    "temperature_2m_min",
])


class WeatherFetchError(Exception):
    pass


def _find_nearest_hour_index(times: list, tz_offset_seconds: int) -> int:
    now_utc_epoch = datetime.now(timezone.utc).timestamp()

    best_index = 0
    best_diff = float("inf")
    for index, time_str in enumerate(times):
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            continue
        local_epoch = dt.replace(tzinfo=timezone.utc).timestamp() - tz_offset_seconds
        diff = abs(local_epoch - now_utc_epoch)
        if diff < best_diff:
            best_diff = diff
            best_index = index
    return best_index


def _get_hourly_value(hourly: Dict[str, Any], key: str, index: int) -> Optional[Any]:
    values = hourly.get(key)
    if not values or index >= len(values):
        return None
    return values[index]


def fetch_current_weather(latitude: float, longitude: float, timezone: str) -> Dict[str, Any]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "hourly": HOURLY_FIELDS,
        "daily": DAILY_FIELDS,
        "wind_speed_unit": "ms",
        "past_hours": 2,
        "forecast_hours": 12,
        "cell_selection": "nearest",
    }
    try:
        response = requests.get(FORECAST_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise WeatherFetchError(str(exc)) from exc

    try:
        payload = response.json()
    except Exception as exc:
        raise WeatherFetchError("invalid JSON response") from exc

    hourly = payload.get("hourly")
    daily = payload.get("daily")
    if hourly is None or daily is None:
        raise WeatherFetchError("malformed response")

    times = hourly.get("time") or []
    tz_offset = payload.get("utc_offset_seconds", 0)
    index = _find_nearest_hour_index(times, tz_offset)
    current_time = times[index] if times else None

    return {
        "time": current_time,
        "temperature": _get_hourly_value(hourly, "temperature_2m", index),
        "apparent_temperature": _get_hourly_value(hourly, "apparent_temperature", index),
        "humidity": _get_hourly_value(hourly, "relative_humidity_2m", index),
        "precipitation": _get_hourly_value(hourly, "precipitation", index),
        "weather_code": _get_hourly_value(hourly, "weather_code", index),
        "wind_speed": _get_hourly_value(hourly, "wind_speed_10m", index),
        "wind_direction": _get_hourly_value(hourly, "wind_direction_10m", index),
        "is_day": _get_hourly_value(hourly, "is_day", index),
        "sunrise": (daily.get("sunrise") or [None])[0],
        "sunset": (daily.get("sunset") or [None])[0],
        "uv_index_max": (daily.get("uv_index_max") or [None])[0],
        "temperature_max": (daily.get("temperature_2m_max") or [None])[0],
        "temperature_min": (daily.get("temperature_2m_min") or [None])[0],
        "timezone": payload.get("timezone", timezone),
        "elevation": payload.get("elevation"),
    }
