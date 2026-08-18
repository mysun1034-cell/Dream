# 장원 강사 — 터미널 멀티턴 챗봇
# 강사님 원문의 system 키 오타(cotent)는 content 로 고쳐 둠.

from openai import OpenAI

client = OpenAI()
API_MODEL = "gpt-5.4-nano"

messages = [
    {"role": "system", "content": "너는 친절한 대화 봇이야. 3문장 이내로만 답해"},
]
total_tokens = 0
print("AI와 대화해요. 나가시려면 exit 입력해주세요.")
while True:
    user_input = input("\nuser > ")
    if user_input == "exit":
        break
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=API_MODEL,
        messages=messages,
        max_completion_tokens=300,
    )
    answer = response.choices[0].message.content
    messages.append({"role": "assistant", "content": answer})
    total_tokens += response.usage.total_tokens
    print(f"\nAI > {answer}  ({response.usage.total_tokens}/{total_tokens})")
