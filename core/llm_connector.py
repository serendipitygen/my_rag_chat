"""
LLM 연결 모듈

이 모듈은 LLM 서비스(LM Studio, Gemini 등)와의 연결을 담당합니다.
"""
import os
import sys
import json
import logging
from typing import Dict, List, Generator, AsyncGenerator, Any, Optional

# 상위 디렉토리를 path에 추가하여 import 할 수 있도록 함
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from llm_services.llm_service_factory import LLMServiceFactory
from utils.common import setup_logger


class LLMConnector:
    """
    LLM 연결 모듈
    
    다양한 LLM 서비스와 연결하고 응답을 생성합니다.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        LLM 연결 모듈 초기화
        
        Args:
            config (Dict[str, Any]): 설정 정보
            logger (Optional[logging.Logger], optional): 로거. 기본값은 None
        """
        self.config = config
        self.logger = logger or setup_logger(__name__)
        
        # LLM 서비스 팩토리 초기화
        self.llm_service_factory = LLMServiceFactory(config, self.logger)
        
    async def generate_response(self, prompt: str, llm_service: str = "lm_studio") -> str:
        """
        프롬프트에 대한 응답을 생성합니다.
        
        Args:
            prompt (str): LLM에 전달할 프롬프트
            llm_service (str, optional): 사용할 LLM 서비스 이름. 기본값은 "lm_studio"
            
        Returns:
            str: LLM 응답 텍스트
        """
        try:
            service = self.llm_service_factory.get_service(llm_service)
            if not service:
                return f"오류: {llm_service} 서비스를 사용할 수 없습니다."
                
            response = service.generate_response(prompt)
            return response
            
        except Exception as e:
            error_msg = f"응답 생성 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            return f"오류: {error_msg}"
    
    async def generate_stream_response(self, prompt: str, llm_service: str = "lm_studio") -> AsyncGenerator[str, None]:
        """
        프롬프트에 대한 스트리밍 응답을 생성합니다.
        
        Args:
            prompt (str): LLM에 전달할 프롬프트
            llm_service (str, optional): 사용할 LLM 서비스 이름. 기본값은 "lm_studio"
            
        Yields:
            str: 응답 토큰
        """
        try:
            service = self.llm_service_factory.get_service(llm_service)
            if not service:
                yield f"오류: {llm_service} 서비스를 사용할 수 없습니다."
                return
                
            for chunk in service.generate_stream_response(prompt):
                yield chunk
                
        except Exception as e:
            error_msg = f"스트리밍 응답 생성 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            yield f"오류: {error_msg}"
    
    def is_api_available(self, llm_service: str = "lm_studio") -> bool:
        """
        지정된 LLM 서비스가 사용 가능한지 확인합니다.
        
        Args:
            llm_service (str, optional): 확인할 LLM 서비스 이름. 기본값은 "lm_studio"
            
        Returns:
            bool: 서비스 사용 가능 여부
        """
        service = self.llm_service_factory.get_service(llm_service)
        if not service:
            return False
            
        return service.is_available()
    
    def get_model_info(self, llm_service: str = "lm_studio") -> Dict[str, Any]:
        """
        지정된 LLM 서비스의 모델 정보를 반환합니다.
        
        Args:
            llm_service (str, optional): 정보를 조회할 LLM 서비스 이름. 기본값은 "lm_studio"
            
        Returns:
            Dict[str, Any]: 모델 정보
        """
        service = self.llm_service_factory.get_service(llm_service)
        if not service:
            return {"error": f"서비스를 찾을 수 없습니다: {llm_service}"}
            
        return service.get_model_info()
    
    def get_available_services(self) -> List[str]:
        """
        사용 가능한 모든 LLM 서비스 목록을 반환합니다.
        
        Returns:
            List[str]: 사용 가능한 서비스 이름 목록
        """
        return self.llm_service_factory.list_available_services()
