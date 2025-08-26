"""
문서 처리기 테스트 스크립트
문서 파일을 벡터 DB에 저장하고 쿼리 수행하는 기능 테스트
"""
import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any
import json

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 내부 모듈
from core.document_processor import DocumentProcessor
from core.embedding_model import EmbeddingModel
from core.vector_db import VectorDB
from utils.common import setup_logger, get_project_root

# 로거 설정
logger = setup_logger("test_doc_processor", "logs/test_doc_processor.log")


def process_documents(docs_path: str, save_path: str = None, query: str = None, top_k: int = 5):
    """
    문서 처리 및 쿼리 테스트
    
    Args:
        docs_path (str): 문서 파일 또는 디렉토리 경로
        save_path (str, optional): 벡터 DB 저장 경로
        query (str, optional): 검색 쿼리 (있는 경우 검색 수행)
        top_k (int): 검색 결과 수 (기본값: 5)
    """
    print(f"\n{'=' * 60}")
    print(f"문서 처리 테스트 시작")
    print(f"{'=' * 60}")
    
    start_time = time.time()
    
    try:
        # 경로 정규화
        docs_path = os.path.abspath(docs_path)
        
        # 저장 경로 설정
        if save_path is None:
            save_path = os.path.join(get_project_root(), "data", "vector_db")
        
        # 저장 디렉토리 생성
        os.makedirs(save_path, exist_ok=True)
        
        print(f"\n[초기화 중...]")
        print(f"- 문서 경로: {docs_path}")
        print(f"- 벡터 DB 저장 경로: {save_path}")
        
        # 임베딩 모델 초기화
        print(f"- 임베딩 모델 초기화 중...")
        embedding_model = EmbeddingModel("jhgan/ko-sroberta-multitask")
        
        # 벡터 DB 초기화
        print(f"- 벡터 DB 초기화 중...")
        vector_db = VectorDB(save_path, dimension=768)
        
        # 문서 처리기 초기화
        print(f"- 문서 처리기 초기화 중...")
        doc_processor = DocumentProcessor(
            embedding_model=embedding_model,
            vector_db=vector_db,
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # 문서 처리
        if os.path.isfile(docs_path):
            # 단일 파일 처리
            print(f"\n[파일 처리 중...]")
            print(f"- 파일: {os.path.basename(docs_path)}")
            
            file_ext = os.path.splitext(docs_path)[1].lower()
            if file_ext not in ['.pdf', '.docx', '.txt', '.md']:
                print(f"지원되지 않는 파일 형식입니다: {file_ext}")
                return
            
            try:
                chunks_count, metadata = doc_processor.process_file(docs_path)
                
                print(f"- 처리 완료")
                print(f"  - 청크 수: {chunks_count}")
                print(f"  - 문서 ID: {metadata.get('doc_id', 'N/A')}")
                print(f"  - 총 텍스트 길이: {metadata.get('total_text_length', 0):,} 글자")
                
                # 벡터 DB 저장
                vector_db.save_index()
                print(f"- 벡터 DB 저장 완료: {save_path}")
                
            except Exception as e:
                print(f"파일 처리 중 오류 발생: {str(e)}")
                return
                
        elif os.path.isdir(docs_path):
            # 디렉토리 처리
            print(f"\n[디렉토리 처리 중...]")
            print(f"- 디렉토리: {docs_path}")
            
            try:
                results = doc_processor.process_directory(
                    docs_path, 
                    file_types=['.pdf', '.docx', '.txt', '.md']
                )
                
                print(f"- 처리 완료")
                print(f"  - 처리된 파일 수: {len(results)}")
                
                if results:
                    total_chunks = sum(doc.get('chunk_count', 0) for doc in results)
                    print(f"  - 총 청크 수: {total_chunks}")
                    
                    # 처리된 파일 목록 출력
                    print(f"\n[처리된 파일 목록]")
                    for i, doc in enumerate(results, 1):
                        print(f"  {i}. {doc.get('file_name', 'N/A')} (청크: {doc.get('chunk_count', 0)})")
                
                # 벡터 DB 저장
                vector_db.save_index()
                print(f"- 벡터 DB 저장 완료: {save_path}")
                
            except Exception as e:
                print(f"디렉토리 처리 중 오류 발생: {str(e)}")
                return
        else:
            print(f"지정된 경로가 존재하지 않습니다: {docs_path}")
            return
        
        # 쿼리 수행 (있는 경우)
        if query:
            print(f"\n[쿼리 수행 중...]")
            print(f"- 쿼리: {query}")
            print(f"- 상위 {top_k}개 결과 검색")
            
            try:
                # 유사 문서 검색
                results = doc_processor.query_similar(query, top_k=top_k)
                
                if not results:
                    print(f"- 검색 결과가 없습니다.")
                else:
                    print(f"- 검색 결과 ({len(results)}개):")
                    
                    for i, result in enumerate(results, 1):
                        print(f"\n결과 #{i} (유사도: {result.get('score', 0):.4f})")
                        metadata = result.get('metadata', {})
                        file_name = metadata.get('file_name', 'N/A')
                        chunk_index = metadata.get('chunk_index', 'N/A')
                        
                        print(f"- 출처: {file_name} (청크 #{chunk_index})")
                        print(f"- 내용:")
                        
                        text = result.get('text', '')
                        # 텍스트가 너무 길면 처음 200자만 표시
                        if len(text) > 200:
                            print(f"{text[:200]}...(계속)")
                        else:
                            print(text)
                
            except Exception as e:
                print(f"쿼리 수행 중 오류 발생: {str(e)}")
        
        elapsed_time = time.time() - start_time
        print(f"\n[처리 시간] {elapsed_time:.2f}초")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {str(e)}")
    
    print(f"\n{'=' * 60}")
    print(f"테스트 완료")
    print(f"{'=' * 60}")


def test_interactive_query(save_path: str = None):
    """
    대화형 문서 검색 테스트
    
    Args:
        save_path (str, optional): 벡터 DB 로드 경로
    """
    print(f"\n{'=' * 60}")
    print(f"대화형 문서 검색 테스트 시작")
    print(f"{'=' * 60}")
    
    try:
        # 저장 경로 설정
        if save_path is None:
            save_path = os.path.join(get_project_root(), "data", "vector_db")
        
        if not os.path.exists(save_path):
            print(f"벡터 DB 경로가 존재하지 않습니다: {save_path}")
            print(f"먼저 문서를 처리하여 벡터 DB를 생성해주세요.")
            return
        
        print(f"\n[초기화 중...]")
        print(f"- 벡터 DB 로드 경로: {save_path}")
        
        # 임베딩 모델 및 벡터 DB 초기화
        print(f"- 임베딩 모델 초기화 중...")
        embedding_model = EmbeddingModel("jhgan/ko-sroberta-multitask")
        
        print(f"- 벡터 DB 초기화 중...")
        vector_db = VectorDB(save_path, dimension=768)
        
        # 메타데이터 정보 출력
        stats = vector_db.get_stats()
        print(f"\n[벡터 DB 정보]")
        print(f"- 총 문서 수: {stats.get('document_count', 0)}")
        print(f"- 총 청크 수: {stats.get('chunk_count', 0)}")
        print(f"- 총 벡터 수: {stats.get('vector_count', 0)}")
        
        # 대화형 문서 검색 시작
        print(f"\n[대화형 문서 검색 시작]")
        print(f"- 질문을 입력하면 관련된 문서 청크를 검색합니다.")
        print(f"- 종료하려면 'q', 'quit', 'exit' 또는 빈 줄을 입력하세요.")
        
        while True:
            print(f"\n{'=' * 40}")
            query = input("질문을 입력하세요: ").strip()
            
            if not query or query.lower() in ['q', 'quit', 'exit']:
                print("대화형 문서 검색을 종료합니다.")
                break
            
            try:
                # 쿼리 임베딩 생성
                print(f"\n[검색 중...]")
                query_embedding = embedding_model.embed_query(query)
                
                # 유사 문서 검색
                results = vector_db.search(query_embedding, top_k=5)
                
                if not results:
                    print(f"\n검색 결과가 없습니다.")
                else:
                    print(f"\n[검색 결과 - 상위 {len(results)}개]")
                    
                    for i, result in enumerate(results, 1):
                        similarity = result.get('similarity', 0)
                        doc_id = result.get('doc_id', 'N/A')
                        doc_title = result.get('doc_title', 'N/A')
                        
                        # 문서 정보
                        doc_info = vector_db.get_document_by_id(doc_id)
                        file_path = doc_info.get('file_path', 'N/A') if doc_info else 'N/A'
                        
                        # 청크 정보
                        chunk_id = result.get('chunk_id', 'N/A')
                        chunk_info = vector_db.get_chunk_by_id(chunk_id)
                        chunk_text = chunk_info.get('text', '텍스트 없음') if chunk_info else '텍스트 없음'
                        
                        print(f"\n결과 #{i} (유사도: {similarity:.4f})")
                        print(f"- 문서: {doc_title}")
                        print(f"- 출처: {os.path.basename(file_path)}")
                        print(f"- 내용:")
                        print(f"{chunk_text}")
                
            except Exception as e:
                print(f"검색 중 오류 발생: {str(e)}")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {str(e)}")
    
    print(f"\n{'=' * 60}")
    print(f"대화형 문서 검색 테스트 완료")
    print(f"{'=' * 60}")


def main():
    """
    메인 함수
    """
    # 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(description="문서 처리 및 쿼리 테스트")
    
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["process", "query"], 
        default="process",
        help="실행 모드 (process: 문서 처리, query: 대화형 쿼리)"
    )
    
    parser.add_argument(
        "--path", 
        type=str, 
        help="문서 파일 또는 디렉토리 경로 (process 모드에서 필수)"
    )
    
    parser.add_argument(
        "--db", 
        type=str, 
        help="벡터 DB 저장/로드 경로 (기본값: ./data/vector_db)"
    )
    
    parser.add_argument(
        "--query", 
        type=str, 
        help="검색 쿼리 (process 모드에서 선택 사항)"
    )
    
    parser.add_argument(
        "--top-k", 
        type=int, 
        default=5,
        help="검색 결과 수 (기본값: 5)"
    )
    
    args = parser.parse_args()
    
    # 로그 및 데이터 디렉토리 생성
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data/vector_db", exist_ok=True)
    
    # 모드별 실행
    if args.mode == "process":
        if not args.path:
            print("process 모드에서는 --path 인자가 필요합니다.")
            parser.print_help()
            return
        
        process_documents(args.path, args.db, args.query, args.top_k)
        
    elif args.mode == "query":
        test_interactive_query(args.db)


if __name__ == "__main__":
    main()
