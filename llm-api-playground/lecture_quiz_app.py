"""
그래프는 유지하되, 노드는 자리 잡고 클릭만으로 고른다.
큰 칸·라디오도 같이 둔다. 항목 화면 하단에 줄마다 주석이 달린 코드를 붙인다.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import List

import streamlit as st
from openai import OpenAI
from pydantic import BaseModel, Field
from streamlit_agraph import Config, Edge, Node, agraph

from curriculum import LECTURES
from curriculum_code import code_for

HERE = Path(__file__).resolve().parent
for env_path in (HERE / ".env", HERE / "env"):
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if "=" in line and "key" in line.lower():
                os.environ["OPENAI_API_KEY"] = line.split("=", 1)[1].strip()

API_MODEL = "gpt-5.4-nano"


def font_white(size: int) -> dict:
    return {"color": "#ffffff", "size": size, "face": "arial", "strokeWidth": 0}


def font_ink(size: int) -> dict:
    return {"color": "#111827", "size": size, "face": "arial", "strokeWidth": 0}


def node_box(
    nid: str,
    label: str,
    bg: str,
    ink: bool,
    size: int,
    fsize: int,
    x: float,
    y: float,
) -> Node:
    return Node(
        id=nid,
        label=label,
        title=label,
        size=size,
        shape="box",
        color={
            "background": bg,
            "border": "#0f172a",
            "highlight": {"background": "#fde047", "border": "#0f172a"},
        },
        font=font_ink(fsize) if ink else font_white(fsize),
        x=x,
        y=y,
        physics=False,
        fixed=True,
        margin=16,
    )


def fan_xy(n: int, cx: float, cy: float, radius: float, start: float = -math.pi / 2) -> list[tuple[float, float]]:
    if n == 1:
        return [(cx, cy - radius)]
    pts = []
    for i in range(n):
        ang = start + (2 * math.pi * i / n)
        pts.append((cx + radius * math.cos(ang), cy + radius * math.sin(ang)))
    return pts


class Question(BaseModel):
    question: str = Field(description="문제")
    choices: List[str] = Field(description="보기 정확히 4개")
    answer: int = Field(description="정답 번호 1~4")
    explanation: str = Field(description="한두 문장 해설")


class Quiz(BaseModel):
    questions: List[Question]


def make_quiz(topic: str) -> Quiz:
    client = OpenAI()
    rq = client.chat.completions.parse(
        model=API_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "수업 복습용 객관식 퀴즈를 만든다. 보기는 4개, 정답번호는 1~4. "
                    "수업에서 배운 개념만 묻는다."
                ),
            },
            {"role": "user", "content": f"주제: {topic}\n문항 수: 3."},
        ],
        response_format=Quiz,
        max_completion_tokens=1200,
    )
    quiz = rq.choices[0].message.parsed
    if quiz is None:
        raise RuntimeError("퀴즈 파싱 실패")
    return quiz


def lecture_by_id(lid: str) -> dict:
    for lec in LECTURES:
        if lec["id"] == lid:
            return lec
    return LECTURES[0]


def tracks() -> list[str]:
    out = []
    for lec in LECTURES:
        if lec["track"] not in out:
            out.append(lec["track"])
    return out


def grouped_lectures() -> dict[str, list]:
    grouped: dict[str, list] = {}
    for lec in LECTURES:
        grouped.setdefault(lec["track"], []).append(lec)
    return grouped


def build_graph(focus: str):
    """focus 에 따라 그 층만 그린다. 자리는 고정해서 화면 밖으로 안 나간다."""
    grouped = grouped_lectures()
    nodes: list[Node] = []
    edges: list[Edge] = []

    def add(nid, label, bg, ink, size, fsize, x, y):
        nodes.append(node_box(nid, label, bg, ink, size, fsize, x, y))

    if focus.startswith("item:"):
        _, lec_id, item_id = focus.split(":", 2)
        lec = lecture_by_id(lec_id)
        item = next((x for x in lec.get("items", []) if x["id"] == item_id), None)
        add(f"lec:{lec['id']}", f"{lec['date']}  {lec['title']}", "#7c3aed", False, 34, 16, 0, -140)
        if item:
            add(f"item:{lec['id']}:{item['id']}", item["title"], "#fffbeb", True, 40, 20, 0, 120)
            edges.append(Edge(source=f"lec:{lec['id']}", target=f"item:{lec['id']}:{item['id']}"))
        return nodes, edges

    if focus.startswith("lec:"):
        lec = lecture_by_id(focus.split(":", 1)[1])
        items = lec.get("items", [])
        add(f"track:{lec['track']}", lec["track"], "#0891b2", False, 28, 16, 0, -220)
        add(f"lec:{lec['id']}", f"{lec['date']}  {lec['title']}", "#7c3aed", False, 36, 17, 0, -40)
        edges.append(Edge(source=f"track:{lec['track']}", target=f"lec:{lec['id']}"))
        span = 900
        for i, item in enumerate(items):
            x = -span / 2 + (span * i / max(len(items) - 1, 1)) if len(items) > 1 else 0
            add(f"item:{lec['id']}:{item['id']}", item["title"], "#fffbeb", True, 32, 16, x, 180)
            edges.append(Edge(source=f"lec:{lec['id']}", target=f"item:{lec['id']}:{item['id']}"))
        return nodes, edges

    if focus.startswith("track:"):
        track = focus.split(":", 1)[1]
        lecs = grouped.get(track, [])
        add("root", "수업 맵", "#4f46e5", False, 32, 18, 0, -220)
        add(f"track:{track}", track, "#0891b2", False, 38, 20, 0, -40)
        edges.append(Edge(source="root", target=f"track:{track}"))
        span = 980
        for i, lec in enumerate(lecs):
            x = -span / 2 + (span * i / max(len(lecs) - 1, 1)) if len(lecs) > 1 else 0
            add(f"lec:{lec['id']}", f"{lec['date']}  {lec['title']}", "#7c3aed", False, 32, 15, x, 180)
            edges.append(Edge(source=f"track:{track}", target=f"lec:{lec['id']}"))
        return nodes, edges

    add("root", "수업 맵", "#4f46e5", False, 42, 22, 0, 0)
    names = list(grouped)
    for (x, y), track in zip(fan_xy(len(names), 0, 0, 280), names):
        add(f"track:{track}", track, "#0891b2", False, 36, 18, x, y)
        edges.append(Edge(source="root", target=f"track:{track}"))
    return nodes, edges


def apply_click(clicked: str) -> None:
    st.session_state.focus = clicked
    if clicked == "root":
        st.session_state.item_id = None
        return
    if clicked.startswith("track:"):
        track = clicked.split(":", 1)[1]
        st.session_state.lecture_id = next(x["id"] for x in LECTURES if x["track"] == track)
        st.session_state.item_id = None
        return
    if clicked.startswith("lec:"):
        st.session_state.lecture_id = clicked.split(":", 1)[1]
        st.session_state.item_id = None
        return
    if clicked.startswith("item:"):
        _, lec_id, item_id = clicked.split(":", 2)
        st.session_state.lecture_id = lec_id
        st.session_state.item_id = item_id


def on_track_change() -> None:
    track = st.session_state.radio_track
    st.session_state.lecture_id = next(x["id"] for x in LECTURES if x["track"] == track)
    st.session_state.item_id = None
    st.session_state.focus = f"track:{track}"
    st.session_state.quiz = None


def on_lec_change() -> None:
    lec_id = st.session_state.radio_lec
    st.session_state.lecture_id = lec_id
    st.session_state.item_id = None
    st.session_state.focus = f"lec:{lec_id}"
    st.session_state.quiz = None


def on_item_change() -> None:
    item_id = st.session_state.radio_item
    st.session_state.item_id = item_id or None
    if item_id:
        st.session_state.focus = f"item:{st.session_state.lecture_id}:{item_id}"
    else:
        st.session_state.focus = f"lec:{st.session_state.lecture_id}"
    st.session_state.quiz = None


st.set_page_config(page_title="수업 그래프 · 퀴즈", layout="wide")
st.markdown(
    """
