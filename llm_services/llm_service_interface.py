"""
LLM 서비스 인터페이스 모듈
"""
from abc import ABC, abstractmethod
from typing import Dict, Generator, Any, Optional


class ILLMService(ABC):
    """
    LLM 서비스 인터페이스
    모든 LLM 서비스 구현체는 이 인터페이스를 구현해야 합니다.
    """
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        프롬프트에 대한 응답을 생성합니다.
        
        Args:
            prompt (str): LLM에 전달할 프롬프트
            
        Returns:
            str: LLM 응답 텍스트
        """
        pass
    
    @abstractmethod
    def generate_stream_response(self, prompt: str) -> Generator[str, None, None]:
        """
        프롬프트에 대한 스트리밍 응답을 생성합니다.
        
        Args:
            prompt (str): LLM에 전달할 프롬프트
            
        Returns:
            Generator[str, None, None]: 응답 토큰을 생성하는 제너레이터
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        서비스가 사용 가능한지 확인합니다.
        
        Returns:
            bool: 서비스 사용 가능 여부
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        모델 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 모델 정보
        """
        pass
