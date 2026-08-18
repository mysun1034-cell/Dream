"""
터미널에서 도는 도구 호출 챗봇.
- 모델은 함수를 실행하지 않는다 — "이 함수를 이 인자로 불러줘"라는 요청(tool_calls)만 돌려준다.
- 실제 실행은 이 파이썬 코드가 한다.
- 실행 결과를 role:"tool" 메시지로, tool_call_id로 원래 요청과 짝지어 다시 모델에 보낸다(왕복).
"""

import json
import os
from pathlib import Path

import requests
from openai import OpenAI

# playground 로 옮긴 뒤에도 키가 잡히게 (.env / env 직접 읽음)
_root = Path(__file__).resolve().parent.parent
for env_path in (_root / ".env", _root / "env"):
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if "=" in line and "key" in line.lower():
                os.environ["OPENAI_API_KEY"] = line.split("=", 1)[1].strip()

client = OpenAI()
API_MODEL = "gpt-5.4-nano"

# ── 실제로 실행되는 함수들 ──────────────────────────────────────

def get_weather(city: str) -> dict:
    """open-meteo: 키 없이 쓰는 지오코딩 + 날씨 API."""
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "ko"},
        timeout=10,
    ).json()

    results = geo.get("results")
    if not results:
        return {"error": f"'{city}' 위치를 찾을 수 없음"}

    lat, lon = results[0]["latitude"], results[0]["longitude"]
    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": lat, "longitude": lon, "current_weather": True},
        timeout=10,
    ).json()

    current = weather.get("current_weather", {})
    return {
        "city": city,
        "temperature_c": current.get("temperature"),
        "windspeed_kmh": current.get("windspeed"),
    }


def calculate(expression: str) -> dict:
    """+ - * / ( ) 와 숫자만 허용하는 안전한 계산기."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return {"error": "허용되지 않은 문자가 포함됨"}
    try:
        return {"expression": expression, "result": eval(expression)}
    except Exception as e:
        return {"error": str(e)}


FUNCTIONS = {"get_weather": get_weather, "calculate": calculate}

# ── 모델에게 알려주는 도구 사용법(스키마) ──────────────────────

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "특정 도시의 현재 실시간 날씨(기온, 풍속)를 가져온다. 날씨를 묻는 질문에 사용.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "도시 이름, 예: 서울, 부산"},
                },
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "사칙연산 수식을 계산한다. 숫자 계산 질문에 사용.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "예: (3+5)*2"},
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    },
]

# ── 왕복 루프 ────────────────────────────────────────────────

MAX_ROUNDS = 5


def chat(messages: list) -> str:
    for _ in range(MAX_ROUNDS):
        r = client.chat.completions.create(
            model=API_MODEL,
            messages=messages,
            tools=tools,
        )
        msg = r.choices[0].message

        if r.choices[0].finish_reason != "tool_calls":
            return msg.content or "(빈 응답)"

        # 모델의 요청서 자체도 대화 기록에 넣어야 다음 턴에서 맥락이 이어진다.
        messages.append(msg)

        for call in msg.tool_calls:
            fn_name = call.function.name
            args = json.loads(call.function.arguments)
            fn = FUNCTIONS.get(fn_name)
            result = fn(**args) if fn else {"error": f"알 수 없는 함수: {fn_name}"}

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    return "(도구 호출 상한 도달 — 응답을 완성하지 못함)"


def main():
    print("도구 챗봇 — 날씨나 계산을 물어보세요. (종료: exit)")
    messages = [
        {"role": "system", "content": "필요할 때 get_weather, calculate 도구를 사용해 정확히 답하라."},
    ]
    while True:
        user_input = input("\n나: ").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})
        answer = chat(messages)
        print(f"봇: {answer}")
        messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