<style>
div[role="radiogroup"] label {
  display: block;
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.3rem;
  border-radius: 12px;
  background: #f3efe7;
  font-size: 1.05rem;
}
div.stButton > button { min-height: 2.8rem; }
</style>
""",
    unsafe_allow_html=True,
)
st.title("수업 그래프 · 과목 퀴즈")
st.caption("아래 큰 단추나 그래프의 청록 상자를 누르면 그 과목이 열린다. 노드가 제자리에 있다.")

if "lecture_id" not in st.session_state:
    st.session_state.lecture_id = LECTURES[0]["id"]
if "item_id" not in st.session_state:
    st.session_state.item_id = None
if "focus" not in st.session_state:
    st.session_state.focus = "root"
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "last_graph_click" not in st.session_state:
    st.session_state.last_graph_click = None

track_names = tracks()
grouped = grouped_lectures()
st.markdown(
    "**과목 "
    + str(len(track_names))
    + "개 · 수업 "
    + str(len(LECTURES))
    + "개**  —  "
    + " · ".join(track_names)
)

bar = st.columns((0.25, 0.25, 0.5))
if bar[0].button("전체 맵으로", use_container_width=True):
    st.session_state.focus = "root"
    st.session_state.item_id = None
    st.session_state.quiz = None
    st.session_state.last_graph_click = None
    st.rerun()
if bar[1].button("한 단계 위", use_container_width=True):
    focus = st.session_state.focus
    if focus.startswith("item:"):
        st.session_state.focus = f"lec:{st.session_state.lecture_id}"
        st.session_state.item_id = None
    elif focus.startswith("lec:"):
        lec = lecture_by_id(st.session_state.lecture_id)
        st.session_state.focus = f"track:{lec['track']}"
        st.session_state.item_id = None
    else:
        st.session_state.focus = "root"
        st.session_state.item_id = None
    st.session_state.quiz = None
    st.session_state.last_graph_click = None
    st.rerun()

st.markdown("#### 과목 고르기")
btn_cols = st.columns(4)
for i, name in enumerate(track_names):
    n_lec = len(grouped[name])
    if btn_cols[i % 4].button(f"{name}  ({n_lec})", key=f"btn_track_{name}", use_container_width=True):
        st.session_state.focus = f"track:{name}"
        st.session_state.lecture_id = grouped[name][0]["id"]
        st.session_state.item_id = None
        st.session_state.quiz = None
        st.session_state.last_graph_click = None
        st.rerun()

nodes, edges = build_graph(st.session_state.focus)
graph_cfg = Config(
    width=1100,
    height=560,
    directed=True,
    physics=False,
    hierarchical=False,
)
clicked = agraph(nodes=nodes, edges=edges, config=graph_cfg)
if clicked and str(clicked) != st.session_state.last_graph_click:
    st.session_state.last_graph_click = str(clicked)
    apply_click(str(clicked))
    st.session_state.quiz = None
    st.session_state.submitted = False
    st.rerun()

nav, body = st.columns((0.38, 0.62), gap="large")

with nav:
    st.subheader("큰 칸으로 고르기")
    lec_now = lecture_by_id(st.session_state.lecture_id)
    if st.session_state.get("radio_track") not in track_names:
        st.session_state.radio_track = lec_now["track"]
    if st.session_state.focus == "root":
        pass
    elif st.session_state.focus.startswith("track:"):
        st.session_state.radio_track = st.session_state.focus.split(":", 1)[1]
    else:
        st.session_state.radio_track = lec_now["track"]

    track = st.radio("줄기", track_names, key="radio_track", on_change=on_track_change)
    branch = [x for x in LECTURES if x["track"] == track]
    branch_ids = [x["id"] for x in branch]
    if st.session_state.lecture_id not in branch_ids:
        st.session_state.lecture_id = branch_ids[0]
    st.session_state.radio_lec = st.session_state.lecture_id
    lecture = next(x for x in branch if x["id"] == st.session_state.lecture_id)
    st.radio(
        "수업",
        branch_ids,
        format_func=lambda lid: next(f"{x['date']}  {x['title']}" for x in branch if x["id"] == lid),
        key="radio_lec",
        on_change=on_lec_change,
    )
    lecture = lecture_by_id(st.session_state.lecture_id)
    item_ids = [""] + [it["id"] for it in lecture.get("items", [])]
    if (st.session_state.item_id or "") not in item_ids:
        st.session_state.item_id = None
    st.session_state.radio_item = st.session_state.item_id or ""

    def item_label(iid: str) -> str:
        if not iid:
            return "수업 전체"
        return next(it["title"] for it in lecture["items"] if it["id"] == iid)

    st.radio("항목", item_ids, format_func=item_label, key="radio_item", on_change=on_item_change)
    item = next((it for it in lecture.get("items", []) if it["id"] == st.session_state.item_id), None)

with body:
    st.markdown(f"### {lecture['title']}")
    if item:
        st.markdown(f"#### {item['title']}")
    st.info(lecture["one_liner"])
    st.markdown(item["body"] if item else lecture["explain"])

    src = code_for(lecture["id"], item["id"] if item else None)
    if src:
        st.markdown("#### 이 화면을 구성하는 코드")
        st.caption(
            "한 줄마다 주석이 있다. 수업 전체를 보면 그날 항목 예제가 이어진다."
            if not item
            else "한 줄마다 주석이 있다. 코드가 이 칸의 실체다."
        )
        lang = "java" if "System.out" in src or "@Tool" in src or "chatClient" in src else "python"
        if src.lstrip().startswith("# git") or "git switch" in src or "compose.yaml" in src:
            lang = "bash"
        st.code(src, language=lang)

    st.divider()
    topic = f"{item['title']} — {lecture['quiz_topic']}" if item else lecture["quiz_topic"]
    st.markdown("### 이 칸으로 퀴즈")
    st.caption(topic)
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY 없음 — .env / env 확인")
    else:
        if st.button("퀴즈 3문제 만들기", type="primary"):
            st.session_state.submitted = False
            with st.spinner("parse 로 문항 모양을 고정하는 중..."):
                try:
                    st.session_state.quiz = make_quiz(topic)
                except Exception as e:
                    st.exception(e)
                    st.session_state.quiz = None
        quiz = st.session_state.quiz
        if quiz:
            for i, q in enumerate(quiz.questions):
                st.markdown(f"**Q{i + 1}. {q.question}**")
                labs = [f"{j + 1}) {opt}" for j, opt in enumerate(q.choices)]
                st.radio(
                    f"보기 {i + 1}",
                    options=list(range(1, len(q.choices) + 1)),
                    format_func=lambda n, labs=labs: labs[n - 1],
                    key=f"pick_{i}",
                )
            if st.button("채점"):
                st.session_state.submitted = True
            if st.session_state.submitted:
                score = 0
                for i, q in enumerate(quiz.questions):
                    pick = st.session_state.get(f"pick_{i}", 0)
                    ok = pick == q.answer
                    score += int(ok)
                    st.write(f"Q{i + 1} {'맞음' if ok else '틀림'} — 정답 {q.answer}. {q.explanation}")
                st.success(f"{score} / {len(quiz.questions)}")

st.sidebar.markdown("위에 **과목 단추 8개**가 있다. Streamlit·머신러닝·딥러닝·Spring AI 가 거기 있다.")
st.sidebar.markdown("그래프 노드는 제자리에 있다. 클릭하면 그 층만 남는다.")
st.sidebar.markdown("과제: **`parse` + Pydantic `Quiz`**")
