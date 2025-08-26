"""
문서 처리 모듈 - 다양한 형식의 문서를 처리하여 텍스트 추출
"""
import os
import tempfile
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import logging

# 문서 처리용 라이브러리
import pypdf
from pypdf import PdfReader
import docx
from markdown import markdown
from bs4 import BeautifulSoup

# 내부 모듈
from utils.common import setup_logger, sanitize_filename, get_project_root

# 로거 설정
logger = setup_logger(
    "document_processor", 
    os.path.join(get_project_root(), "logs", "document_processor.log")
)

class DocumentProcessor:
    """
    문서 처리기 클래스 - 다양한 파일 형식에서 텍스트 추출
    지원 형식: PDF, DOCX, TXT, MD
    """
    
    def __init__(self):
        """
        문서 처리기 초기화
        """
        self.supported_extensions = {
            '.pdf': self._process_pdf,
            '.docx': self._process_docx,
            '.txt': self._process_txt,
            '.md': self._process_markdown
        }
        logger.info("문서 처리기가 초기화되었습니다.")
    
    def process_document(self, file_path: str) -> Tuple[str, List[str]]:
        """
        문서 파일을 처리하여 텍스트 추출
        
        Args:
            file_path (str): 처리할 파일 경로
            
        Returns:
            Tuple[str, List[str]]: (문서 제목, 텍스트 청크 리스트)
            
        Raises:
            ValueError: 지원하지 않는 파일 형식일 경우
        """
        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            error_msg = f"파일이 존재하지 않습니다: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # 파일 확장자 확인
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in self.supported_extensions:
            error_msg = f"지원하지 않는 파일 형식입니다: {ext}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            # 해당 파일 형식에 맞는 처리 함수 호출
            logger.info(f"'{file_path}' 파일 처리 시작")
            title, content = self.supported_extensions[ext](file_path)
            logger.info(f"'{file_path}' 파일 처리 완료")
            return title, content
            
        except Exception as e:
            error_msg = f"파일 처리 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _process_pdf(self, file_path: str) -> Tuple[str, List[str]]:
        """PDF 파일 처리"""
        try:
            reader = PdfReader(file_path)
            content = []
            
            # 제목 추출 (PDF 메타데이터 또는 파일명)
            title = reader.metadata.title if reader.metadata and reader.metadata.title else os.path.basename(file_path)
            
            # 페이지별 텍스트 추출
            for page in reader.pages:
                text = page.extract_text()
                if text.strip():  # 빈 페이지가 아닌 경우에만 추가
                    content.append(text)
            
            logger.info(f"PDF 파일에서 {len(content)}개 페이지 추출 완료")
            return title, content
            
        except Exception as e:
            logger.error(f"PDF 처리 중 오류: {str(e)}")
            raise
    
    def _process_docx(self, file_path: str) -> Tuple[str, List[str]]:
        """DOCX 파일 처리"""
        try:
            doc = docx.Document(file_path)
            
            # 제목 추출 (문서 제목 속성 또는 파일명)
            title = doc.core_properties.title if doc.core_properties.title else os.path.basename(file_path)
            
            # 문단별 텍스트 추출
            content = [para.text for para in doc.paragraphs if para.text.strip()]
            
            logger.info(f"DOCX 파일에서 {len(content)}개 문단 추출 완료")
            return title, content
            
        except Exception as e:
            logger.error(f"DOCX 처리 중 오류: {str(e)}")
            raise
    
    def _process_txt(self, file_path: str) -> Tuple[str, List[str]]:
        """TXT 파일 처리"""
        try:
            # 파일명을 제목으로 사용
            title = os.path.basename(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                # 줄 단위로 읽기
                lines = f.readlines()
                
                # 빈 줄 제거 및 정리
                content = [line.strip() for line in lines if line.strip()]
            
            logger.info(f"TXT 파일에서 {len(content)}개 줄 추출 완료")
            return title, content
            
        except UnicodeDecodeError:
            # UTF-8이 아닌 경우 다른 인코딩 시도
            logger.warning("UTF-8 디코딩 실패, CP949로 시도합니다.")
            with open(file_path, 'r', encoding='cp949') as f:
                lines = f.readlines()
                content = [line.strip() for line in lines if line.strip()]
            
            return os.path.basename(file_path), content
            
        except Exception as e:
            logger.error(f"TXT 처리 중 오류: {str(e)}")
            raise
    
    def _process_markdown(self, file_path: str) -> Tuple[str, List[str]]:
        """마크다운 파일 처리"""
        try:
            # 파일명을 제목으로 사용
            title = os.path.basename(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # 마크다운을 HTML로 변환
            html = markdown(md_content)
            
            # HTML에서 텍스트 추출
            soup = BeautifulSoup(html, 'html.parser')
            
            # 제목 추출 시도 (h1 태그가 있으면 첫 번째 h1을 제목으로)
            h1 = soup.find('h1')
            if h1 and h1.text.strip():
                title = h1.text.strip()
            
            # 텍스트 추출 (단락별로)
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            content = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
            
            logger.info(f"마크다운 파일에서 {len(content)}개 문단 추출 완료")
            return title, content
            
        except UnicodeDecodeError:
            # UTF-8이 아닌 경우 다른 인코딩 시도
            logger.warning("UTF-8 디코딩 실패, CP949로 시도합니다.")
            with open(file_path, 'r', encoding='cp949') as f:
                md_content = f.read()
            
            html = markdown(md_content)
            soup = BeautifulSoup(html, 'html.parser')
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            content = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
            
            return os.path.basename(file_path), content
            
        except Exception as e:
            logger.error(f"마크다운 처리 중 오류: {str(e)}")
            raise
