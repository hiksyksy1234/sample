# app.py
import streamlit as st
import json
import os

from rag_pilates import get_answer

st.set_page_config(
    page_title="필라테스 Q&A 챗봇",
    page_icon="🧘‍♀️",
    layout="centered"
)

SAVE_FILE = "conversation.json"

# -----------------------------------------------------
# 🔹 대화 내용 저장 함수
# -----------------------------------------------------
def save_conversation(messages):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

# -----------------------------------------------------
# 🔹 대화 내용 불러오기 함수
# -----------------------------------------------------
def load_conversation():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# -----------------------------------------------------
# 🔹 세션 상태 초기화 + 파일에서 불러오기
# -----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = load_conversation()


# -----------------------------------------------------
# UI 헤더
# -----------------------------------------------------
st.markdown("<h1 style='text-align: center;'>🧘 필라테스 Q&A 챗봇</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>필라테스 관련 궁금한 내용을 질문해보세요!</p>", unsafe_allow_html=True)
st.write("---")

# -----------------------------------------------------
# 질문 입력
# -----------------------------------------------------
st.subheader("질문 입력")

with st.form("question_form", clear_on_submit=True):
    query = st.text_input("질문을 입력하세요:", placeholder="예: 10월 3일은 수업이 있나요?")
    submitted = st.form_submit_button("질문하기")

# -----------------------------------------------------
# RAG 호출
# -----------------------------------------------------
if submitted and query:
    st.session_state.messages.append({"role": "user", "content": query})
    answer = get_answer(query)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # 🔥 대화 저장
    save_conversation(st.session_state.messages)


# -----------------------------------------------------
# 대화 출력 (챗봇 왼쪽, 사용자 오른쪽)
# -----------------------------------------------------
st.subheader("📒 대화 기록")

for msg in st.session_state.messages:

    # 챗봇 메시지(left)
    if msg["role"] == "assistant":
        st.markdown(
            f"""
            <div style='display:flex; justify-content:flex-start; margin-bottom:10px;'>
                <div style='background-color:#FFF0E6; color:black; padding:12px 16px;
                            border-radius:12px; max-width:70%;'>
                    <b>🤖 챗봇</b><br>{msg["content"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 사용자 메시지(right)
    else:
        st.markdown(
            f"""
            <div style='display:flex; justify-content:flex-end; margin-bottom:10px;'>
                <div style='background-color:#E8F4FF; color:black; padding:12px 16px;
                            border-radius:12px; max-width:70%; text-align:right;'>
                    <b>🙋 사용자</b><br>{msg["content"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


st.write("---")

# -----------------------------------------------------
# 🔹 대화 초기화 버튼 (파일도 삭제)
# -----------------------------------------------------
if st.button("대화 초기화 🗑"):
    st.session_state.messages = []

    # 파일 삭제
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

    st.rerun()
