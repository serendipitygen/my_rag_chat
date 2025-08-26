"""
RAG 엔진 모듈 - 검색 증강 생성 기능 구현
"""
import os
import logging
from typing import List, Dict, Optional, Union, Any, Tuple
import numpy as np
from pathlib import Path

# 랭체인 텍스트 분할기
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 내부 모듈
from utils.common import setup_logger, get_project_root, sanitize_filename
from utils.document_processor import DocumentProcessor
from core.embedding_model import EmbeddingModel
from core.vector_db import VectorDB
from core.llm_connector import LLMConnector

# 로거 설정
logger = setup_logger(
    "rag_engine", 
    os.path.join(get_project_root(), "logs", "rag_engine.log")
)

class RAGEngine:
    """
    RAG(Retrieval Augmented Generation) 엔진 클래스
    
    문서 처리, 임베딩, 벡터 검색, LLM 응답 생성을 통합하여
    검색 기반의 질의응답 기능을 제공
    """
    
    def __init__(self,
                embedding_model_name: str = "jhgan/ko-sroberta-multitask",
                llm_service: str = "lm_studio",
                vector_db_path: Optional[str] = None,
                chunk_size: int = 1000,
                chunk_overlap: int = 200,
                config: Optional[Dict[str, Any]] = None):
        """
        RAG 엔진 초기화
        
        Args:
            embedding_model_name (str): 임베딩 모델 이름
            llm_service (str): LLM 서비스 (lm_studio 또는 gemini)
            vector_db_path (Optional[str]): 벡터 DB 경로
            chunk_size (int): 청크 크기 (기본값: 1000)
            chunk_overlap (int): 청크 겹침 크기 (기본값: 200)
            config (Optional[Dict[str, Any]]): 추가 설정 정보
        """
        logger.info("RAG 엔진 초기화 시작")
        
        # 설정 초기화
        self.config = config or {}
        
        # 모듈 초기화
        self.doc_processor = DocumentProcessor()
        
        # 임베딩 모델 초기화
        logger.info(f"임베딩 모델 '{embedding_model_name}' 초기화 중...")
        self.embedding_model = EmbeddingModel(model_name=embedding_model_name)
        
        # 벡터 DB 초기화
        if vector_db_path is None:
            vector_db_path = os.path.join(get_project_root(), "data", "vector_db")
            
        logger.info(f"벡터 DB 초기화 중... (경로: {vector_db_path})")
        self.vector_db = VectorDB(
            db_path=vector_db_path,
            dimension=self.embedding_model.embedding_dim
        )
        
        # LLM 커넥터 초기화
        logger.info(f"LLM 서비스 초기화 중... (서비스: {llm_service})")
        self.llm_connector = LLMConnector(config=self.config, logger=logger)
        self.current_llm_service = llm_service
        
        # 텍스트 분할기 초기화
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # 청크 설정
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        logger.info("RAG 엔진 초기화 완료")
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        문서 파일을 처리하여 벡터 DB에 저장
        
        Args:
            file_path (str): 처리할 파일 경로
            
        Returns:
            Dict[str, Any]: 처리 결과 (성공 여부, 문서 ID, 청크 수 등)
        """
        try:
            logger.info(f"문서 처리 시작: {file_path}")
            
            # 파일 존재 확인
            if not os.path.exists(file_path):
                error_msg = f"파일이 존재하지 않습니다: {file_path}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # 문서 처리기로 텍스트 추출
            title, contents = self.doc_processor.process_document(file_path)
            logger.info(f"문서 '{title}' 텍스트 추출 완료 ({len(contents)} 부분)")
            
            # 내용이 없으면 오류 반환
            if not contents:
                error_msg = f"문서 '{title}'에서 추출된 텍스트가 없습니다."
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # 텍스트 결합 및 청크 분할
            combined_text = "\n\n".join(contents)
            chunks = self.text_splitter.split_text(combined_text)
            
            if not chunks:
                error_msg = f"문서 '{title}'를 청크로 분할할 수 없습니다."
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
            logger.info(f"문서를 {len(chunks)}개 청크로 분할 완료")
            
            # 청크 임베딩
            embeddings = self.embedding_model.embed_texts(chunks)
            logger.info(f"청크 임베딩 완료 (차원: {embeddings.shape})")
            
            # 벡터 DB에 문서 추가
            doc_id = self.vector_db.add_document(
                title=title,
                file_path=file_path,
                chunks=chunks,
                embeddings=embeddings
            )
            
            logger.info(f"문서 '{title}' 처리 및 저장 완료 (ID: {doc_id}, 청크 수: {len(chunks)})")
            
            return {
                "success": True,
                "doc_id": doc_id,
                "title": title,
                "chunk_count": len(chunks),
                "embedding_dim": embeddings.shape[1]
            }
            
        except Exception as e:
            error_msg = f"문서 처리 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def query(self, 
             query_text: str, 
             top_k: int = 5,
             system_prompt: Optional[str] = None,
             llm_service: Optional[str] = None) -> Dict[str, Any]:
        """
        쿼리를 처리하여 관련 문서를 검색하고 LLM으로 응답 생성
        
        Args:
            query_text (str): 사용자 질의 텍스트
            top_k (int): 검색할 최대 결과 수 (기본값: 5)
            system_prompt (Optional[str]): 시스템 프롬프트 (기본값: None)
            llm_service (Optional[str]): 사용할 LLM 서비스 (기본값: None, 현재 설정된 서비스 사용)
            
        Returns:
            Dict[str, Any]: 쿼리 결과 (성공 여부, 응답 텍스트, 참조 문서 등)
        """
        try:
            # 사용할 LLM 서비스 결정
            if llm_service is None:
                llm_service = self.current_llm_service
            else:
                # 서비스 변경 시 현재 서비스 업데이트
                self.current_llm_service = llm_service
                
            logger.info(f"쿼리 처리 시작: '{query_text[:50]}...' (서비스: {llm_service})")
            
            # 질의 임베딩
            query_embedding = self.embedding_model.embed_query(query_text)
            logger.debug(f"쿼리 임베딩 완료 (차원: {query_embedding.shape})")
            
            # 벡터 DB에서 유사한 청크 검색
            search_results = self.vector_db.search(query_embedding, top_k=top_k)
            
            # 검색 결과가 없는 경우
            if not search_results:
                logger.warning("검색 결과가 없습니다.")
                
                # 그래도 LLM에 질의는 전송 (검색 결과 없이)
                if system_prompt:
                    prompt = f"{system_prompt}\n\n질문: {query_text}"
                else:
                    prompt = f"질문: {query_text}"
                
                llm_response = await self.llm_connector.generate_response(
                    prompt=prompt,
                    llm_service=llm_service
                )
                
                return {
                    "success": True,
                    "query": query_text,
                    "answer": llm_response,
                    "references": [],
                    "search_results": [],
                    "model_info": self.llm_connector.get_model_info(llm_service)
                }
                
            logger.info(f"검색 결과: {len(search_results)} 개 청크 찾음")
            
            # 참조 문서 정보 수집
            references = self._collect_references(search_results)
            
            # 컨텍스트 구성
            context = self._build_context(search_results)
            
            # LLM 프롬프트 구성
            if system_prompt:
                # 시스템 프롬프트가 있는 경우
                prompt = self._build_rag_prompt_with_system(
                    query=query_text,
                    context=context,
                    system_prompt=system_prompt
                )
            else:
                # 시스템 프롬프트가 없는 경우
                prompt = self._build_rag_prompt(
                    query=query_text,
                    context=context
                )
                
            logger.debug(f"LLM 프롬프트 구성 완료 (길이: {len(prompt)}자)")
            
            # LLM 응답 생성
            llm_response = await self.llm_connector.generate_response(
                prompt=prompt,
                llm_service=llm_service
            )
            
            logger.info("LLM 응답 생성 완료")
            
            return {
                "success": True,
                "query": query_text,
                "answer": llm_response,
                "references": references,
                "search_results": search_results,
                "model_info": self.llm_connector.get_model_info(llm_service)
            }
            
        except Exception as e:
            error_msg = f"쿼리 처리 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "query": query_text,
                "error": error_msg
            }
    
    async def query_stream(self,
                     query_text: str,
                     top_k: int = 5,
                     system_prompt: Optional[str] = None,
                     llm_service: Optional[str] = None):
        """
        스트리밍 방식으로 쿼리를 처리하여 관련 문서를 검색하고 LLM으로 응답 생성
        
        Args:
            query_text (str): 사용자 질의 텍스트
            top_k (int): 검색할 최대 결과 수 (기본값: 5)
            system_prompt (Optional[str]): 시스템 프롬프트 (기본값: None)
            llm_service (Optional[str]): 사용할 LLM 서비스 (기본값: None, 현재 설정된 서비스 사용)
            
        Yields:
            str: 응답 토큰
        """
        try:
            # 사용할 LLM 서비스 결정
            if llm_service is None:
                llm_service = self.current_llm_service
            else:
                # 서비스 변경 시 현재 서비스 업데이트
                self.current_llm_service = llm_service
                
            logger.info(f"스트리밍 쿼리 처리 시작: '{query_text[:50]}...' (서비스: {llm_service})")
            
            # 질의 임베딩
            query_embedding = self.embedding_model.embed_query(query_text)
            
            # 벡터 DB에서 유사한 청크 검색
            search_results = self.vector_db.search(query_embedding, top_k=top_k)
            
            # 검색 결과가 없는 경우
            if not search_results:
                logger.warning("검색 결과가 없습니다.")
                
                # 그래도 LLM에 질의는 전송 (검색 결과 없이)
                if system_prompt:
                    prompt = f"{system_prompt}\n\n질문: {query_text}"
                else:
                    prompt = f"질문: {query_text}"
                
                async for token in self.llm_connector.generate_stream_response(
                    prompt=prompt,
                    llm_service=llm_service
                ):
                    yield token
                    
                return
                
            # 참조 문서 정보 수집
            references = self._collect_references(search_results)
            
            # 컨텍스트 구성
            context = self._build_context(search_results)
            
            # LLM 프롬프트 구성
            if system_prompt:
                # 시스템 프롬프트가 있는 경우
                prompt = self._build_rag_prompt_with_system(
                    query=query_text,
                    context=context,
                    system_prompt=system_prompt
                )
            else:
                # 시스템 프롬프트가 없는 경우
                prompt = self._build_rag_prompt(
                    query=query_text,
                    context=context
                )
                
            # LLM 스트리밍 응답 생성
            async for token in self.llm_connector.generate_stream_response(
                prompt=prompt,
                llm_service=llm_service
            ):
                yield token
                
        except Exception as e:
            error_msg = f"스트리밍 쿼리 처리 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            yield f"오류: {error_msg}"
    
    def get_available_llm_services(self) -> List[str]:
        """
        사용 가능한 LLM 서비스 목록을 반환합니다.
        
        Returns:
            List[str]: 사용 가능한 LLM 서비스 목록
        """
        return self.llm_connector.get_available_services()
    
    def set_llm_service(self, service_name: str) -> bool:
        """
        사용할 LLM 서비스를 설정합니다.
        
        Args:
            service_name (str): 설정할 LLM 서비스 이름
            
        Returns:
            bool: 설정 성공 여부
        """
        available_services = self.get_available_llm_services()
        if service_name in available_services:
            self.current_llm_service = service_name
            logger.info(f"LLM 서비스를 '{service_name}'(으)로 변경했습니다.")
            return True
        else:
            logger.error(f"'{service_name}' 서비스를 사용할 수 없습니다.")
            return False
    
    def get_current_llm_service(self) -> str:
        """
        현재 설정된 LLM 서비스 이름을 반환합니다.
        
        Returns:
            str: 현재 LLM 서비스 이름
        """
        return self.current_llm_service
    
    def _collect_references(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        참조 문서 정보를 수집합니다.
        
        Args:
            search_results (List[Dict[str, Any]]): 검색 결과
        
        Returns:
            List[Dict[str, Any]]: 참조 문서 정보 목록
        """
        references = []
        for result in search_results:
            chunk_id = result["chunk_id"]
            doc_id = result["doc_id"]
            
            # 전체 청크 정보 가져오기
            chunk_info = self.vector_db.get_chunk_by_id(chunk_id)
            doc_info = self.vector_db.get_document_by_id(doc_id)
            
            if chunk_info and doc_info:
                # 실제 전체 텍스트가 메타데이터에 없을 수 있음 (미리보기만 저장했을 수 있음)
                chunk_text = chunk_info.get("text", "")
                
                # 참조 문서 정보 추가
                reference = {
                    "doc_id": doc_id,
                    "title": doc_info.get("title", f"문서 {doc_id}"),
                    "similarity": result["similarity"],
                    "preview": chunk_text[:100] + ("..." if len(chunk_text) > 100 else "")
                }
                
                # 중복 제거 (같은 문서는 한 번만 참조에 포함)
                if not any(ref["doc_id"] == doc_id for ref in references):
                    references.append(reference)
        
        return references
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """
        컨텍스트를 구성합니다.
        
        Args:
            search_results (List[Dict[str, Any]]): 검색 결과
        
        Returns:
            List[str]: 컨텍스트 목록
        """
        context = []
        for result in search_results:
            chunk_id = result["chunk_id"]
            doc_id = result["doc_id"]
            
            # 전체 청크 정보 가져오기
            chunk_info = self.vector_db.get_chunk_by_id(chunk_id)
            doc_info = self.vector_db.get_document_by_id(doc_id)
            
            if chunk_info and doc_info:
                # 실제 전체 텍스트가 메타데이터에 없을 수 있음 (미리보기만 저장했을 수 있음)
                chunk_text = chunk_info.get("text", "")
                
                # 컨텍스트에 추가
                context.append(chunk_text)
        
        return context
    
    def _build_rag_prompt(self, query: str, context: List[str]) -> str:
        """
        RAG 프롬프트를 구성합니다.
        
        Args:
            query (str): 질의 텍스트
            context (List[str]): 컨텍스트 목록
        
        Returns:
            str: RAG 프롬프트
        """
        prompt = f"질문: {query}\n\n"
        for i, ctx in enumerate(context):
            prompt += f"문서 {i+1}:\n{ctx}\n\n"
        
        return prompt
    
    def _build_rag_prompt_with_system(self, query: str, context: List[str], system_prompt: str) -> str:
        """
        시스템 프롬프트가 있는 RAG 프롬프트를 구성합니다.
        
        Args:
            query (str): 질의 텍스트
            context (List[str]): 컨텍스트 목록
            system_prompt (str): 시스템 프롬프트
        
        Returns:
            str: RAG 프롬프트
        """
        prompt = f"{system_prompt}\n\n질문: {query}\n\n"
        for i, ctx in enumerate(context):
            prompt += f"문서 {i+1}:\n{ctx}\n\n"
        
        return prompt
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """
        등록된 모든 문서 목록 조회
        
        Returns:
            List[Dict[str, Any]]: 문서 목록
        """
        try:
            docs = self.vector_db.get_all_documents()
            
            # 문서 목록 구성
            doc_list = []
            for doc_id, doc_info in docs.items():
                doc_list.append({
                    "doc_id": doc_id,
                    "title": doc_info.get("title", f"문서 {doc_id}"),
                    "file_path": doc_info.get("file_path", ""),
                    "chunk_count": doc_info.get("chunk_count", 0),
                    "created_at": doc_info.get("created_at", "")
                })
            
            return doc_list
            
        except Exception as e:
            logger.error(f"문서 목록 조회 중 오류 발생: {str(e)}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """
        문서 삭제
        
        Args:
            doc_id (str): 삭제할 문서 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            return self.vector_db.delete_document(doc_id)
        except Exception as e:
            logger.error(f"문서 삭제 중 오류 발생: {str(e)}")
            return False
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        RAG 엔진 정보 조회
        
        Returns:
            Dict[str, Any]: 엔진 정보
        """
        return {
            "embedding_model": self.embedding_model.model_name,
            "llm_service": self.current_llm_service,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }
