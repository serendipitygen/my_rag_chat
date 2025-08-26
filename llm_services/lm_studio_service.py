"""
LM Studio API 서비스 구현 모듈
"""
import json
import logging
import requests
from typing import Dict, Generator, Any, Optional

from .llm_service_interface import ILLMService


class LMStudioService(ILLMService):
    """
    LM Studio API 서비스 구현
    """
    
    def __init__(self, api_base_url: str, api_key: str = "", logger: Optional[logging.Logger] = None):
        """
        LM Studio 서비스 초기화
        
        Args:
            api_base_url (str): API 기본 URL (예: http://localhost:1234/v1)
            api_key (str, optional): API 키 (필요한 경우). 기본값은 빈 문자열
            logger (Optional[logging.Logger], optional): 로거. 기본값은 None
        """
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.logger = logger or logging.getLogger(__name__)
        self.model = "LM Studio Model"  # LM Studio에서는 모델 이름이 고정되지 않을 수 있음
        
    def generate_response(self, prompt: str) -> str:
        """
        프롬프트에 대한 응답을 생성합니다.
        
        Args:
            prompt (str): LLM에 전달할 프롬프트
            
        Returns:
            str: LLM 응답 텍스트
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"LM Studio API 요청 실패: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return f"오류: {error_msg}"
                
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
            
        except Exception as e:
            error_msg = f"LM Studio 응답 생성 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            return f"오류: {error_msg}"
    
    def generate_stream_response(self, prompt: str) -> Generator[str, None, None]:
        """
        프롬프트에 대한 스트리밍 응답을 생성합니다.
        
        Args:
            prompt (str): LLM에 전달할 프롬프트
            
        Returns:
            Generator[str, None, None]: 응답 토큰을 생성하는 제너레이터
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
                "stream": True
            }
            
            response = requests.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"LM Studio API 스트리밍 요청 실패: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                yield f"오류: {error_msg}"
                return
                
            # 스트리밍 응답 처리
            for line in response.iter_lines():
                if not line:
                    continue
                    
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    line = line[6:]  # 'data: ' 부분 제거
                    
                    if line == "[DONE]":
                        break
                        
                    try:
                        data = json.loads(line)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                content = delta['content']
                                yield content
                    except json.JSONDecodeError as e:
                        self.logger.error(f"JSON 파싱 오류: {str(e)} - {line}")
                        continue
                        
        except Exception as e:
            error_msg = f"LM Studio 스트리밍 응답 생성 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            yield f"오류: {error_msg}"
    
    def is_available(self) -> bool:
        """
        LM Studio API가 사용 가능한지 확인합니다.
        
        Returns:
            bool: 서비스 사용 가능 여부
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"LM Studio API 연결 확인 중 오류 발생: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        모델 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 모델 정보
        """
        return {
            "name": "LM Studio 모델",
            "provider": "LM Studio",
            "description": "로컬에서 실행 중인 LM Studio 모델",
            "context_window": 4096,  # 기본값, 실제 모델마다 다를 수 있음
            "is_local": True
        }
