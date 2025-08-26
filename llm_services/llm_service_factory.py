"""
LLM 서비스 팩토리 모듈

이 모듈은 다양한 LLM 서비스(LM Studio, Gemini 등)를 생성하고 관리하는 팩토리 클래스를 제공합니다.
"""
import os
import logging
from typing import Dict, List, Optional, Any

from .llm_service_interface import ILLMService
from .lm_studio_service import LMStudioService
from .gemini_service import GeminiService


class LLMServiceFactory:
    """
    LLM 서비스 팩토리
    
    사용 가능한 LLM 서비스를 생성하고 관리합니다.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        LLM 서비스 팩토리 초기화
        
        Args:
            config (Dict[str, Any]): 설정 정보
            logger (Optional[logging.Logger], optional): 로거. 기본값은 None
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.services = {}  # 서비스 인스턴스 캐시
        
    def get_service(self, service_name: str) -> Optional[ILLMService]:
        """
        지정된 이름의 LLM 서비스를 반환합니다.
        
        Args:
            service_name (str): 서비스 이름 ("lm_studio" 또는 "gemini")
            
        Returns:
            Optional[ILLMService]: LLM 서비스 인스턴스 또는 None
        """
        # 이미 생성된 서비스가 있다면 반환
        if service_name in self.services:
            return self.services[service_name]
            
        # 새 서비스 인스턴스 생성
        service = None
        
        if service_name == "lm_studio":
            # LM Studio 서비스 생성
            api_base_url = self.config.get("lm_studio_api_base_url", "http://localhost:1234/v1")
            api_key = self.config.get("lm_studio_api_key", "")
            
            service = LMStudioService(
                api_base_url=api_base_url,
                api_key=api_key,
                logger=self.logger
            )
            
        elif service_name == "gemini":
            # Gemini 서비스 생성
            # 환경 변수에서 API 키를 가져옵니다
            api_key = os.environ.get("GOOGLE_API_KEY", "")
            
            # config에서도 확인
            if not api_key:
                api_key = self.config.get("gemini_api_key", "")
                
            if not api_key:
                self.logger.error("Gemini API 키가 설정되지 않았습니다.")
                return None
                
            model = self.config.get("gemini_model", "gemini-1.5-pro")
            
            service = GeminiService(
                api_key=api_key,
                model=model,
                logger=self.logger
            )
            
        else:
            self.logger.error(f"지원되지 않는 LLM 서비스: {service_name}")
            return None
            
        # 서비스 캐싱
        if service:
            self.services[service_name] = service
            
        return service
        
    def list_available_services(self) -> List[str]:
        """
        사용 가능한 모든 LLM 서비스 목록을 반환합니다.
        
        Returns:
            List[str]: 사용 가능한 서비스 이름 목록
        """
        available_services = []
        
        # LM Studio 서비스 확인
        lm_studio = self.get_service("lm_studio")
        if lm_studio and lm_studio.is_available():
            available_services.append("lm_studio")
            
        # Gemini 서비스 확인
        gemini = self.get_service("gemini")
        if gemini and gemini.is_available():
            available_services.append("gemini")
            
        return available_services
        
    def get_service_info(self, service_name: str) -> Dict[str, Any]:
        """
        서비스 정보를 반환합니다.
        
        Args:
            service_name (str): 서비스 이름
            
        Returns:
            Dict[str, Any]: 서비스 정보
        """
        service = self.get_service(service_name)
        if not service:
            return {"error": f"서비스를 찾을 수 없습니다: {service_name}"}
            
        return service.get_model_info()
