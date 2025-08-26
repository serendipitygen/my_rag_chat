"""
Google Gemini API 서비스 구현 모듈
"""
import logging
import os
from typing import Dict, Generator, Any, Optional

import google.generativeai as genai
from google.generativeai.types import generation_types

from .llm_service_interface import ILLMService


class GeminiService(ILLMService):
    """
    Google Gemini API 서비스 구현
    """
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro", logger: Optional[logging.Logger] = None):
        """
        Gemini 서비스 초기화
        
        Args:
            api_key (str): Gemini API 키
            model (str, optional): 사용할 모델 이름. 기본값은 "gemini-1.5-pro"
            logger (Optional[logging.Logger], optional): 로거. 기본값은 None
        """
        self.api_key = api_key
        self.model = model
        self.logger = logger or logging.getLogger(__name__)
        
        # API 키 설정
        genai.configure(api_key=self.api_key)
        
        # 모델 설정
        try:
            self.model_instance = genai.GenerativeModel(model_name=self.model)
        except Exception as e:
            self.logger.error(f"Gemini 모델 초기화 중 오류 발생: {str(e)}")
            self.model_instance = None
    
    def generate_response(self, prompt: str) -> str:
        """
        프롬프트에 대한 응답을 생성합니다.
        
        Args:
            prompt (str): LLM에 전달할 프롬프트
            
        Returns:
            str: LLM 응답 텍스트
        """
        try:
            if not self.model_instance:
                return "오류: Gemini 모델이 초기화되지 않았습니다."
            
            # 응답 생성
            response = self.model_instance.generate_content(prompt)
            
            # 응답 검증 및 반환
            if hasattr(response, 'text'):
                return response.text
            else:
                return "응답 처리 중 오류가 발생했습니다."
            
        except Exception as e:
            error_msg = f"Gemini 응답 생성 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            return f"오류: {error_msg}"
    
    def generate_stream_response(self, prompt: str) -> Generator[Any, None, None]:
        """
        프롬프트에 대한 스트리밍 응답을 생성합니다.
        
        Args:
            prompt (str): LLM에 전달할 프롬프트
            
        Returns:
            Generator[Any, None, None]: 응답 청크를 생성하는 제너레이터
        """
        try:
            if not self.model_instance:
                yield "오류: Gemini 모델이 초기화되지 않았습니다."
                return
            
            # 스트리밍 응답 생성
            response = self.model_instance.generate_content(
                prompt,
                stream=True
            )
            
            # 청크 단위로 응답 처리 (청크 자체를 yield)
            for chunk in response:
                yield chunk
                    
        except Exception as e:
            error_msg = f"Gemini 스트리밍 응답 생성 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            yield f"오류: {error_msg}"
    
    def is_available(self) -> bool:
        """
        Gemini API가 사용 가능한지 확인합니다.
        
        Returns:
            bool: 서비스 사용 가능 여부
        """
        try:
            if not self.model_instance:
                return False
                
            # 간단한 프롬프트로 API 테스트
            test_response = self.model_instance.generate_content("안녕하세요")
            return hasattr(test_response, 'text')
            
        except Exception as e:
            self.logger.error(f"Gemini API 연결 확인 중 오류 발생: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        모델 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 모델 정보
        """
        return {
            "name": self.model,
            "provider": "Google",
            "description": "Google의 Gemini AI 모델",
            "context_window": 32768 if "pro" in self.model else 16384,  # 대략적인 값
            "is_local": False
        }
