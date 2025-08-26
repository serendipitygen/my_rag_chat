"""
GeminiService 테스트 모듈

이 파일은 Gemini API 서비스를 테스트하는 코드입니다.
"""
import os
import sys
import logging
from pathlib import Path

# 상위 디렉토리를 파이썬 path에 추가 (모듈 import를 위해)
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# GeminiService 클래스 가져오기
from llm_services.gemini_service import GeminiService

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_simple_query():
    """
    간단한 질의로 Gemini 서비스를 테스트합니다.
    """
    # API 키 설정
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("환경 변수 'GOOGLE_API_KEY'가 설정되지 않았습니다.")
        api_key = input("Google Gemini API 키를 입력하세요: ")

    # 모델 이름 설정
    model_name = "gemini-1.5-pro"  # 최신 모델 사용
    
    print(f"Gemini 서비스 초기화 중... (모델: {model_name})")
    service = GeminiService(api_key=api_key, model=model_name, logger=logger)
    
    # 서비스 사용 가능 여부 확인
    if service.is_available():
        print("Gemini 서비스 연결 성공!")
    else:
        print("Gemini 서비스 연결 실패!")
        return
    
    # 모델 정보 출력
    model_info = service.get_model_info()
    print("\n모델 정보:")
    for key, value in model_info.items():
        print(f"- {key}: {value}")
    
    # 테스트 질의
    test_queries = [
        "한국어로 인공지능에 대해 간략하게 설명해줘",
        "RAG(Retrieval Augmented Generation)이란 무엇인가요?",
        "EML 파일이란 무엇이며 어떻게 처리할 수 있나요?"
    ]
    
    # 각 질의에 대한 응답 테스트
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n[테스트 {i}] 질의: {query}")
        
        # 응답 생성
        response = service.generate_response(query)
        
        # 응답 출력
        print("\n응답:")
        print(response)

def test_streaming_response():
    """
    스트리밍 응답 방식으로 Gemini 서비스를 테스트합니다.
    """
    # API 키 설정
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("환경 변수 'GOOGLE_API_KEY'가 설정되지 않았습니다.")
        api_key = input("Google Gemini API 키를 입력하세요: ")

    # 모델 이름 설정
    model_name = "gemini-1.5-pro"  # 최신 모델 사용
    
    print(f"Gemini 서비스 초기화 중... (모델: {model_name})")
    service = GeminiService(api_key=api_key, model=model_name, logger=logger)
    
    # 서비스 사용 가능 여부 확인
    if not service.is_available():
        print("Gemini 서비스 연결 실패!")
        return
    
    # 테스트 질의
    query = "한국의 역사를 간략하게 요약해줘"
    print(f"\n스트리밍 테스트 질의: {query}")
    print("\n스트리밍 응답:")
    
    # 스트리밍 응답 생성 및 출력
    for token in service.generate_stream_response(query):
        print(token, end="", flush=True)

def main():
    """
    메인 함수
    """
    print("=" * 50)
    print("Gemini 서비스 테스트 시작")
    print("=" * 50)
    
    # 일반 응답 테스트
    test_simple_query()
    
    # 사용자 확인 후 스트리밍 테스트 실행
    user_input = input("\n\n스트리밍 응답 테스트를 실행하시겠습니까? (y/n): ")
    if user_input.lower() == 'y':
        test_streaming_response()

    print("\n" + "=" * 50)
    print("Gemini 서비스 테스트 완료")
    print("=" * 50)

if __name__ == "__main__":
    main()
