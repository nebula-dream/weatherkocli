from typing import Any, Dict, List, Optional

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
REQUEST_TIMEOUT = 6

KOREA_QUICK_REGIONS: List[Dict[str, Any]] = [
    {"name_ko": "서울특별시", "name_en": "Seoul", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 37.5665, "longitude": 126.9780, "timezone": "Asia/Seoul"},
    {"name_ko": "부산광역시", "name_en": "Busan", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 35.1796, "longitude": 129.0756, "timezone": "Asia/Seoul"},
    {"name_ko": "대구광역시", "name_en": "Daegu", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 35.8714, "longitude": 128.6014, "timezone": "Asia/Seoul"},
    {"name_ko": "인천광역시", "name_en": "Incheon", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 37.4563, "longitude": 126.7052, "timezone": "Asia/Seoul"},
    {"name_ko": "광주광역시", "name_en": "Gwangju", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 35.1595, "longitude": 126.8526, "timezone": "Asia/Seoul"},
    {"name_ko": "대전광역시", "name_en": "Daejeon", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 36.3504, "longitude": 127.3845, "timezone": "Asia/Seoul"},
    {"name_ko": "울산광역시", "name_en": "Ulsan", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 35.5384, "longitude": 129.3114, "timezone": "Asia/Seoul"},
    {"name_ko": "세종특별자치시", "name_en": "Sejong", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 36.4801, "longitude": 127.2890, "timezone": "Asia/Seoul"},
    {"name_ko": "경기도 수원시", "name_en": "Suwon, Gyeonggi", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 37.2636, "longitude": 127.0286, "timezone": "Asia/Seoul"},
    {"name_ko": "강원특별자치도 춘천시", "name_en": "Chuncheon, Gangwon", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 37.8813, "longitude": 127.7298, "timezone": "Asia/Seoul"},
    {"name_ko": "충청북도 청주시", "name_en": "Cheongju, Chungbuk", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 36.6424, "longitude": 127.4890, "timezone": "Asia/Seoul"},
    {"name_ko": "충청남도 홍성군", "name_en": "Hongseong, Chungnam", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 36.6010, "longitude": 126.6608, "timezone": "Asia/Seoul"},
    {"name_ko": "전북특별자치도 전주시", "name_en": "Jeonju, Jeonbuk", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 35.8242, "longitude": 127.1480, "timezone": "Asia/Seoul"},
    {"name_ko": "전라남도 무안군", "name_en": "Muan, Jeonnam", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 34.9903, "longitude": 126.4816, "timezone": "Asia/Seoul"},
    {"name_ko": "경상북도 안동시", "name_en": "Andong, Gyeongbuk", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 36.5684, "longitude": 128.7294, "timezone": "Asia/Seoul"},
    {"name_ko": "경상남도 창원시", "name_en": "Changwon, Gyeongnam", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 35.2280, "longitude": 128.6811, "timezone": "Asia/Seoul"},
    {"name_ko": "제주특별자치도 제주시", "name_en": "Jeju City, Jeju", "admin_ko": "대한민국", "admin_en": "South Korea",
     "latitude": 33.4996, "longitude": 126.5312, "timezone": "Asia/Seoul"},
]


def quick_regions() -> List[Dict[str, Any]]:
    return KOREA_QUICK_REGIONS


def _build_admin_label(item: Dict[str, Any]) -> Optional[str]:
    parts = []
    for key in ("admin1", "admin2"):
        value = item.get(key)
        if value:
            parts.append(value)
    country = item.get("country")
    if country:
        parts.append(country)
    if not parts:
        return None
    return ", ".join(parts)


def search_locations(query: str, language: str, limit: int = 10) -> List[Dict[str, Any]]:
    params = {
        "name": query,
        "count": limit,
        "language": "ko" if language == "ko" else "en",
        "format": "json",
    }
    response = requests.get(GEOCODING_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    results = payload.get("results") or []

    normalized: List[Dict[str, Any]] = []
    for item in results:
        name = item.get("name")
        latitude = item.get("latitude")
        longitude = item.get("longitude")
        timezone = item.get("timezone")
        if name is None or latitude is None or longitude is None or timezone is None:
            continue
        normalized.append({
            "name": name,
            "admin_label": _build_admin_label(item),
            "country_code": item.get("country_code"),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
        })
    return normalized
