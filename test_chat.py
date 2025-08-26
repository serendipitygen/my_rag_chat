"""
질문-응답 테스트 모듈 - 벡터 DB에서 문서를 검색하고 LM Studio API로 답변 생성

이 스크립트는 다음과 같은 순서로 작동합니다:
1. 사용자 질문 입력 받기
2. 임베딩 모델로 질문을 벡터로 변환
3. 벡터 DB에서 관련 문서 검색
4. LM Studio API를 통해 검색된 문서 정보를 바탕으로 답변 생성
5. 결과 출력
"""

import os
import sys
import argparse
import time
from typing import Dict, Any, Optional

# 내부 모듈
from utils.common import setup_logger, get_project_root
from core.rag_engine import RAGEngine

# 로거 설정
logger = setup_logger(
    "test_chat", 
    os.path.join(get_project_root(), "logs", "test_chat.log")
)

def setup_arg_parser() -> argparse.ArgumentParser:
    """
    명령행 인자 파서 설정
    
    Returns:
        argparse.ArgumentParser: 설정된 인자 파서
    """
    parser = argparse.ArgumentParser(description="RAG 챗봇 테스트")
    
    # 벡터 DB 경로 설정
    parser.add_argument(
        "--db_path", 
        type=str, 
        default=None,
        help="벡터 DB 경로 (기본값: 프로젝트 루트/data/vector_db)"
    )
    
    # LLM 설정
    parser.add_argument(
        "--provider", 
        type=str, 
        default="lmstudio",
        choices=["lmstudio", "openai"],
        help="LLM 제공자 (기본값: lmstudio)"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        default="",
        help="LLM 모델명 (기본값: 제공자의 기본 모델)"
    )
    
    parser.add_argument(
        "--lmstudio_url", 
        type=str, 
        default="http://localhost:4982",
        help="LM Studio API URL (기본값: http://localhost:4982)"
    )
    
    # 검색 설정
    parser.add_argument(
        "--top_k", 
        type=int, 
        default=5,
        help="검색 결과 개수 (기본값: 5)"
    )
    
    # 모드 설정
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="대화형 모드로 실행"
    )
    
    return parser

def print_separator(width: int = 60) -> None:
    """
    구분선 출력
    
    Args:
        width (int): 구분선 너비
    """
    print(f"\n{'=' * width}")

def print_result(result: Dict[str, Any]) -> None:
    """
    질의 결과 출력
    
    Args:
        result (Dict[str, Any]): 응답 결과 정보
    """
    if not result.get("success", False):
        print(f"\n[오류] {result.get('error', '알 수 없는 오류가 발생했습니다.')}")
        return
    
    print(f"\n[답변]")
    print(f"{result.get('answer', '응답을 생성할 수 없습니다.')}")
    
    # 참조 문서 정보 출력
    if "references" in result and result["references"]:
        print(f"\n[참조한 문서]")
        for idx, ref in enumerate(result["references"], 1):
            print(f"{idx}. {ref.get('title', 'N/A')} (유사도: {ref.get('similarity', 0):.4f})")
    
    # 모델 정보 출력
    if "model_info" in result:
        model_info = result["model_info"]
        print(f"\n[모델 정보]")
        print(f"- 모델: {model_info.get('model', 'N/A')}")
        print(f"- 제공자: {model_info.get('provider', 'N/A')}")
    
    # 토큰 사용량 출력
    if "token_usage" in result and result["token_usage"]:
        tokens = result["token_usage"]
        print(f"\n[토큰 사용량]")
        print(f"- 입력 토큰: {tokens.get('prompt_tokens', 0)}")
        print(f"- 출력 토큰: {tokens.get('completion_tokens', 0)}")
        print(f"- 전체 토큰: {tokens.get('total_tokens', 0)}")

def test_single_query(engine: RAGEngine, 
                     query: str, 
                     top_k: int = 5) -> None:
    """
    단일 질의 테스트
    
    Args:
        engine (RAGEngine): RAG 엔진 인스턴스
        query (str): 사용자 질의
        top_k (int): 검색 결과 개수
    """
    print_separator()
    print(f"[질문] {query}")
    
    start_time = time.time()
    result = engine.query(query_text=query, top_k=top_k)
    elapsed = time.time() - start_time
    
    print_result(result)
    print(f"\n[처리 시간] {elapsed:.2f}초")
    print_separator()

