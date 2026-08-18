import os
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent
for env_path in (HERE / ".env", HERE / "env"):
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if "=" in line and "key" in line.lower():
                os.environ["OPENAI_API_KEY"] = line.split("=", 1)[1].strip()

API_MODEL = "gpt-5.4-nano"
client = OpenAI()


class Question(BaseModel):
    question: str = Field(description="문제")
    choices: list[str] = Field(description="보기 4개")
    answer: int = Field(description="정답 번호 1~4")


class Quiz(BaseModel):
    questions: list[Question]


topic = input("퀴즈 주제를 정해주세요. > ").strip()
print(f"\n{topic}과 관련된 주제를 만드는 중입니다...")

rq = client.chat.completions.parse(
    model=API_MODEL,
    messages=[
        {"role": "system", "content": "객관식 퀴즈를 만든다. 보기는 4개, 정답번호는 1~4."},
        {"role": "user", "content": f"{topic} 관련 객관식 3문제를 JSON으로 만들어라."},
    ],
    response_format=Quiz,
)
quiz = rq.choices[0].message.parsed

score = 0

for i, q in enumerate(quiz.questions, 1):
    print(f"\nQ{i}. {q.question}")
    for j, opt in enumerate(q.choices, 1):
        print(f"    {j} {opt}")

    try:
        pick = int(input("답을 입력해주세요 (1,2,3,4) > "))
    except ValueError:
        pick = 0

    if pick == q.answer:
        score += 1
        print("축하합니다. 정답을 맞추셨습니다.")
    else:
        print(f"아깝습니다. 정답은 {q.answer}입니다.")

print(f"\n점수: {score}/{len(quiz.questions)}")
