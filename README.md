# RAG 기반 개인용 생성형 AI 챗봇

개인 PC에 저장된 문서를 업로드하고, 해당 문서를 기반으로 질의응답을 수행할 수 있는 RAG(Retrieval-Augmented Generation) 챗봇 시스템입니다.

## 📋 프로젝트 개요

이 프로젝트는 사용자가 개인 문서(PDF, DOCX, TXT, MD, EML)를 업로드하면, 문서 내용을 벡터화하여 저장하고, 사용자 질문에 대해 관련 문서 내용을 검색하여 AI가 답변하는 시스템입니다.

### 주요 특징
- 🗂️ **다양한 문서 형식 지원**: PDF, DOCX, TXT, MD, EML 파일 처리
- 🔍 **벡터 기반 검색**: FAISS를 사용한 빠른 문서 검색
- 🤖 **다중 LLM 지원**: Google Gemini API, LM Studio 연동
- 🌐 **웹 기반 인터페이스**: Dash 대시보드 + Chainlit 챗봇
- 🇰🇷 **한국어 최적화**: 한국어 임베딩 모델 사용

## 🛠️ 기술 스택

- **Backend**: Python 3.11
- **벡터 DB**: FAISS
- **임베딩**: jhgan/ko-sroberta-multitask (한국어 특화)
- **LLM**: Google Gemini API, LM Studio
- **UI**: Dash (대시보드), Chainlit (챗봇)
- **문서 처리**: LangChain, PyPDF, python-docx

## 🚀 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/serendipitygen/my_rag_chat.git
cd my_rag_chat
```

### 2. Python 가상환경 설정
```bash
# Conda 환경 생성 (권장)
conda create -n my_rag python=3.11
conda activate my_rag

# 또는 venv 사용
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가:

```env
# Google Gemini API (필수)
GEMINI_API_KEY=your_gemini_api_key_here

# LM Studio (선택사항)
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL_NAME=your_model_name
```

### 5. 디렉토리 구조 확인
프로젝트는 다음 디렉토리들을 자동으로 생성합니다:
- `data/uploads/`: 업로드된 파일 저장
- `data/vector_db/`: 벡터 DB 저장
- `logs/`: 로그 파일 저장

## 🎯 실행 방법

### 1. 파일 등록 대시보드 실행
```bash
python dashboard.py
```
브라우저에서 `http://localhost:8050`으로 접속하여 문서 업로드

### 2. 챗봇 실행
```bash
chainlit run chat.py -w
```
브라우저에서 `http://localhost:8000`으로 접속하여 챗봇 사용

## 📁 프로젝트 구조

```
my_rag_chat/
├── core/                    # 핵심 모듈
│   ├── document_processor.py   # 문서 처리
│   ├── embedding_model.py      # 임베딩 모델
│   ├── vector_db.py           # 벡터 DB 관리
│   ├── rag_engine.py          # RAG 엔진
│   └── llm_service.py         # LLM 서비스
├── llm_services/            # LLM 서비스 구현
│   ├── gemini_service.py      # Gemini API
│   └── lm_studio_service.py   # LM Studio API
├── utils/                   # 유틸리티
│   └── common.py             # 공통 함수
├── data/                    # 데이터 저장소
│   ├── uploads/             # 업로드 파일
│   └── vector_db/           # 벡터 DB
├── logs/                    # 로그 파일
├── docs/                    # 문서
├── chat.py                  # 챗봇 메인 앱
├── dashboard.py             # 대시보드 메인 앱
└── requirements.txt         # 의존성
```

## 📖 사용 방법

### 1. 문서 업로드
1. 대시보드(`http://localhost:8050`)에 접속
2. "Choose Files" 버튼으로 문서 업로드
3. 지원 형식: PDF, DOCX, TXT, MD, EML
4. 업로드된 파일은 자동으로 청킹되어 벡터 DB에 저장

### 2. 챗봇 사용
1. 챗봇(`http://localhost:8000`)에 접속
2. 업로드된 문서와 관련된 질문 입력
3. AI가 관련 문서 내용을 바탕으로 답변 제공

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 특정 모듈 테스트
python test_chat.py
python test_document_processor.py
python test_llm_service.py
```

## 📝 로그 확인

각 모듈별 로그는 `logs/` 디렉토리에 저장됩니다:
- `chat.log`: 챗봇 관련 로그
- `dashboard.log`: 대시보드 관련 로그
- `document_processor.log`: 문서 처리 로그
- `rag_engine.log`: RAG 엔진 로그

## 🔧 설정 커스터마이징

### 임베딩 모델 변경
`core/rag_engine.py`에서 임베딩 모델을 변경할 수 있습니다:
```python
rag_engine = RAGEngine(
    embedding_model_name="sentence-transformers/distiluse-base-multilingual-cased-v2",
    # ... 기타 설정
)
```

### LLM 서비스 변경
환경 변수 또는 코드에서 LLM 서비스를 변경할 수 있습니다:
- `gemini`: Google Gemini API
- `lm_studio`: LM Studio API

## 🚨 문제 해결

### 일반적인 오류
1. **CUDA 관련 오류**: CPU 버전 사용을 위해 `torch` 재설치
2. **메모리 부족**: 큰 문서 처리 시 청크 크기 조정
3. **API 키 오류**: `.env` 파일의 API 키 확인

### 로그 확인
상세한 오류 정보는 `logs/` 디렉토리의 로그 파일에서 확인하세요.

## 📄 라이선스

이 프로젝트는 개인용 및 교육용으로 자유롭게 사용할 수 있습니다.

## 🤝 기여

버그 리포트나 기능 요청은 GitHub Issues를 통해 제출해 주세요.