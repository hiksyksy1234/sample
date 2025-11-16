# rag_pilates.py
from datetime import datetime, date
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
#from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool

import re
import pytz
load_dotenv()

# -----------------------------------------------------
# 🔹 한국 공휴일 계산 (holidays 패키지 없이)
# -----------------------------------------------------

def korean_holidays(year: int):
    """해당 연도의 한국 공휴일을 date 객체 목록으로 반환"""
    holidays = []

    # 고정 공휴일
    fixed = [
        (1, 1), (3, 1), (5, 5), (6, 6),
        (8, 15), (10, 3), (10, 9), (12, 25)
    ]
    for m, d in fixed:
        holidays.append(date(year, m, d))

    # 설·추석 간단 매핑 (실제 음력 반영 아님 — 테스트 목적)
    lunar_based = {
        "seollal": [(2, 9), (2, 10), (2, 11)],
        "chuseok": [(9, 16), (9, 17), (9, 18)],
    }
    for m, d in lunar_based["seollal"]:
        holidays.append(date(year, m, d))
    for m, d in lunar_based["chuseok"]:
        holidays.append(date(year, m, d))

    return holidays


def is_holiday_korea(check_date: date) -> bool:
    """주어진 날짜 한국 공휴일 여부"""
    return check_date in korean_holidays(check_date.year)


# -----------------------------------------------------
# 🔹 Tool 1: 현재 한국시간
# -----------------------------------------------------
@tool
def get_kst_datetime() -> str:
    """현재 한국시간(YYYY-MM-DD HH:MM:SS)"""
    kst = datetime.now(pytz.timezone("Asia/Seoul"))
    return kst.strftime("%Y-%m-%d %H:%M:%S")


# -----------------------------------------------------
# 🔹 Tool 2: 특정 날짜 공휴일 여부
# -----------------------------------------------------
@tool
def check_holiday(date_str: str) -> str:
    """주어진 날짜가 한국 공휴일이면 yes"""
    y, m, d = map(int, date_str.split("-"))
    check = date(y, m, d)
    return "yes" if is_holiday_korea(check) else "no"


# -----------------------------------------------------
# 🔹 Tool 3: 특정 날짜 주말 여부 (토/일)
# -----------------------------------------------------
@tool
def is_weekend(date_str: str) -> str:
    """주어진 날짜가 토요일·일요일이면 yes"""
    y, m, d = map(int, date_str.split("-"))
    dt = date(y, m, d)
    return "yes" if dt.weekday() in (5, 6) else "no"


# -----------------------------------------------------
# 🔹 Tool 4: 특정 날짜의 요일 반환
# -----------------------------------------------------
@tool
def get_weekday(date_str: str) -> str:
    """주어진 날짜의 요일을 (월~일)로 반환"""
    y, m, d = map(int, date_str.split("-"))
    dt = date(y, m, d)
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    return weekdays[dt.weekday()]


# -----------------------------------------------------
# 🔹 사용자 질문에서 날짜 추출
# -----------------------------------------------------
def extract_date_from_question(text: str):
    """
    질문에서 날짜(예: 10월 3일, 2025-03-01)를 추출해 YYYY-MM-DD로 변환.
    없으면 None.
    """

    # 1) YYYY-MM-DD
    m = re.search(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", text)
    if m:
        y, mo, d = map(int, m.groups())
        return f"{y:04d}-{mo:02d}-{d:02d}"

    # 2) "10월 3일"
    m = re.search(r"(\d{1,2})월\s*(\d{1,2})일", text)
    if m:
        mo, d = map(int, m.groups())
        today = datetime.now().date()
        y = today.year
        return f"{y:04d}-{mo:02d}-{d:02d}"

    return None


# -----------------------------------------------------
# 🔹 PDF 로드 및 벡터 RAG 구성
# -----------------------------------------------------
loader = PyPDFLoader("data/Pilates.pdf")
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=100)
docs = splitter.split_documents(pages)

embeddings = OpenAIEmbeddings()
vectordb = FAISS.from_documents(docs, embeddings)

retriever = vectordb.as_retriever(search_kwargs={"k": 3})


# -----------------------------------------------------
# 🔹 Prompt 템플릿
# -----------------------------------------------------
prompt = ChatPromptTemplate.from_template("""
너는 필라테스 운영 전문 어시스턴트이다.
아래 정보를 기반으로 가장 정확한 답변을 제공하라.

[참고문서]
{context}

[현재시간]
{current_time}

[사용자가 물어본 날짜]
{ask_date}

[사용자가 물어본 날짜 요일]
{ask_date_weekday}

[사용자가 물어본 날짜 공휴일 여부]
{ask_date_holiday}

[사용자가 물어본 날짜 주말 여부]
{ask_date_weekend}

[오늘 날짜]
{today}

[오늘 요일]
{today_weekday}

[오늘 공휴일 여부]
{today_holiday}

[오늘 날짜 주말 여부]
{today_weekend}

[질문]
{question}

규칙:
- 주말은 토요일과 일요일이다.
- 사용자가 특정 날짜를 질문한 경우 ask_date 기준으로 운영 규칙을 판단한다.
- 질문 날짜가 없다면 오늘(today)을 기준으로 판단한다.
- 공휴일이면 반드시 공휴일 운영 규정을 우선 적용한다.
- 문서에 없으면 "문서에 정보가 없습니다"라고 답한다.
- 답변은 간결하고 정확하게 작성한다.
""")

# -----------------------------------------------------
# 🔹 RAG 실행 함수
# -----------------------------------------------------
def get_answer(query: str) -> str:

    extracted_date = extract_date_from_question(query)

    today_obj = datetime.now(pytz.timezone("Asia/Seoul")).date()
    today_str = today_obj.strftime("%Y-%m-%d")

    ask_date = extracted_date if extracted_date else today_str

    # 날짜 정보 계산
    ask_date_holiday = check_holiday.run(ask_date)
    ask_date_weekend = is_weekend.run(ask_date)
    ask_date_weekday = get_weekday.run(ask_date)

    today_holiday = check_holiday.run(today_str)
    today_weekend = is_weekend.run(today_str)
    today_weekday = get_weekday.run(today_str)

    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
            "current_time": lambda _: get_kst_datetime.run(""),

            "ask_date": lambda _: ask_date,
            "ask_date_weekday": lambda _: ask_date_weekday,
            "ask_date_holiday": lambda _: ask_date_holiday,
            "ask_date_weekend": lambda _: ask_date_weekend,

            "today": lambda _: today_str,
            "today_weekday": lambda _: today_weekday,
            "today_holiday": lambda _: today_holiday,
            "today_weekend": lambda _: today_weekend,
        }
        | prompt
        | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    )

    response = chain.invoke(query)
    return response.content