def test_interactive_mode(engine: RAGEngine, top_k: int = 5) -> None:
    """
    대화형 모드로 테스트
    
    Args:
        engine (RAGEngine): RAG 엔진 인스턴스
        top_k (int): 검색 결과 개수
    """
    print_separator()
    print("대화형 질의응답 모드를 시작합니다.")
    print("- 종료하려면 'q', 'quit', 'exit' 또는 빈 줄을 입력하세요.")
    print_separator()
    
    total_queries = 0
    
    while True:
        print()
        query = input("질문을 입력하세요: ").strip()
        
        if not query or query.lower() in ['q', 'quit', 'exit']:
            print("대화를 종료합니다.")
            break
        
        total_queries += 1
        print(f"\n[질문 #{total_queries}] {query}")
        
        start_time = time.time()
        result = engine.query(query_text=query, top_k=top_k)
        elapsed = time.time() - start_time
        
        print_result(result)
        print(f"\n[처리 시간] {elapsed:.2f}초")
        print_separator()
    
    if total_queries > 0:
        print(f"\n총 {total_queries}개 질문에 응답했습니다.")
    
    print("대화형 질의응답을 종료합니다.")
    print_separator()

def main():
    """
    메인 함수
    """
    # 인자 파싱
    parser = setup_arg_parser()
    args = parser.parse_args()
    
    print_separator()
    print("RAG 챗봇 테스트 시작")
    print_separator()
    
    try:
        print("\n[초기화 중...]")
        
        # 벡터 DB 경로 설정
        vector_db_path = args.db_path
        if vector_db_path is None:
            vector_db_path = os.path.join(get_project_root(), "data", "vector_db")
        
        print(f"- 벡터 DB 경로: {vector_db_path}")
        
        if not os.path.exists(vector_db_path):
            print(f"오류: 벡터 DB 경로가 존재하지 않습니다: {vector_db_path}")
            print("먼저 'test_document_processor.py --mode process'를 실행하여 문서를 처리해주세요.")
            return 1
        
        # LLM 모델 설정
        provider = args.provider
        model = args.model
        
        if not model:
            if provider == "lmstudio":
                model = "default-model"  # LM Studio의 기본 모델
            else:  # openai
                model = "gpt-3.5-turbo"
                
        print(f"- LLM 제공자: {provider}")
        print(f"- LLM 모델: {model}")
        
        if provider == "lmstudio":
            print(f"- LM Studio URL: {args.lmstudio_url}")
        
        # RAG 엔진 초기화
        print("- RAG 엔진 초기화 중...")
        engine = RAGEngine(
            embedding_model_name="jhgan/ko-sroberta-multitask",
            llm_provider=provider,
            llm_model=model,
            vector_db_path=vector_db_path
        )
        
        # LM Studio에 특정 URL 설정이 필요한 경우
        if provider == "lmstudio" and args.lmstudio_url:
            engine.llm_service.lmstudio_url = args.lmstudio_url
        
        # 벡터 DB 정보 출력
        stats = engine.get_engine_info()
        db_stats = stats.get("vector_db", {})
        
        print("\n[벡터 DB 정보]")
        print(f"- 총 문서 수: {db_stats.get('document_count', 0)}")
        print(f"- 총 청크 수: {db_stats.get('chunk_count', 0)}")
        print(f"- 총 벡터 수: {db_stats.get('vector_count', 0)}")
        
        # 실행 모드에 따라 처리
        if args.interactive:
            # 대화형 모드
            test_interactive_mode(engine, top_k=args.top_k)
        else:
            # 단일 질의 모드
            query = input("\n질문을 입력하세요: ").strip()
            if query:
                test_single_query(engine, query, top_k=args.top_k)
            else:
                print("질문이 입력되지 않았습니다.")
        
        print("\nRAG 챗봇 테스트 완료")
        print_separator()
        return 0
        
    except Exception as e:
        print(f"\n[오류] 테스트 중 예외가 발생했습니다: {str(e)}")
        import traceback
        traceback.print_exc()
        print_separator()
        return 1

if __name__ == "__main__":
    sys.exit(main())
