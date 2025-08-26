"""
이메일(.eml) 파일 처리 모듈
"""
import os
import email
import logging
from email.header import decode_header
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional, Tuple

# 로거 설정
logger = logging.getLogger(__name__)

class EmailProcessor:
    """
    이메일(.eml) 파일을 처리하는 클래스
    """
    
    def __init__(self):
        """
        이메일 처리기 초기화
        """
        logger.info("이메일 처리기 초기화")
    
    def process_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        EML 파일을 처리하여 텍스트 및 메타데이터 추출
        
        Args:
            file_path (str): EML 파일 경로
            
        Returns:
            Optional[Dict[str, Any]]: 처리된 이메일 데이터 (실패 시 None)
        """
        try:
            logger.info(f"EML 파일 처리 중: {file_path}")
            
            # 파일이 존재하는지 확인
            if not os.path.exists(file_path):
                logger.error(f"파일을 찾을 수 없습니다: {file_path}")
                return None
                
            # 이메일 파일 읽기
            with open(file_path, 'rb') as f:
                msg = email.message_from_binary_file(f)
            
            # 기본 메타데이터 추출
            metadata = self._extract_metadata(msg)
            
            # 이메일 본문 추출
            content = self._extract_content(msg)
            
            # 첨부 파일 정보 추출
            attachments = self._extract_attachments(msg)
            
            # 결과 데이터 구성
            result = {
                "metadata": metadata,
                "content": content,
                "attachments": attachments,
                "file_path": file_path
            }
            
            logger.info(f"EML 파일 처리 완료: {metadata.get('subject', '제목 없음')}")
            return result
            
        except Exception as e:
            logger.error(f"EML 파일 처리 중 오류 발생: {str(e)}")
            return None
    
    def _decode_header_value(self, value: str) -> str:
        """
        이메일 헤더 값 디코딩
        
        Args:
            value (str): 디코딩할 헤더 값
            
        Returns:
            str: 디코딩된 헤더 값
        """
        if value is None:
            return ""
            
        try:
            decoded_parts = []
            parts = decode_header(value)
            
            for part, encoding in parts:
                if isinstance(part, bytes):
                    # 인코딩이 지정된 경우
                    if encoding:
                        try:
                            decoded_part = part.decode(encoding)
                        except:
                            # 지정된 인코딩으로 디코딩 실패 시 대체 시도
                            try:
                                decoded_part = part.decode('utf-8')
                            except:
                                try:
                                    decoded_part = part.decode('euc-kr')
                                except:
                                    decoded_part = part.decode('cp949', errors='replace')
                    else:
                        # 인코딩이 지정되지 않은 경우
                        try:
                            decoded_part = part.decode('utf-8')
                        except:
                            try:
                                decoded_part = part.decode('euc-kr')
                            except:
                                decoded_part = part.decode('cp949', errors='replace')
                else:
                    # 이미 문자열인 경우
                    decoded_part = part
                    
                decoded_parts.append(decoded_part)
                
            return ''.join(decoded_parts)
            
        except Exception as e:
            logger.warning(f"헤더 디코딩 중 오류 발생: {str(e)}")
            return value
    
    def _extract_metadata(self, msg) -> Dict[str, str]:
        """
        이메일 메시지에서 메타데이터 추출
        
        Args:
            msg: 이메일 메시지 객체
            
        Returns:
            Dict[str, str]: 추출된 메타데이터
        """
        metadata = {}
        
        # 기본 헤더 정보 추출
        for key in ['From', 'To', 'Subject', 'Date', 'Cc', 'Bcc', 'Message-ID']:
            if msg[key]:
                metadata[key.lower()] = self._decode_header_value(msg[key])
        
        return metadata
    
    def _extract_content(self, msg) -> str:
        """
        이메일 메시지에서 본문 내용 추출
        
        Args:
            msg: 이메일 메시지 객체
            
        Returns:
            str: 추출된 본문 내용
        """
        content = []
        
        # 메시지 파트 순회
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = part.get('Content-Disposition')
            
            # 첨부 파일이 아닌 본문 내용만 추출
            if content_disposition is None or 'attachment' not in content_disposition:
                # 텍스트 내용 추출
                if content_type == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        try:
                            text = payload.decode(charset)
                        except:
                            try:
                                text = payload.decode('utf-8')
                            except:
                                try:
                                    text = payload.decode('euc-kr')
                                except:
                                    text = payload.decode('cp949', errors='replace')
                        content.append(text)
                
                # HTML 내용 추출 및 텍스트로 변환
                elif content_type == 'text/html':
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        try:
                            html = payload.decode(charset)
                        except:
                            try:
                                html = payload.decode('utf-8')
                            except:
                                try:
                                    html = payload.decode('euc-kr')
                                except:
                                    html = payload.decode('cp949', errors='replace')
                        
                        # HTML을 텍스트로 변환
                        soup = BeautifulSoup(html, 'html.parser')
                        text = soup.get_text(separator=' ', strip=True)
                        content.append(text)
        
        return '\n\n'.join(content)
    
    def _extract_attachments(self, msg) -> List[Dict[str, Any]]:
        """
        이메일 메시지에서 첨부 파일 정보 추출
        
        Args:
            msg: 이메일 메시지 객체
            
        Returns:
            List[Dict[str, Any]]: 추출된 첨부 파일 정보 목록
        """
        attachments = []
        
        for part in msg.walk():
            content_disposition = part.get('Content-Disposition')
            filename = part.get_filename()
            
            # 첨부 파일인 경우
            if content_disposition and 'attachment' in content_disposition and filename:
                # 파일명 디코딩
                filename = self._decode_header_value(filename)
                
                # 첨부 파일 정보 저장
                attachments.append({
                    "filename": filename,
                    "content_type": part.get_content_type(),
                    "size": len(part.get_payload(decode=True))
                })
        
        return attachments
