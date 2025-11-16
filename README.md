# 🧘 필라테스 Q&A 챗봇 (RAG 기반 AI 챗봇)

이 프로젝트는 **RAG(Retrieval-Augmented Generation)** 기술을 활용하여  
필라테스 운영 매뉴얼(PDF 기반)을 분석하고,  
사용자가 질문한 날짜(평일/주말/공휴일)를 자동으로 인식해 올바른 운영 규칙을 안내하는 **지능형 챗봇**입니다.

Streamlit UI와 LangChain 기반 RAG 파이프라인을 사용하며,  
대화 기록은 로컬 파일(`conversation.json`)로 자동 저장됩니다.

---

## 📂 프로젝트 구조

```
project/
├── app.py                 # Streamlit UI
├── rag_pilates.py         # RAG 로직 및 날짜 분석, Tools
├── data/
│   └── Pilates.pdf        # 필라테스 운영 문서
├── conversation.json      # (자동 생성) 대화 기록 저장 파일
└── requirements.txt       # 패키지 목록
```

---

## 🧠 주요 기능

### 1️⃣ **정확한 날짜 기반 답변**
사용자 질문에서 날짜를 자동 추출  
→ 평일·주말·공휴일 여부 판별  
→ PDF 기반 운영 규칙 적용

### 2️⃣ **날짜 관련 도구(Tools) 직접 구현**
- 한국 공휴일 계산 (holidays 패키지 없이 직접 구현)
- 요일 계산  
- 주말(토/일) 판별  
- 현재 한국 시간 반환  
- 질문에서 날짜 자동 추출

### 3️⃣ **RAG 기반 정밀 답변**
- PDF 문서를 RecursiveCharacterTextSplitter 로 분할
- OpenAI Embeddings + FAISS 벡터 DB
- 최적화된 프롬프트 기반 답변 생성

### 4️⃣ **Streamlit UI 제공**
- 사용자 질문 입력  
- 좌/우 정렬 메시지 출력  
- 챗봇/사용자 구분 출력  
- 대화 초기화 기능  
- 대화 내용 자동 저장 및 다시 로드

---

## 📦 설치 방법

### 1. 리포지토리 클론
```bash
git clone https://github.com/yourname/pilates-rag-chatbot.git
cd pilates-rag-chatbot

2. 필요한 패키지 설치
pip install -r requirements.txt

3. 환경 변수 설정
.env 파일 생성 후 아래처럼 입력:

OPENAI_API_KEY=your_api_key_here

---

🚀 실행 방법
Streamlit 실행:
```bash
streamlit run app.py
```
브라우저가 자동으로 열리며
필라테스 Q&A 챗봇을 바로 사용할 수 있습니다.
---
📄 requirements.txt
아래 패키지들이 포함됩니다:

arduino
코드 복사
streamlit
langchain
langchain-community
langchain-openai
langchain-text-splitters
faiss-cpu
python-dotenv
pypdf
pytz
tiktoken
---
🛠 기술 스택
Language Model: OpenAI GPT-4o-mini

Framework: LangChain

Vector DB: FAISS

Frontend: Streamlit

Document Splitter: RecursiveCharacterTextSplitter

Date Recognition: 정규식 + 직접 구현한 한국 공휴일 계산



