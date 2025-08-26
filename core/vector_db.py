"""
벡터 데이터베이스 관리 모듈 - FAISS를 사용한 벡터 저장 및 검색
"""
import os
import json
import shutil
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import faiss
import pickle

# 내부 모듈
from utils.common import setup_logger, get_project_root, get_timestamp

# 로거 설정
logger = setup_logger(
    "vector_db", 
    os.path.join(get_project_root(), "logs", "vector_db.log")
)

class VectorDB:
    """
    벡터 데이터베이스 관리 클래스 - FAISS를 이용한 벡터 저장 및 검색
    """
    
    def __init__(self, db_path: Optional[str] = None, dimension: int = 768):
        """
        벡터 데이터베이스 초기화
        
        Args:
            db_path (Optional[str]): 벡터 DB 저장 경로. 
                None인 경우 기본 경로 사용 (data/vector_db)
            dimension (int): 벡터 차원 (기본값: 768)
        """
        # 기본 경로 설정
        if db_path is None:
            self.db_path = os.path.join(get_project_root(), "data", "vector_db")
        else:
            self.db_path = db_path
            
        # 디렉토리 생성
        os.makedirs(self.db_path, exist_ok=True)
        
        # 인덱스 파일 경로
        self.index_path = os.path.join(self.db_path, "faiss_index.bin")
        self.metadata_path = os.path.join(self.db_path, "metadata.json")
        
        # 차원 저장
        self.dimension = dimension
        
        # 메타데이터 및 인덱스 초기화/로드
        self._init_db()
        
        logger.info(f"벡터 DB 초기화 완료 (경로: {self.db_path}, 차원: {self.dimension})")
    
    def _init_db(self):
        """
        벡터 DB 초기화 또는 로드
        """
        # 메타데이터 초기화
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                logger.info(f"메타데이터 로드 완료: {len(self.metadata['documents'])}개 문서")
            except Exception as e:
                logger.error(f"메타데이터 로드 오류: {str(e)}")
                self._create_new_metadata()
        else:
            self._create_new_metadata()
        
        # FAISS 인덱스 초기화
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                logger.info(f"FAISS 인덱스 로드 완료: {self.index.ntotal}개 벡터")
                
                # 차원이 메타데이터와 일치하는지 확인
                if self.index.d != self.dimension:
                    logger.warning(
                        f"로드된 인덱스의 차원({self.index.d})이 설정된 차원({self.dimension})과 다릅니다. "
                        "로드된 인덱스의 차원을 사용합니다."
                    )
                    self.dimension = self.index.d
            except Exception as e:
                logger.error(f"FAISS 인덱스 로드 오류: {str(e)}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_metadata(self):
        """
        새 메타데이터 생성
        """
        self.metadata = {
            "documents": {},  # 문서 정보 (ID: {제목, 파일경로, 등록일시 등})
            "chunks": {},     # 청크 정보 (ID: {문서ID, 내용, 인덱스 등})
            "next_doc_id": 1,
            "next_chunk_id": 1
        }
        
        # 메타데이터 저장
        self._save_metadata()
        logger.info("새 메타데이터 생성 완료")
    
    def _create_new_index(self):
        """
        새 FAISS 인덱스 생성
        """
        # L2 거리 측정 기반 인덱스 생성
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # 인덱스 저장
        faiss.write_index(self.index, self.index_path)
        logger.info(f"새 FAISS 인덱스 생성 완료 (차원: {self.dimension})")
    
    def _save_metadata(self):
        """
        메타데이터 저장
        """
        try:
            # 백업 생성
            if os.path.exists(self.metadata_path):
                backup_path = f"{self.metadata_path}.{get_timestamp()}.bak"
                shutil.copy2(self.metadata_path, backup_path)
                logger.debug(f"메타데이터 백업 생성: {backup_path}")
            
            # 메타데이터 저장
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                
            logger.debug("메타데이터 저장 완료")
        except Exception as e:
            logger.error(f"메타데이터 저장 중 오류 발생: {str(e)}")
    
    def _save_index(self):
        """
        FAISS 인덱스 저장
        """
        try:
            # 백업 생성
            if os.path.exists(self.index_path):
                backup_path = f"{self.index_path}.{get_timestamp()}.bak"
                shutil.copy2(self.index_path, backup_path)
                logger.debug(f"인덱스 백업 생성: {backup_path}")
            
            # 인덱스 저장
            faiss.write_index(self.index, self.index_path)
            logger.debug(f"FAISS 인덱스 저장 완료 ({self.index.ntotal}개 벡터)")
        except Exception as e:
            logger.error(f"인덱스 저장 중 오류 발생: {str(e)}")
    
    def add_document(self, 
                    title: str, 
                    file_path: str, 
                    chunks: List[str], 
                    embeddings: np.ndarray) -> int:
        """
        문서와 해당 청크들을 벡터 DB에 추가
        
        Args:
            title (str): 문서 제목
            file_path (str): 원본 파일 경로
            chunks (List[str]): 텍스트 청크 목록
            embeddings (np.ndarray): 청크 임베딩 벡터 배열
            
        Returns:
            int: 생성된 문서 ID
        """
        if len(chunks) == 0 or embeddings.shape[0] == 0:
            error_msg = "빈 청크 또는 임베딩이 제공되었습니다."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if len(chunks) != embeddings.shape[0]:
            error_msg = f"청크 수({len(chunks)})와 임베딩 수({embeddings.shape[0]})가 일치하지 않습니다."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            # 새 문서 ID 할당
            doc_id = str(self.metadata["next_doc_id"])
            self.metadata["next_doc_id"] += 1
            
            # 문서 메타데이터 추가
            self.metadata["documents"][doc_id] = {
                "title": title,
                "file_path": file_path,
                "chunk_count": len(chunks),
                "created_at": get_timestamp()
            }
            
            # 청크 벡터 FAISS에 추가
            self.index.add(embeddings)
            
            # 청크 메타데이터 추가
            chunk_ids = []
            for i, chunk_text in enumerate(chunks):
                chunk_id = str(self.metadata["next_chunk_id"])
                self.metadata["next_chunk_id"] += 1
                
                # 청크 메타데이터 저장
                self.metadata["chunks"][chunk_id] = {
                    "doc_id": doc_id,
                    "index": i,
                    "vector_index": self.index.ntotal - len(chunks) + i,
                    "text": chunk_text[:200] + ("..." if len(chunk_text) > 200 else ""),  # 미리보기만 저장
                    "created_at": get_timestamp()
                }
                chunk_ids.append(chunk_id)
            
            # 문서에 청크 ID 목록 추가
            self.metadata["documents"][doc_id]["chunk_ids"] = chunk_ids
            
            # 저장
            self._save_metadata()
            self._save_index()
            
            logger.info(f"문서 '{title}' 추가 완료 (ID: {doc_id}, 청크 수: {len(chunks)})")
            return int(doc_id)
            
        except Exception as e:
            logger.error(f"문서 추가 중 오류 발생: {str(e)}")
            raise
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        쿼리 벡터와 가장 유사한 청크 검색
        
        Args:
            query_vector (np.ndarray): 쿼리 임베딩 벡터
            top_k (int): 검색할 최대 결과 수 (기본값: 5)
            
        Returns:
            List[Dict[str, Any]]: 유사도 상위 청크 정보 및 메타데이터
        """
        if self.index.ntotal == 0:
            logger.warning("검색할 벡터가 없습니다.")
            return []
            
        try:
            # 벡터가 2D 배열이 아니면 변환
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
            
            # 상위 K개 검색
            distances, indices = self.index.search(query_vector, top_k)
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                # 잘못된 인덱스 건너뛰기
                if idx == -1:
                    continue
                
                # 해당 벡터 인덱스를 가진 청크 찾기
                chunk_id = None
                chunk_info = None
                
                for c_id, c_info in self.metadata["chunks"].items():
                    if c_info["vector_index"] == idx:
                        chunk_id = c_id
                        chunk_info = c_info
                        break
                
                if chunk_id is None:
                    logger.warning(f"인덱스 {idx}에 해당하는 청크 정보를 찾을 수 없습니다.")
                    continue
                
                # 문서 정보 가져오기
                doc_id = chunk_info["doc_id"]
                doc_info = self.metadata["documents"][doc_id]
                
                # 결과 추가
                results.append({
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "doc_title": doc_info["title"],
                    "chunk_index": chunk_info["index"],
                    "similarity": float(1.0 / (1.0 + distance)),  # 거리를 유사도로 변환
                    "distance": float(distance),
                    "text_preview": chunk_info["text"]
                })
            
            logger.debug(f"쿼리에 대해 {len(results)}개 결과 검색 완료")
            return results
            
        except Exception as e:
            logger.error(f"검색 중 오류 발생: {str(e)}")
            raise
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        ID로 문서 정보 조회
        
        Args:
            doc_id (str): 문서 ID
            
        Returns:
            Optional[Dict[str, Any]]: 문서 정보 (없으면 None)
        """
        doc_id = str(doc_id)  # 문자열로 변환
        return self.metadata["documents"].get(doc_id)
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        ID로 청크 정보 조회
        
        Args:
            chunk_id (str): 청크 ID
            
        Returns:
            Optional[Dict[str, Any]]: 청크 정보 (없으면 None)
        """
        chunk_id = str(chunk_id)  # 문자열로 변환
        return self.metadata["chunks"].get(chunk_id)
    
    def get_all_documents(self) -> Dict[str, Dict[str, Any]]:
        """
        모든 문서 정보 조회
        
        Returns:
            Dict[str, Dict[str, Any]]: 모든 문서 정보 (ID: 문서정보)
        """
        try:
            return self.metadata["documents"]
        except Exception as e:
            logger.error(f"모든 문서 정보 조회 중 오류 발생: {str(e)}")
            return {}
    
    def get_all_chunks(self) -> Dict[str, Dict[str, Any]]:
        """
        모든 청크 정보 조회
        
        Returns:
            Dict[str, Dict[str, Any]]: 모든 청크 정보 (ID: 청크정보)
        """
        try:
            return self.metadata["chunks"]
        except Exception as e:
            logger.error(f"모든 청크 정보 조회 중 오류 발생: {str(e)}")
            return {}
    
    def delete_document(self, doc_id: str) -> bool:
        """
        문서와 관련된 모든 청크 삭제
        
        Args:
            doc_id (str): 삭제할 문서 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        doc_id = str(doc_id)  # 문자열로 변환
        
        if doc_id not in self.metadata["documents"]:
            logger.warning(f"문서 ID {doc_id}가 존재하지 않습니다.")
            return False
            
        try:
            # 문서에 속한 청크 ID 목록 가져오기
            chunk_ids = self.metadata["documents"][doc_id].get("chunk_ids", [])
            
            # 벡터 인덱스 목록 구성
            vector_indices = []
            for chunk_id in chunk_ids:
                if chunk_id in self.metadata["chunks"]:
                    vector_idx = self.metadata["chunks"][chunk_id].get("vector_index")
                    if vector_idx is not None:
                        vector_indices.append(vector_idx)
                    
                    # 청크 메타데이터 삭제
                    del self.metadata["chunks"][chunk_id]
            
            # 현재 FAISS는 벡터 삭제를 직접 지원하지 않으므로 재구성 필요
            # 이 부분은 간단한 구현을 위해 새 인덱스를 만들고 유지할 벡터만 복사
            if vector_indices:
                logger.info(f"문서 {doc_id} 삭제로 인한 인덱스 재구성 시작...")
                
                # 전체 벡터 수
                total_vectors = self.index.ntotal
                
                # 유지할 벡터 인덱스 구성 (삭제할 것 제외)
                keep_indices = [i for i in range(total_vectors) if i not in vector_indices]
                
                if keep_indices:
                    # 유지할 벡터만 가져오기
                    keep_vectors = np.zeros((len(keep_indices), self.index.d), dtype=np.float32)
                    for new_idx, old_idx in enumerate(keep_indices):
                        # FAISS는 직접 벡터 접근을 제공하지 않으므로 검색으로 가져옴
                        # 정확히 일치하는 벡터를 찾기 위해 해당 인덱스 벡터로 검색
                        original_vec = np.array([[0.0] * self.index.d], dtype=np.float32)
                        self.index.reconstruct(old_idx, original_vec.reshape(-1))
                        keep_vectors[new_idx] = original_vec
                    
                    # 청크 메타데이터의 벡터 인덱스 업데이트
                    index_mapping = {old_idx: new_idx for new_idx, old_idx in enumerate(keep_indices)}
                    for chunk_id, chunk_info in self.metadata["chunks"].items():
                        old_idx = chunk_info["vector_index"]
                        if old_idx in index_mapping:
                            chunk_info["vector_index"] = index_mapping[old_idx]
                    
                    # 새 인덱스 생성 및 벡터 추가
                    new_index = faiss.IndexFlatL2(self.index.d)
                    new_index.add(keep_vectors)
                    self.index = new_index
                else:
                    # 유지할 벡터가 없으면 빈 인덱스로 초기화
                    self._create_new_index()
            
            # 문서 메타데이터 삭제
            del self.metadata["documents"][doc_id]
            
            # 변경사항 저장
            self._save_metadata()
            self._save_index()
            
            logger.info(f"문서 ID {doc_id} 및 관련 청크 {len(chunk_ids)}개 삭제 완료")
            return True
            
        except Exception as e:
            logger.error(f"문서 삭제 중 오류 발생: {str(e)}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        벡터 DB 통계 정보 조회
        
        Returns:
            Dict[str, Any]: DB 통계 정보
        """
        try:
            doc_count = len(self.metadata["documents"])
            chunk_count = len(self.metadata["chunks"])
            vector_count = self.index.ntotal
            
            return {
                "document_count": doc_count,
                "chunk_count": chunk_count,
                "vector_count": vector_count,
                "dimension": self.dimension,
                "db_path": self.db_path
            }
        except Exception as e:
            logger.error(f"통계 정보 조회 중 오류 발생: {str(e)}")
            return {"error": str(e)}
    
    def save_index(self):
        """
        FAISS 인덱스와 메타데이터를 저장합니다.
        
        외부에서 호출 가능한 공개 메서드입니다.
        """
        logger.info("인덱스 및 메타데이터 저장 시작")
        self._save_metadata()
        self._save_index()
        logger.info("인덱스 및 메타데이터 저장 완료")
