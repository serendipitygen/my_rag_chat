"""
문서 처리 모듈 - 다양한 형식의 문서를 처리하고 벡터 DB에 저장하는 기능 제공
"""
import os
import re
import logging
import hashlib
import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Union, Iterator
from pathlib import Path
from datetime import datetime

# 문서 처리 관련 라이브러리
import pypdf
import docx
import markdown
from bs4 import BeautifulSoup
import email
from email import policy
from email.parser import BytesParser
import html2text

# 내부 모듈
from utils.common import setup_logger, get_project_root, clean_filename, get_timestamp_str
from core.embedding_model import EmbeddingModel
from core.vector_db import VectorDB
from core.email_processor import EmailProcessor

# 로거 설정
logger = setup_logger(
    "document_processor", 
    os.path.join(get_project_root(), "logs", "document_processor.log")
)

class DocumentProcessor:
    """
    다양한 형식의 문서를 처리하고 벡터 DB에 저장하는 클래스
    """
    
    def __init__(self, 
                embedding_model: EmbeddingModel, 
                vector_db: VectorDB,
                chunk_size: int = 1000, 
                chunk_overlap: int = 200):
        """
        DocumentProcessor 초기화
        
        Args:
            embedding_model (EmbeddingModel): 임베딩 모델 인스턴스
            vector_db (VectorDB): 벡터 DB 인스턴스
            chunk_size (int): 문서 분할 시 청크 크기 (기본값: 1000)
            chunk_overlap (int): 문서 분할 시 청크 간 겹침 크기 (기본값: 200)
        """
        self.embedding_model = embedding_model
        self.vector_db = vector_db
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        logger.info(f"DocumentProcessor 초기화 완료 (청크 크기: {chunk_size}, 청크 겹침: {chunk_overlap})")
    
    def process_file(self, file_path: str) -> Tuple[int, Dict[str, Any]]:
        """
        파일을 처리하고 벡터 DB에 저장
        
        Args:
            file_path (str): 처리할 파일 경로
            
        Returns:
            Tuple[int, Dict[str, Any]]: (성공적으로 처리된 청크 수, 문서 메타데이터)
        """
        if not os.path.exists(file_path):
            error_msg = f"파일이 존재하지 않습니다: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # 파일 확장자 확인
        file_ext = os.path.splitext(file_path)[1].lower()
        
        logger.info(f"파일 처리 시작: {file_path} (형식: {file_ext})")
        
        try:
            # 파일 형식에 따라 텍스트 추출
            if file_ext == '.pdf':
                text = self._extract_text_from_pdf(file_path)
            elif file_ext == '.docx':
                text = self._extract_text_from_docx(file_path)
            elif file_ext == '.txt':
                text = self._extract_text_from_txt(file_path)
            elif file_ext == '.md':
                text = self._extract_text_from_md(file_path)
            elif file_ext == '.eml':
                text, metadata = self._extract_text_from_eml(file_path)
            else:
                error_msg = f"지원되지 않는 파일 형식입니다: {file_ext}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 문서 메타데이터 설정
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            modified_time = datetime.fromtimestamp(file_stats.st_mtime)
            
            doc_metadata = {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_ext": file_ext,
                "file_size": file_size,
                "modified_time": modified_time.isoformat(),
                "processed_time": get_timestamp_str()
            }
            
            # 텍스트가 비어있는지 확인
            if not text.strip():
                logger.warning(f"파일에서 텍스트를 추출했지만 내용이 없습니다: {file_path}")
                return 0, doc_metadata
            
            # 텍스트를 청크로 분할
            chunks = self._split_text(text)
            
            # 청크가 없는 경우
            if not chunks:
                logger.warning(f"텍스트를 분할했지만 청크가 생성되지 않았습니다: {file_path}")
                return 0, doc_metadata
            
            # 문서 ID 생성 (파일 경로 기반)
            doc_id = self._generate_doc_id(file_path)
            
            # 임베딩 생성
            embeddings = self.embedding_model.embed_texts(chunks)
            
            # 벡터 DB에 문서 저장
            self.vector_db.add_document(doc_id, file_path, chunks, embeddings)
            
            # 저장 완료
            logger.info(f"파일 처리 완료: {file_path} (청크 수: {len(chunks)})")
            
            # 문서 메타데이터 업데이트
            doc_metadata.update({
                "doc_id": doc_id,
                "chunk_count": len(chunks),
                "total_text_length": len(text)
            })
            
            # EML 파일인 경우 추가 메타데이터 병합
            if file_ext == '.eml' and metadata:
                doc_metadata.update(metadata)
            
            return len(chunks), doc_metadata
            
        except Exception as e:
            logger.error(f"파일 처리 중 오류 발생: {file_path} - {str(e)}")
            raise
    
    def process_directory(self, dir_path: str, file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        디렉토리 내의 모든 파일을 처리하고 벡터 DB에 저장
        
        Args:
            dir_path (str): 처리할 디렉토리 경로
            file_types (List[str], optional): 처리할 파일 확장자 목록 (예: ['.pdf', '.docx'])
                기본값은 None으로, 모든 지원되는 파일 형식을 처리
                
        Returns:
            List[Dict[str, Any]]: 처리된 파일들의 메타데이터 목록
        """
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            error_msg = f"디렉토리가 존재하지 않습니다: {dir_path}"
            logger.error(error_msg)
            raise NotADirectoryError(error_msg)
        
        # 지원되는 파일 형식
        supported_types = ['.pdf', '.docx', '.txt', '.md', '.eml']
        
        # 처리할 파일 형식 필터링
        if file_types:
            file_types = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in file_types]
            file_types = [ext for ext in file_types if ext in supported_types]
        else:
            file_types = supported_types
        
        if not file_types:
            logger.warning(f"처리할 유효한 파일 형식이 지정되지 않았습니다.")
            return []
        
        logger.info(f"디렉토리 처리 시작: {dir_path} (파일 형식: {', '.join(file_types)})")
        
        results = []
        processed_count = 0
        error_count = 0
        
        # 디렉토리 내 파일 목록 가져오기
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file_path)[1].lower()
                
                # 파일 형식 확인
                if file_ext not in file_types:
                    continue
                
                try:
                    # 파일 처리
                    chunks_count, metadata = self.process_file(file_path)
                    
                    if chunks_count > 0:
                        results.append(metadata)
                        processed_count += 1
                        logger.info(f"파일 처리 성공: {file_path} (청크 수: {chunks_count})")
                    else:
                        logger.warning(f"파일에서 텍스트를 추출했지만 저장된 청크가 없습니다: {file_path}")
                
                except Exception as e:
                    logger.error(f"파일 처리 실패: {file_path} - {str(e)}")
                    error_count += 1
        
        logger.info(f"디렉토리 처리 완료: {dir_path} (성공: {processed_count}, 실패: {error_count})")
        
        return results
    
    def process_text(self, text: str, metadata: Dict[str, Any] = None) -> Tuple[int, Dict[str, Any]]:
        """
        텍스트를 직접 처리하고 벡터 DB에 저장
        
        Args:
            text (str): 처리할 텍스트
            metadata (Dict[str, Any], optional): 문서 메타데이터
                
        Returns:
            Tuple[int, Dict[str, Any]]: (성공적으로 처리된 청크 수, 문서 메타데이터)
        """
        if not text.strip():
            logger.warning("처리할 텍스트가 비어 있습니다.")
            return 0, {}
        
        logger.info(f"텍스트 처리 시작 (길이: {len(text)})")
        
        try:
            # 기본 메타데이터 설정
            if metadata is None:
                metadata = {}
            
            # 문서 ID 생성
            text_hash = hashlib.md5(text[:1000].encode()).hexdigest()
            doc_id = f"text_{text_hash}_{int(datetime.now().timestamp())}"
            
            # 텍스트 청크로 분할
            chunks = self._split_text(text)
            
            # 청크가 없는 경우
            if not chunks:
                logger.warning("텍스트를 분할했지만 청크가 생성되지 않았습니다.")
                return 0, metadata
            
            # 임베딩 생성
            embeddings = self.embedding_model.embed_texts(chunks)
            
            # 벡터 DB에 문서 저장
            self.vector_db.add_document(doc_id, "", chunks, embeddings)
            
            # 처리 완료
            logger.info(f"텍스트 처리 완료 (청크 수: {len(chunks)})")
            
            # 문서 메타데이터 업데이트
            doc_metadata = {
                "doc_id": doc_id,
                "chunk_count": len(chunks),
                "total_text_length": len(text),
                "processed_time": get_timestamp_str(),
                **metadata
            }
            
            return len(chunks), doc_metadata
            
        except Exception as e:
            logger.error(f"텍스트 처리 중 오류 발생: {str(e)}")
            raise
    
    def query_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        쿼리와 유사한 문서 청크 검색
        
        Args:
            query (str): 검색 쿼리
            top_k (int): 반환할 최대 결과 수 (기본값: 5)
            
        Returns:
            List[Dict[str, Any]]: 쿼리와 유사한 문서 청크 정보 목록
                (각 아이템은 원본 텍스트, 메타데이터, 유사도 점수 포함)
        """
        if not query.strip():
            logger.warning("검색 쿼리가 비어 있습니다.")
            return []
        
        logger.info(f"유사 문서 검색 시작 (쿼리: '{query[:50]}...', top_k: {top_k})")
        
        try:
            # 쿼리 임베딩
            query_embedding = self.embedding_model.embed_query(query)
            
            # 벡터 DB에서 유사한 문서 검색
            results = self.vector_db.search_vectors(query_embedding, top_k)
            
            logger.info(f"유사 문서 검색 완료 (결과 수: {len(results)})")
            
            return results
            
        except Exception as e:
            logger.error(f"유사 문서 검색 중 오류 발생: {str(e)}")
            raise
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        PDF 파일에서 텍스트 추출
        
        Args:
            file_path (str): PDF 파일 경로
            
        Returns:
            str: 추출된 텍스트
        """
        logger.debug(f"PDF 파일에서 텍스트 추출 시작: {file_path}")
        
        try:
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                text = ""
                
                # 각 페이지에서 텍스트 추출
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"{page_text}\n\n"
                    else:
                        logger.debug(f"PDF 페이지 {i+1}에서 텍스트를 추출할 수 없습니다.")
                
                # 여러 줄바꿈 정리
                text = re.sub(r'\n{3,}', '\n\n', text)
                
                logger.debug(f"PDF 파일에서 텍스트 추출 완료: {file_path} (길이: {len(text)})")
                
                return text
                
        except Exception as e:
            logger.error(f"PDF 파일에서 텍스트 추출 중 오류 발생: {file_path} - {str(e)}")
            raise
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """
        DOCX 파일에서 텍스트 추출
        
        Args:
            file_path (str): DOCX 파일 경로
            
        Returns:
            str: 추출된 텍스트
        """
        logger.debug(f"DOCX 파일에서 텍스트 추출 시작: {file_path}")
        
        try:
            doc = docx.Document(file_path)
            text = ""
            
            # 각 단락에서 텍스트 추출
            for para in doc.paragraphs:
                if para.text:
                    text += f"{para.text}\n"
            
            # 텍스트 정리
            text = text.strip()
            
            logger.debug(f"DOCX 파일에서 텍스트 추출 완료: {file_path} (길이: {len(text)})")
            
            return text
            
        except Exception as e:
            logger.error(f"DOCX 파일에서 텍스트 추출 중 오류 발생: {file_path} - {str(e)}")
            raise
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """
        TXT 파일에서 텍스트 추출
        
        Args:
            file_path (str): TXT 파일 경로
            
        Returns:
            str: 추출된 텍스트
        """
        logger.debug(f"TXT 파일에서 텍스트 추출 시작: {file_path}")
        
        try:
            # 다양한 인코딩 시도
            encodings = ['utf-8', 'cp949', 'euc-kr']
            text = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text = file.read()
                    logger.debug(f"TXT 파일을 {encoding} 인코딩으로 성공적으로 읽었습니다.")
                    break
                except UnicodeDecodeError:
                    logger.debug(f"TXT 파일을 {encoding} 인코딩으로 읽는 데 실패했습니다.")
                    continue
            
            if text is None:
                logger.error(f"TXT 파일을 어떠한 인코딩으로도 읽을 수 없습니다: {file_path}")
                raise UnicodeDecodeError("", b"", 0, 0, "텍스트 파일을 읽을 수 없습니다.")
            
            logger.debug(f"TXT 파일에서 텍스트 추출 완료: {file_path} (길이: {len(text)})")
            
            return text
            
        except Exception as e:
            logger.error(f"TXT 파일에서 텍스트 추출 중 오류 발생: {file_path} - {str(e)}")
            raise
    
    def _extract_text_from_md(self, file_path: str) -> str:
        """
        Markdown 파일에서 텍스트 추출
        
        Args:
            file_path (str): Markdown 파일 경로
            
        Returns:
            str: 추출된 텍스트
        """
        logger.debug(f"Markdown 파일에서 텍스트 추출 시작: {file_path}")
        
        try:
            # 다양한 인코딩 시도
            encodings = ['utf-8', 'cp949', 'euc-kr']
            md_text = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        md_text = file.read()
                    logger.debug(f"Markdown 파일을 {encoding} 인코딩으로 성공적으로 읽었습니다.")
                    break
                except UnicodeDecodeError:
                    logger.debug(f"Markdown 파일을 {encoding} 인코딩으로 읽는 데 실패했습니다.")
                    continue
            
            if md_text is None:
                logger.error(f"Markdown 파일을 어떠한 인코딩으로도 읽을 수 없습니다: {file_path}")
                raise UnicodeDecodeError("", b"", 0, 0, "Markdown 파일을 읽을 수 없습니다.")
            
            # Markdown을 HTML로 변환
            html = markdown.markdown(md_text)
            
            # HTML에서 텍스트 추출
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(separator='\n')
            
            logger.debug(f"Markdown 파일에서 텍스트 추출 완료: {file_path} (길이: {len(text)})")
            
            return text
            
        except Exception as e:
            logger.error(f"Markdown 파일에서 텍스트 추출 중 오류 발생: {file_path} - {str(e)}")
            raise
    
    def _extract_text_from_eml(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        EML 파일에서 텍스트 추출
        
        Args:
            file_path (str): EML 파일 경로
            
        Returns:
            Tuple[str, Dict[str, Any]]: 추출된 텍스트와 메타데이터
        """
        try:
            # EmailProcessor 클래스를 사용하여 EML 파일 처리
            email_processor = EmailProcessor()
            result = email_processor.process_file(file_path)
            
            if not result:
                logger.error(f"EML 파일 처리 실패: {file_path}")
                return "", {}
            
            # 이메일 메타데이터 추출
            metadata = result["metadata"]
            content = result["content"]
            attachments = result["attachments"]
            
            # 첨부 파일 정보 구성
            attachments_info = []
            for attachment in attachments:
                attachments_info.append({
                    "filename": attachment.get("filename", "알 수 없는 파일"),
                    "content_type": attachment.get("content_type", "알 수 없는 형식"),
                    "size": attachment.get("size", 0)
                })
            
            # 메타데이터에 첨부 파일 정보 추가
            metadata["attachments"] = attachments_info
            
            # 최종 텍스트 구성
            final_text = f"제목: {metadata.get('subject', '제목 없음')}\n"
            final_text += f"보낸 사람: {metadata.get('from', '발신자 정보 없음')}\n"
            final_text += f"받는 사람: {metadata.get('to', '수신자 정보 없음')}\n"
            final_text += f"날짜: {metadata.get('date', '날짜 정보 없음')}\n\n"
            final_text += "--- 본문 ---\n" + content + "\n"
            
            # 첨부 파일 정보 추가
            if attachments_info:
                final_text += "\n--- 첨부 파일 목록 ---\n"
                for i, attachment in enumerate(attachments_info, 1):
                    final_text += f"{i}. {attachment['filename']} ({attachment['content_type']}, {attachment['size']} 바이트)\n"
            
            return final_text, metadata
            
        except Exception as e:
            logger.error(f"EML 파일 처리 중 오류 발생: {str(e)}")
            return "", {}
    
    def _split_text(self, text: str) -> List[str]:
        """
        텍스트를 청크로 분할
        
        Args:
            text (str): 분할할 텍스트
            
        Returns:
            List[str]: 분할된 텍스트 청크 목록
        """
        if not text.strip():
            return []
        
        logger.debug(f"텍스트 분할 시작 (길이: {len(text)}, 청크 크기: {self.chunk_size}, 겹침: {self.chunk_overlap})")
        
        # 텍스트가 청크 크기보다 작은 경우
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # 청크 끝 위치 계산
            end = start + self.chunk_size
            
            if end >= len(text):
                # 마지막 청크인 경우
                chunk = text[start:]
                chunks.append(chunk)
                break
            
            # 문장 또는 단락 끝에서 잘라내기 (더 자연스러운 분할을 위해)
            # 1. 단락 끝 (빈 줄) 찾기
            paragraph_end = text.find('\n\n', start + self.chunk_size // 2, end)
            
            # 2. 단락 끝을 찾지 못한 경우, 문장 끝 (마침표, 물음표, 느낌표) 찾기
            if paragraph_end == -1:
                # 문장 끝 찾기 (마침표, 물음표, 느낌표 + 공백 또는 줄바꿈)
                sentence_patterns = ['. ', '? ', '! ', '.\n', '?\n', '!\n']
                sentence_ends = [text.find(pattern, start + self.chunk_size // 2, end) for pattern in sentence_patterns]
                sentence_ends = [e for e in sentence_ends if e != -1]
                
                if sentence_ends:
                    # 가장 늦은 문장 끝 선택
                    split_point = max(sentence_ends) + 1  # 마침표 등 포함
                else:
                    # 문장 끝을 찾지 못한 경우, 공백에서 분할
                    space = text.rfind(' ', start + self.chunk_size // 2, end)
                    if space != -1:
                        split_point = space + 1  # 공백 포함
                    else:
                        # 공백도 없는 경우, 그냥 크기대로 분할
                        split_point = end
            else:
                # 단락 끝을 찾은 경우
                split_point = paragraph_end + 2  # '\n\n' 포함
            
            # 청크 추출
            chunk = text[start:split_point].strip()
            if chunk:  # 비어있지 않은 경우만 추가
                chunks.append(chunk)
            
            # 다음 시작 위치 계산 (겹침 고려)
            start = split_point - self.chunk_overlap
            if start < split_point - self.chunk_size:
                # 겹침이 너무 큰 경우 (음수가 될 수 있음) 조정
                start = split_point - min(self.chunk_overlap, self.chunk_size // 2)
            
            # 시작 위치가 이전 분할 지점과 같거나 작으면 강제로 전진
            if start <= split_point - self.chunk_size:
                start = split_point
        
        logger.debug(f"텍스트 분할 완료 (청크 수: {len(chunks)})")
        
        return chunks
    
    def _generate_doc_id(self, file_path: str) -> str:
        """
        파일 경로를 기반으로 문서 ID 생성
        
        Args:
            file_path (str): 파일 경로
            
        Returns:
            str: 생성된 문서 ID
        """
        # 파일 이름과 수정 시간으로 ID 생성
        file_name = os.path.basename(file_path)
        file_stats = os.stat(file_path)
        modified_time = int(file_stats.st_mtime)
        
        # 해시 생성
        hash_base = f"{file_name}_{modified_time}"
        doc_id = hashlib.md5(hash_base.encode()).hexdigest()
        
        return doc_id
    
    def get_stats(self) -> Dict[str, Any]:
        """
        문서 처리기 통계 정보 반환
        
        Returns:
            Dict[str, Any]: 통계 정보
        """
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "vector_db_stats": self.vector_db.get_stats()
        }
