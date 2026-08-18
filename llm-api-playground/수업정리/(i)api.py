# 장원 강사 — messages 배열 수업
# 1) 첫 호출  2) system 페르소나  3) 멀티턴이면 보낸 토큰이 커진다
# 노트북에서 client / API_MODEL 이 있는 전제로 보여 준 셀들.

from openai import OpenAI

client = OpenAI()
API_MODEL = "gpt-5.4-nano"

# ── 1. 첫 호출 (gpt-5-nano 예시) ────────────────────────────────
response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {"role": "user", "content": "환절기에 감기 조심해야 하는 이유 알려줘"},
    ],
    max_completion_tokens=300,
)
print(response.choices[0].message.content)

# ── 2. 페르소나 — 지시(system)가 배열 맨 앞에 탄다 ───────────────
question = "환절기에 감기 조심해야 하는 이유 알려줘"
personas = {
    "초등 선생님": "너는 초등학생에게 설명하는 선생님이야. 쉬운 말로 짧게.",
    "논문 저자  ": "너는 의학 논문 저자야. 전문용어로 간결하게, 다섯 문장 이내로.",
    "조선시대 어의": "너는 조선시대 임금님 주치의(어의)야. 사극 말투로 정중하게, 다섯 문장 이내로.",
}
for name, sys_msg in personas.items():
    r = client.chat.completions.create(
        model=API_MODEL,
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": question},
        ],
        max_completion_tokens=400,
    )
    print(f"\n[{name}]")
    print(r.choices[0].message.content)

# ── 3. 멀티턴 — 앞 대화 전체가 매번 다시 실려 간다 ───────────────
messages = [{"role": "system", "content": "너는 친절한 상담사야. 두 문장 이내로 답해."}]
questions = [
    "주말에 뭐 하면 좋을까?",
    "비가 오면?",
    "실내에서 몸을 움직이고 싶으면?",
    "돈이 안 들면 더 좋겠어.",
    "지금까지 추천한 것 중 딱 하나만 골라 줘.",
]

print(f"{'턴':>2} | {'배열 칸수':>4} | {'보낸 토큰':>5} | {'받은 토큰':>5} | 누적 합계")
print("-" * 48)
total = 0
for i, q in enumerate(questions, 1):
    messages.append({"role": "user", "content": q})
    r = client.chat.completions.create(model=API_MODEL, messages=messages, max_completion_tokens=300)
    answer = r.choices[0].message.content
    messages.append({"role": "assistant", "content": answer})
    total += r.usage.total_tokens
    print(f"{i:>2} | {len(messages):>6} | {r.usage.prompt_tokens:>7} | {r.usage.completion_tokens:>7} | {total:>6}")

# 보낸 토큰이 매 턴 커진다 — 답은 두 문장씩인데 보내는 쪽이 자꾸 무거워진다.
# API 요금은 이 토큰 수로 매겨진다.
