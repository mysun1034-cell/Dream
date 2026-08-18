# 장원 강사 — 도구 두 개 (날씨 + 계산)
# 함수는 내가 실행한다. tools 는 모델에게 주는 사용법(오전의 JSON 스키마).

import json
import re
import urllib.request

from openai import OpenAI

client = OpenAI()
API_MODEL = "gpt-5.4-nano"


def get_weather(city: str, latitude: float, longitude: float) -> str:
    """그 좌표의 지금 날씨를 open-meteo 에서 가져온다 (키 불필요)"""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&timezone=auto"
    )
    with urllib.request.urlopen(url, timeout=10) as resp:
        c = json.load(resp)["current"]
    return (
        f"{city} 기온 {c['temperature_2m']}도, 습도 {c['relative_humidity_2m']}%, "
        f"강수 {c['precipitation']}mm, 바람 {c['wind_speed_10m']}m/s"
    )


def calc(expression: str) -> str:
    """수식 문자열을 계산한다. 모델이 준 문자열이므로 허용 문자만 통과시킨다."""
    if not re.fullmatch(r"[0-9+\-*/(). %]+", expression) or "**" in expression or len(expression) > 80:
        return "허용되지 않는 수식이라 계산을 거부했다"
    return str(eval(expression, {"__builtins__": {}}, {}))


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "그 도시의 지금 날씨를 알려 준다. 위도·경도는 네가 아는 값을 채워라.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "도시 이름"},
                    "latitude": {"type": "number", "description": "그 도시의 위도"},
                    "longitude": {"type": "number", "description": "그 도시의 경도"},
                },
                "required": ["city", "latitude", "longitude"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc",
            "description": "수식을 정확하게 계산한다. 예: 739521468 * 8462137",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "계산할 수식"}},
                "required": ["expression"],
            },
        },
    },
]
print("함수 준비 완료 — 아직 아무도 부르지 않았다")
