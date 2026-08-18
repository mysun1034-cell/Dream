# 장원 강사 — 금요일 Streamlit 챗봇 (최종본)
# 2:29 버전은 이번 턴만 그림. 2:33 에서 세션을 다시 그리게 고친 것.

import streamlit as st
from openai import OpenAI

st.title("AI 챗봇")

client = OpenAI()
API_MODEL = "gpt-5.4-nano"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "시스템 프롬프트"}]

# 재실행될 때마다 지금까지의 대화를 다시 그린다 (system 은 말풍선에서 제외)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

prompt = st.chat_input("물어보세요")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = client.chat.completions.create(
        model=API_MODEL,
        messages=st.session_state.messages,
        max_completion_tokens=400,
    )
    answer = response.choices[0].message.content
    st.chat_message("assistant").write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
