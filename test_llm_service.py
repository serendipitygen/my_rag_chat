"""
LLM 서비스 모듈 테스트 스크립트
LM Studio 연결 및 응답 생성 기능 테스트
"""
import os
import sys
import time
import argparse
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 내부 모듈
from core.llm_service import LLMService
from utils.common import setup_logger

# 로거 설정
logger = setup_logger("test_llm", "logs/test_llm.log")

# 환경 변수 로드
load_dotenv()


def test_lmstudio_response(model_name=None, stream=False):
    """
    LM Studio 응답 생성 테스트
    
    Args:
        model_name (str, optional): 사용할 모델 이름
        stream (bool): 스트림 모드 사용 여부
    """
    # LM Studio 기본 설정
    url = "http://localhost:4982"
    
    # 모델명 지정하지 않은 경우 기본값 사용
    if not model_name:
        model_name = "kanana-nano-2.1b-instruct"
    
    print(f"\n{'=' * 50}")
    print(f"LM Studio 테스트 시작 (모델: {model_name})")
    print(f"{'=' * 50}")
    
    try:
        # LM Studio 서비스 초기화
        llm = LLMService(
            provider="lmstudio",
            model=model_name,
            temperature=0.7,
            max_tokens=1024,
            lmstudio_url=url
        )
        
        # 테스트 프롬프트
        test_prompt = "안녕하세요! Flutter에 대해 설명해줘."
        
        print(f"\n[입력 프롬프트]\n{test_prompt}\n")
        print(f"[응답 결과]")
        
        start_time = time.time()
        
        if stream:
            # 스트림 방식으로 응답 생성
            print("\n스트림 응답 생성 중...")
            try:
                for text_chunk in llm.generate_stream_response(test_prompt):
                    print(text_chunk, end="", flush=True)
                print()  # 줄바꿈
            except Exception as e:
                print(f"\n스트림 응답 생성 중 오류 발생: {str(e)}")
        else:
            # 일반 방식으로 응답 생성
            print("\n응답 생성 중...")
            result = llm.generate_response(test_prompt)
            
            if "error" in result:
                print(f"오류: {result['error']}")
            else:
                print(result["text"])
                
                # 토큰 정보 출력 (있는 경우)
                if "tokens" in result:
                    tokens = result["tokens"]
                    print(f"\n[토큰 정보]")
                    print(f"- 프롬프트 토큰: {tokens.get('prompt_tokens', 'N/A')}")
                    print(f"- 응답 토큰: {tokens.get('completion_tokens', 'N/A')}")
                    print(f"- 총 토큰: {tokens.get('total_tokens', 'N/A')}")
        
        elapsed_time = time.time() - start_time
        print(f"\n[처리 시간] {elapsed_time:.2f}초\n")
            
    except Exception as e:
        print(f"테스트 중 오류 발생: {str(e)}")
    
    print(f"{'=' * 50}")
    print("테스트 완료")
    print(f"{'=' * 50}\n")


def test_openai_response(model_name=None, stream=False):
    """
    OpenAI 응답 생성 테스트
    
    Args:
        model_name (str, optional): 사용할 모델 이름
        stream (bool): 스트림 모드 사용 여부
    """
    # OpenAI API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return
    
    # 모델명 지정하지 않은 경우 기본값 사용
    if not model_name:
        model_name = "gpt-3.5-turbo"
    
    print(f"\n{'=' * 50}")
    print(f"OpenAI 테스트 시작 (모델: {model_name})")
    print(f"{'=' * 50}")
    
    try:
        # OpenAI 서비스 초기화
        llm = LLMService(
            provider="openai",
            model=model_name,
            api_key=api_key,
            temperature=0.7,
            max_tokens=1024
        )
        
        # 테스트 프롬프트
        test_prompt = "안녕하세요! Flutter에 대해 설명해줘."
        
        print(f"\n[입력 프롬프트]\n{test_prompt}\n")
        print(f"[응답 결과]")
        
        start_time = time.time()
        
        if stream:
            # 스트림 방식으로 응답 생성
            print("\n스트림 응답 생성 중...")
            try:
                for chunk in llm.generate_stream_response(test_prompt):
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        print(chunk.choices[0].delta.content, end="", flush=True)
                print()  # 줄바꿈
            except Exception as e:
                print(f"\n스트림 응답 생성 중 오류 발생: {str(e)}")
        else:
            # 일반 방식으로 응답 생성
            print("\n응답 생성 중...")
            result = llm.generate_response(test_prompt)
            
            if "error" in result:
                print(f"오류: {result['error']}")
            else:
                print(result["text"])
                
                # 토큰 정보 출력 (있는 경우)
                if "tokens" in result:
                    tokens = result["tokens"]
                    print(f"\n[토큰 정보]")
                    print(f"- 프롬프트 토큰: {tokens.get('prompt_tokens', 'N/A')}")
                    print(f"- 응답 토큰: {tokens.get('completion_tokens', 'N/A')}")
                    print(f"- 총 토큰: {tokens.get('total_tokens', 'N/A')}")
        
        elapsed_time = time.time() - start_time
        print(f"\n[처리 시간] {elapsed_time:.2f}초\n")
            
    except Exception as e:
        print(f"테스트 중 오류 발생: {str(e)}")
    
    print(f"{'=' * 50}")
    print("테스트 완료")
    print(f"{'=' * 50}\n")


def main():
    """
    메인 함수
    """
    # 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(description="LLM 서비스 테스트")
    
    parser.add_argument(
        "--provider", 
        type=str, 
        choices=["openai", "lmstudio"], 
        default="lmstudio",
        help="LLM 프로바이더 (openai 또는 lmstudio)"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        help="사용할 모델 이름"
    )
    
    parser.add_argument(
        "--stream", 
        action="store_true", 
        help="스트림 모드 사용"
    )
    
    args = parser.parse_args()
    
    # 테스트 실행
    if args.provider == "openai":
        test_openai_response(args.model, args.stream)
    else:
        test_lmstudio_response(args.model, args.stream)


if __name__ == "__main__":
    # 로그 디렉토리 생성
    os.makedirs("logs", exist_ok=True)
    
    # 테스트 실행
    main()
