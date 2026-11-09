import os
import pickle

import pandas as pd
import streamlit as st
from openai import APIError

from analyze import PKL
from rag import UNKNOWN, generate, retrieve

st.set_page_config(page_title="타이타닉 데이터 복습", layout="wide")
st.title("타이타닉 데이터 복습")
st.caption("Seaborn 타이타닉 CSV에 포함된 승객 표본")

if not PKL.exists():
    st.info("먼저 터미널에서 python analyze.py를 실행해 주세요.")
    st.stop()

# 프로젝트의 analyze.py로 만든 PKL만 읽는다.
with PKL.open("rb") as file:
    data = pickle.load(file)

dashboard, fact_tab, chat = st.tabs(["대시보드", "사실표", "질문하기"])

with dashboard:
    cols = st.columns(3)
    for col, (label, value) in zip(cols, data["total"].items()):
        col.metric(label, value)
    st.caption(f"나이 결측 {data['missing_age']}명. 생존율 집계에는 포함했습니다.")

    option = st.radio("비교 기준", ["성별", "객실 등급"], horizontal=True)
    table = pd.DataFrame(data["by_sex"] if option == "성별" else data["by_class"])
    st.bar_chart(table, x="그룹", y="생존율(%)")
    st.dataframe(table, hide_index=True)

with fact_tab:
    st.dataframe(
        pd.DataFrame(data["facts"], columns=["사실 ID", "주제", "근거"]),
        hide_index=True,
    )


def show_message(role, answer, evidence):
    with st.chat_message(role):
        st.markdown(answer)
        if evidence:
            with st.expander("검색 후보 확인"):
                for fact_id, topic, body in evidence:
                    st.write(f"[{fact_id}] {topic} · {body}")


with chat:
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    st.caption("예시 질문 · 객실 등급별 생존율은 어떻게 달라?")
    if not has_key:
        st.info("검색 실습 모드입니다. OPENAI_API_KEY를 설정하면 답변 생성도 실행됩니다.")

    history = st.session_state.setdefault("history", [])
    for role, answer, evidence in history:
        show_message(role, answer, evidence)

    if question := st.chat_input("사실표에 대해 한 가지씩 질문하세요", max_chars=500):
        show_message("user", question, [])
        evidence = retrieve(question, data["facts"])
        if not evidence:
            answer = UNKNOWN
        elif not has_key:
            answer = "검색 후보를 찾았습니다. 아래에서 사실표의 해당 행을 확인하세요."
        else:
            try:
                with st.spinner("사실표를 바탕으로 답변을 만드는 중…"):
                    answer = generate(question, evidence)
            except APIError:
                answer = "답변 생성에 실패했습니다. API 키, 모델 접근 권한, 연결 상태를 확인하세요."

        show_message("assistant", answer, evidence)
        history.extend([("user", question, []), ("assistant", answer, evidence)])
