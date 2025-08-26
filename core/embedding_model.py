"""
임베딩 모델 모듈 - 문서와 질의를 벡터로 변환
"""
import os
import logging
from typing import List, Dict, Optional, Union, Any
import numpy as np
import torch
from pathlib import Path
import shutil
import tempfile

# Sentence Transformers 및 Hugging Face
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings

# 내부 모듈
from utils.common import setup_logger, get_project_root

# 로거 설정
logger = setup_logger(
    "embedding_model", 
    os.path.join(get_project_root(), "logs", "embedding_model.log")
)

# 기본 임베딩 모델 설정
DEFAULT_MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v2"
DEFAULT_MODEL_PATH = os.path.join(get_project_root(), "embedding_model")

class EmbeddingModel:
    """
    임베딩 모델 클래스 - 텍스트를 벡터로 변환
    """
    
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        """
        임베딩 모델 초기화
        
        Args:
            model_name (str, optional): 사용할 모델 이름 또는 경로
                기본값: "sentence-transformers/distiluse-base-multilingual-cased-v2"
        """
        try:
            # 모델 저장 경로 설정
            model_folder_name = model_name.replace("/", "-")
            self.local_model_path = os.path.join(DEFAULT_MODEL_PATH, model_folder_name)
            
            logger.info(f"임베딩 모델 '{model_name}' 로딩 준비 중...")
            
            # GPU 가용성 확인
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"사용 장치: {self.device}")
            
            # 모델 로딩 시도
            self._load_model(model_name)
            
            logger.info(f"임베딩 모델 로딩 완료 (차원: {self.embedding_dim})")
            
        except Exception as e:
            error_msg = f"임베딩 모델 초기화 오류: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _load_model(self, model_name: str):
        """
        모델을 로딩하는 내부 함수
        모델이 로컬에 없다면 다운로드 후 저장
        
        Args:
            model_name (str): 모델 이름 또는 경로
        """
        try:
            # 로컬에 모델이 있는지 확인
            if os.path.exists(self.local_model_path):
                logger.info(f"로컬 저장소에서 모델 로딩: {self.local_model_path}")
                self.model = SentenceTransformer(self.local_model_path, device=self.device)
                self.model_name = model_name
            else:
                # 로컬에 없으면 온라인에서 다운로드 후 저장
                logger.info(f"온라인에서 모델 다운로드 중: {model_name}")
                # 디렉토리 생성
                os.makedirs(DEFAULT_MODEL_PATH, exist_ok=True)
                
                # 모델 다운로드
                self.model = SentenceTransformer(model_name, device=self.device)
                self.model_name = model_name
                
                # 모델 저장
                logger.info(f"모델을 로컬에 저장 중: {self.local_model_path}")
                self.model.save(self.local_model_path)
                logger.info(f"모델이 성공적으로 저장됨: {self.local_model_path}")
            
            # 임베딩 차원 정보 저장
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            
            # 테스트 임베딩 생성
            test_embedding = self.model.encode("테스트 문장")
            logger.info(f"테스트 임베딩 생성 완료: 차원={len(test_embedding)}")
            
        except Exception as e:
            logger.error(f"모델 로딩 오류: {str(e)}")
            raise

    def get_embedding_dim(self) -> int:
        """
        임베딩 차원 반환
        
        Returns:
            int: 임베딩 벡터의 차원
        """
        return self.embedding_dim

    def embed_texts(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        텍스트 또는 텍스트 목록을 임베딩 벡터로 변환
        
        Args:
            texts (Union[str, List[str]]): 임베딩할 텍스트 또는 텍스트 목록
            
        Returns:
            np.ndarray: 임베딩 벡터 배열
        """
        # 단일 텍스트의 경우 리스트로 변환
        if isinstance(texts, str):
            texts = [texts]
            
        if not texts:
            logger.warning("임베딩할 텍스트가 없습니다.")
            return np.array([])
            
        try:
            logger.debug(f"{len(texts)}개 텍스트 임베딩 시작")
            
            # 배치 크기 설정 (메모리 고려)
            batch_size = 32
            all_embeddings = []
            
            # 배치 처리
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                embeddings = self.model.encode(batch, convert_to_numpy=True)
                all_embeddings.append(embeddings)
                
                logger.debug(f"배치 {i//batch_size + 1} 임베딩 완료 ({len(batch)}개 텍스트)")
            
            # 모든 배치 결합
            combined_embeddings = np.vstack(all_embeddings)
            
            logger.debug(f"임베딩 완료: {combined_embeddings.shape}")
            return combined_embeddings
            
        except Exception as e:
            error_msg = f"텍스트 임베딩 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        단일 텍스트를 임베딩 벡터로 변환
        
        Args:
            text (str): 임베딩할 텍스트
            
        Returns:
            np.ndarray: 임베딩 벡터
        """
        return self.embed_texts([text])[0]
    
    def get_embedding(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        텍스트 또는 텍스트 목록을 임베딩 벡터로 변환 (embed_texts의 별칭)
        
        Args:
            texts (Union[str, List[str]]): 임베딩할 텍스트 또는 텍스트 목록
            
        Returns:
            np.ndarray: 임베딩 벡터 배열
        """
        return self.embed_texts(texts)
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        단일 쿼리 텍스트를 임베딩 벡터로 변환
        
        Args:
            query (str): 임베딩할 쿼리 텍스트
            
        Returns:
            np.ndarray: 임베딩 벡터 (shape: [1, 임베딩 차원])
        """
        if not query.strip():
            logger.warning("임베딩할 쿼리가 비어 있습니다.")
            return np.zeros((1, self.embedding_dim))
            
        try:
            logger.debug(f"쿼리 임베딩 시작: '{query[:50]}...'")
            
            # 쿼리 임베딩
            embedding = self.model.encode([query], convert_to_numpy=True)
            
            logger.debug(f"쿼리 임베딩 완료: {embedding.shape}")
            return embedding
            
        except Exception as e:
            error_msg = f"쿼리 임베딩 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        현재 임베딩 모델의 정보 반환
        
        Returns:
            Dict[str, Any]: 모델 정보
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "device": self.device
        }
