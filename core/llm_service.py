"""
LLM 서비스 연결 모듈 - 외부 대규모 언어 모델 서비스와 통신
"""
import os
import logging
import json
import time
import requests
from typing import List, Dict, Optional, Union, Any, Callable
from pathlib import Path
import openai
from dotenv import load_dotenv

# 내부 모듈
from utils.common import setup_logger, get_project_root

# 로거 설정
logger = setup_logger(
    "llm_service", 
    os.path.join(get_project_root(), "logs", "llm_service.log")
)

# 환경 변수 로드
load_dotenv(os.path.join(get_project_root(), ".env"))

class LLMService:
    """
    대규모 언어 모델(LLM) 서비스 연결 클래스
    OpenAI API 또는 LM Studio를 통한, 로컬 LLM 모델 사용
    """
    
    def __init__(self, 
                provider: str = "lmstudio",
                model: str = "kanana-nano-2.1b-instruct",
                api_key: Optional[str] = None,
                temperature: float = 0.3,
                max_tokens: int = 1024,
                lmstudio_url: str = "http://localhost:4982"):
        """
        LLM 서비스 초기화
        
        Args:
            provider (str): LLM 제공자 (기본값: "lmstudio", 옵션: "openai", "lmstudio")
            model (str): 사용할 모델 (기본값: "kanana-nano-2.1b-instruct")
            api_key (Optional[str]): API 키 (None인 경우 환경 변수에서 로드)
            temperature (float): 응답 무작위성 정도 (0.0-1.0, 기본값: 0.3)
            max_tokens (int): 최대 응답 토큰 수 (기본값: 1024)
            lmstudio_url (str): LM Studio API 서버 URL (기본값: "http://localhost:4982")
        """
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # LM Studio 설정
        self.lmstudio_url = lmstudio_url
        
        # API 키 설정
        if api_key is None:
            if self.provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
            else:
                api_key_var = f"{self.provider.upper()}_API_KEY"
                api_key = os.getenv(api_key_var)
                if not api_key:
                    logger.debug(f"{api_key_var} 환경 변수가 설정되지 않았습니다.")
        
        self.api_key = api_key
        
        # 프로바이더별 초기화
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "lmstudio":
            self._init_lmstudio()
        else:
            logger.warning(f"지원되지 않는 프로바이더입니다: {provider}")
        
        logger.info(f"LLM 서비스 초기화 완료 (프로바이더: {provider}, 모델: {model})")
    
    def _init_openai(self):
        """
        OpenAI API 초기화
        """
        if self.api_key:
            openai.api_key = self.api_key
            try:
                # API 키 유효성 확인 (모델 목록 가져오기)
                logger.debug("OpenAI API 연결 확인 중...")
                client = openai.OpenAI(api_key=self.api_key)
                models = client.models.list()
                logger.debug("OpenAI API 연결 성공")
            except Exception as e:
                logger.error(f"OpenAI API 초기화 오류: {str(e)}")
        else:
            logger.warning("OpenAI API 키가 설정되지 않았습니다.")
    
    def _init_lmstudio(self):
        """
        LM Studio API 초기화 및 연결 확인
        """
        try:
            # 간단한 ping 요청으로 LM Studio 서버 연결 확인
            logger.debug(f"LM Studio API 서버 연결 확인 중... (URL: {self.lmstudio_url})")
            # LM Studio의 /v1/models 엔드포인트로 연결 확인
            response = requests.get(f"{self.lmstudio_url}/v1/models", timeout=5)
            
            if response.status_code == 200:
                logger.debug("LM Studio API 서버 연결 성공")
            else:
                logger.warning(f"LM Studio API 서버 응답 코드: {response.status_code}")
        except Exception as e:
            logger.error(f"LM Studio API 서버 연결 확인 중 오류: {str(e)}")
            logger.warning("LM Studio 서버가 실행 중인지 확인하세요 (기본 URL: http://localhost:4982)")
    
    def generate_response(self, 
                         prompt: str, 
                         context: Optional[List[str]] = None,
                         system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        LLM에 프롬프트를 전송하고 응답 생성
        
        Args:
            prompt (str): 사용자 질의 텍스트
            context (Optional[List[str]]): 추가 컨텍스트 텍스트 목록
            system_prompt (Optional[str]): 시스템 프롬프트
            
        Returns:
            Dict[str, Any]: 응답 결과 (텍스트, 토큰 수 등)
        """
        if not prompt.strip():
            return {"error": "빈 프롬프트가 제공되었습니다."}
        
        # 프로바이더별 처리
        if self.provider == "openai":
            return self._generate_openai_response(prompt, context, system_prompt)
        elif self.provider == "lmstudio":
            return self._generate_lmstudio_response(prompt, context, system_prompt)
        else:
            error_msg = f"지원되지 않는 프로바이더입니다: {self.provider}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _generate_openai_response(self, 
                                 prompt: str, 
                                 context: Optional[List[str]] = None,
                                 system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        OpenAI API를 사용하여 응답 생성
        
        Args:
            prompt (str): 사용자 질의 텍스트
            context (Optional[List[str]]): 추가 컨텍스트 텍스트 목록
            system_prompt (Optional[str]): 시스템 프롬프트
            
        Returns:
            Dict[str, Any]: 응답 결과
        """
        if not self.api_key:
            return {"error": "OpenAI API 키가 설정되지 않았습니다."}
        
        try:
            messages = []
            
            # 시스템 프롬프트 추가
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                # 기본 시스템 프롬프트
                default_system_prompt = """
                당신은 지식이 풍부하고 도움이 되는 AI 어시스턴트입니다. 
                주어진 문서 정보를 바탕으로 정확하게 답변해 주세요.
                문서에서 직접적인 답을 찾을 수 없는 경우, "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답변하세요.
                답변은 깔끔하고 간결하게 한국어로 제공해 주세요.
                """
                messages.append({"role": "system", "content": default_system_prompt})
            
            # 컨텍스트 있으면 추가
            if context and len(context) > 0:
                context_text = "\n\n".join([f"문서 내용 #{i+1}:\n{doc}" for i, doc in enumerate(context)])
                context_message = f"다음은 질문에 답하는 데 도움이 될 관련 문서 내용입니다:\n\n{context_text}"
                messages.append({"role": "user", "content": context_message})
            
            # 사용자 프롬프트 추가
            messages.append({"role": "user", "content": prompt})
            
            start_time = time.time()
            logger.debug(f"OpenAI API 요청 시작 - 프롬프트: '{prompt[:50]}...'")
            
            # API 호출
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            elapsed_time = time.time() - start_time
            
            # 응답 처리
            if hasattr(response, 'choices') and len(response.choices) > 0:
                answer = response.choices[0].message.content
                
                # 응답 정보 구성
                result = {
                    "text": answer,
                    "model": self.model,
                    "elapsed_time": elapsed_time,
                    "success": True
                }
                
                # 토큰 사용량 정보 추출 (있는 경우)
                if hasattr(response, 'usage'):
                    result["tokens"] = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                
                logger.info(f"응답 생성 완료 (걸린 시간: {elapsed_time:.2f}초)")
                return result
            else:
                error_msg = "OpenAI API에서 응답을 받았지만 내용이 없습니다."
                logger.error(error_msg)
                return {"error": error_msg, "success": False}
                
        except Exception as e:
            error_msg = f"OpenAI API 호출 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg, "success": False}
    
    def _generate_lmstudio_response(self, 
                                   prompt: str, 
                                   context: Optional[List[str]] = None,
                                   system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        LM Studio 로컬 API를 사용하여 응답 생성
        
        Args:
            prompt (str): 사용자 질의 텍스트
            context (Optional[List[str]]): 추가 컨텍스트 텍스트 목록
            system_prompt (Optional[str]): 시스템 프롬프트
            
        Returns:
            Dict[str, Any]: 응답 결과
        """
        try:
            # API 요청을 위한 메시지 구성
            messages = []
            
            # 시스템 프롬프트 추가
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                # 기본 시스템 프롬프트
                default_system_prompt = """
                당신은 지식이 풍부하고 도움이 되는 AI 어시스턴트입니다. 
                주어진 문서 정보를 바탕으로 정확하게 답변해 주세요.
                문서에서 직접적인 답을 찾을 수 없는 경우, "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답변하세요.
                답변은 깔끔하고 간결하게 한국어로 제공해 주세요.
                """
                messages.append({"role": "system", "content": default_system_prompt})
            
            # 컨텍스트 있으면 추가
            if context and len(context) > 0:
                context_text = "\n\n".join([f"문서 내용 #{i+1}:\n{doc}" for i, doc in enumerate(context)])
                context_message = f"다음은 질문에 답하는 데 도움이 될 관련 문서 내용입니다:\n\n{context_text}"
                messages.append({"role": "user", "content": context_message})
            
            # 사용자 프롬프트 추가
            messages.append({"role": "user", "content": prompt})
            
            start_time = time.time()
            logger.debug(f"LM Studio API 요청 시작 - 프롬프트: '{prompt[:50]}...'")
            
            # LM Studio API 호출
            url = f"{self.lmstudio_url}/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            
            # max_tokens가 -1이면 무제한 토큰 생성
            max_tokens = -1 if self.max_tokens > 10000 else self.max_tokens
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            elapsed_time = time.time() - start_time
            
            # 응답 처리
            if response.status_code == 200:
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    answer = response_data["choices"][0]["message"]["content"]
                    
                    # 응답 정보 구성
                    result = {
                        "text": answer,
                        "model": self.model,
                        "elapsed_time": elapsed_time,
                        "success": True
                    }
                    
                    # 토큰 사용량 정보 추출 (있는 경우)
                    if "usage" in response_data:
                        result["tokens"] = {
                            "prompt_tokens": response_data["usage"].get("prompt_tokens", 0),
                            "completion_tokens": response_data["usage"].get("completion_tokens", 0),
                            "total_tokens": response_data["usage"].get("total_tokens", 0)
                        }
                    
                    logger.info(f"응답 생성 완료 (걸린 시간: {elapsed_time:.2f}초)")
                    return result
                else:
                    error_msg = "LM Studio API에서 응답을 받았지만 내용이 없습니다."
                    logger.error(error_msg)
                    return {"error": error_msg, "success": False}
            else:
                error_msg = f"LM Studio API 오류 (코드: {response.status_code}): {response.text}"
                logger.error(error_msg)
                return {"error": error_msg, "success": False}
                
        except requests.exceptions.ConnectionError:
            error_msg = f"LM Studio 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요 (URL: {self.lmstudio_url})"
            logger.error(error_msg)
            return {"error": error_msg, "success": False}
            
        except Exception as e:
            error_msg = f"LM Studio API 호출 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg, "success": False}
    
    def generate_stream_response(self,
                               prompt: str,
                               context: Optional[List[str]] = None,
                               system_prompt: Optional[str] = None) -> Any:
        """
        스트림 방식으로 LLM에 프롬프트를 전송하고 응답 생성
        
        Args:
            prompt (str): 사용자 질의 텍스트
            context (Optional[List[str]]): 추가 컨텍스트 텍스트 목록
            system_prompt (Optional[str]): 시스템 프롬프트
            
        Returns:
            Any: 응답 스트림 (프로바이더에 따라 다른 형식)
        """
        if not prompt.strip():
            raise ValueError("빈 프롬프트가 제공되었습니다.")
        
        # 프로바이더별 처리
        if self.provider == "openai":
            return self._generate_openai_stream_response(prompt, context, system_prompt)
        elif self.provider == "lmstudio":
            return self._generate_lmstudio_stream_response(prompt, context, system_prompt)
        else:
            error_msg = f"지원되지 않는 프로바이더입니다: {self.provider}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _generate_openai_stream_response(self,
                                       prompt: str,
                                       context: Optional[List[str]] = None,
                                       system_prompt: Optional[str] = None) -> Any:
        """
        OpenAI API를 사용하여 스트림 방식으로 응답 생성
        
        Args:
            prompt (str): 사용자 질의 텍스트
            context (Optional[List[str]]): 추가 컨텍스트 텍스트 목록
            system_prompt (Optional[str]): 시스템 프롬프트
            
        Returns:
            Any: OpenAI 응답 스트림 객체
        """
        if not self.api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
        
        try:
            messages = []
            
            # 시스템 프롬프트 추가
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                # 기본 시스템 프롬프트
                default_system_prompt = """
                당신은 지식이 풍부하고 도움이 되는 AI 어시스턴트입니다. 
                주어진 문서 정보를 바탕으로 정확하게 답변해 주세요.
                문서에서 직접적인 답을 찾을 수 없는 경우, "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답변하세요.
                답변은 깔끔하고 간결하게 한국어로 제공해 주세요.
                """
                messages.append({"role": "system", "content": default_system_prompt})
            
            # 컨텍스트 있으면 추가
            if context and len(context) > 0:
                context_text = "\n\n".join([f"문서 내용 #{i+1}:\n{doc}" for i, doc in enumerate(context)])
                context_message = f"다음은 질문에 답하는 데 도움이 될 관련 문서 내용입니다:\n\n{context_text}"
                messages.append({"role": "user", "content": context_message})
            
            # 사용자 프롬프트 추가
            messages.append({"role": "user", "content": prompt})
            
            logger.debug(f"OpenAI API 스트림 요청 시작 - 프롬프트: '{prompt[:50]}...'")
            
            # API 호출 (스트림 모드)
            client = openai.OpenAI(api_key=self.api_key)
            return client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
                
        except Exception as e:
            error_msg = f"OpenAI API 스트림 호출 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _generate_lmstudio_stream_response(self,
                                         prompt: str,
                                         context: Optional[List[str]] = None,
                                         system_prompt: Optional[str] = None) -> Any:
        """
        LM Studio 로컬 API를 사용하여 스트림 방식으로 응답 생성
        
        Args:
            prompt (str): 사용자 질의 텍스트
            context (Optional[List[str]]): 추가 컨텍스트 텍스트 목록
            system_prompt (Optional[str]): 시스템 프롬프트
            
        Returns:
            Generator: 응답 텍스트 조각을 생성하는 제너레이터
        """
        try:
            # API 요청을 위한 메시지 구성
            messages = []
            
            # 시스템 프롬프트 추가
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                # 기본 시스템 프롬프트
                default_system_prompt = """
                당신은 지식이 풍부하고 도움이 되는 AI 어시스턴트입니다. 
                주어진 문서 정보를 바탕으로 정확하게 답변해 주세요.
                문서에서 직접적인 답을 찾을 수 없는 경우, "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답변하세요.
                답변은 깔끔하고 간결하게 한국어로 제공해 주세요.
                """
                messages.append({"role": "system", "content": default_system_prompt})
            
            # 컨텍스트 있으면 추가
            if context and len(context) > 0:
                context_text = "\n\n".join([f"문서 내용 #{i+1}:\n{doc}" for i, doc in enumerate(context)])
                context_message = f"다음은 질문에 답하는 데 도움이 될 관련 문서 내용입니다:\n\n{context_text}"
                messages.append({"role": "user", "content": context_message})
            
            # 사용자 프롬프트 추가
            messages.append({"role": "user", "content": prompt})
            
            logger.debug(f"LM Studio API 스트림 요청 시작 - 프롬프트: '{prompt[:50]}...'")
            
            # LM Studio API 호출 (스트림 모드)
            url = f"{self.lmstudio_url}/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            
            # max_tokens가 -1이면 무제한 토큰 생성
            max_tokens = -1 if self.max_tokens > 10000 else self.max_tokens
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            # 스트림 응답 처리
            with requests.post(url, headers=headers, json=data, stream=True, timeout=60) as response:
                if response.status_code != 200:
                    error_msg = f"LM Studio API 오류 (코드: {response.status_code}): {response.text}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                # 청크 스트림 처리
                for line in response.iter_lines():
                    if not line:
                        continue
                        
                    # "data: " 프리픽스 제거
                    if line.startswith(b'data: '):
                        line = line[6:]
                        
                    # '[DONE]' 메시지 처리
                    if line.strip() == b'[DONE]':
                        break
                        
                    try:
                        # JSON 데이터 파싱
                        chunk = json.loads(line)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            # 델타 내용 추출
                            delta = chunk['choices'][0].get('delta', {})
                            if 'content' in delta and delta['content']:
                                yield delta['content']
                    except json.JSONDecodeError:
                        logger.warning(f"JSON 파싱 오류: {line}")
                        continue
                    
        except requests.exceptions.ConnectionError:
            error_msg = f"LM Studio 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요 (URL: {self.lmstudio_url})"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
            
        except Exception as e:
            error_msg = f"LM Studio API 스트림 호출 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        현재 LLM 모델 설정 정보 반환
        
        Returns:
            Dict[str, Any]: 모델 정보
        """
        info = {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        if self.provider == "lmstudio":
            info["lmstudio_url"] = self.lmstudio_url
            
        return info
