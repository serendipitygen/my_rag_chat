"""
공통 유틸리티 함수 모듈
"""
import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import yaml
from pathlib import Path

# 로깅 설정
def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    로거 설정 함수
    
    Args:
        name (str): 로거 이름
        log_file (str): 로그 파일 경로
        level: 로깅 레벨 (기본값: INFO)
        
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    # 로그 디렉토리 생성
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로거 설정
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 이미 핸들러가 있으면 추가하지 않음
    if not logger.handlers:
        # 파일 핸들러 추가
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

# 설정 파일 로드
def load_config(config_path: str) -> Dict[str, Any]:
    """
    YAML 설정 파일 로드 함수
    
    Args:
        config_path (str): 설정 파일 경로
        
    Returns:
        Dict[str, Any]: 설정 값이 담긴 딕셔너리
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"설정 파일 로드 중 오류 발생: {e}")
        return {}

# 프로젝트 루트 경로 가져오기
def get_project_root() -> Path:
    """
    프로젝트 루트 디렉토리 경로 반환
    
    Returns:
        Path: 프로젝트 루트 경로
    """
    # 현재 파일 위치에서 상위로 두 번 올라가면 프로젝트 루트
    return Path(__file__).parent.parent

# 한글 파일명 처리 함수
def sanitize_filename(filename: str) -> str:
    """
    한글 파일명을 포함한 파일명 정리 함수
    
    Args:
        filename (str): 원본 파일명
        
    Returns:
        str: 정리된 파일명
    """
    # 파일 확장자와 이름 분리
    base, ext = os.path.splitext(filename)
    
    # 파일명에서 사용할 수 없는 문자 제거 (Windows 기준)
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        base = base.replace(char, '_')
    
    # 정리된 파일명 반환
    return f"{base}{ext}"

# clean_filename 함수 (document_processor.py에서 사용)
def clean_filename(filename: str) -> str:
    """
    파일명에서 사용할 수 없는 특수 문자를 제거하는 함수
    
    Args:
        filename (str): 원본 파일명
        
    Returns:
        str: 정리된 파일명
    """
    # 내부적으로 sanitize_filename 함수 호출
    return sanitize_filename(filename)

# 타임스탬프 문자열 생성
def get_timestamp() -> str:
    """
    현재 시간을 기반으로 타임스탬프 문자열 생성
    
    Returns:
        str: 타임스탬프 문자열 (YYYYMMDD_HHMMSS 형식)
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# 타임스탬프 문자열 생성 (포맷 지정 가능)
def get_timestamp_str(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    현재 시간을 기반으로 타임스탬프 문자열 생성 (포맷 지정 가능)
    
    Args:
        format_str (str): 날짜/시간 포맷 (기본값: "%Y-%m-%d %H:%M:%S")
        
    Returns:
        str: 지정된 포맷의 타임스탬프 문자열
    """
    return datetime.now().strftime(format_str)
