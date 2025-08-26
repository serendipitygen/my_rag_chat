"""
Chainlit 기반 RAG 챗봇 애플리케이션

사용자의 질문에 대해 벡터 DB에서 관련 문서를 검색하고
Gemini API를 통해 답변을 생성하는 챗봇 인터페이스
"""

import os
import sys
import time
from typing import Dict, List, Any

import chainlit as cl
from chainlit.types import AskFileResponse

# 내부 모듈
from utils.common import setup_logger, get_project_root
from core.rag_engine import RAGEngine

# 로거 설정
logger = setup_logger(
    "chat", 
    os.path.join(get_project_root(), "logs", "chat.log")
)

# 벡터 DB 경로 설정
vector_db_path = os.path.join(get_project_root(), "data", "vector_db")

# RAG 엔진 초기화
@cl.on_chat_start
async def on_chat_start():
    """
    챗 세션 시작 시 호출되는 함수
    RAG 엔진을 초기화하고 사용자에게 환영 메시지를 보냅니다.
    """
    try:
        # RAG 엔진 초기화
        rag_engine = RAGEngine(
            embedding_model_name="jhgan/ko-sroberta-multitask",
            llm_service="gemini",  # Gemini API 사용
            vector_db_path=vector_db_path
        )

        # 세션에 RAG 엔진 저장
        cl.user_session.set("rag_engine", rag_engine)

        # 환영 메시지 표시
        await cl.Message(
            content="안녕하세요! RAG 챗봇입니다. 무엇을 도와드릴까요?",
            author="시스템"
        ).send()
        logger.info("새 챗 세션 시작")

    except Exception as e:
        error_msg = f"챗봇 초기화 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        await cl.Message(
            content=f"오류: {error_msg}\n\n시스템을 다시 시작해주세요.",
            author="시스템"
        ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    사용자 메시지 수신 시 호출되는 함수
    
    Args:
        message: 사용자가 보낸 메시지
    """
    try:
        # 세션에서 RAG 엔진 가져오기
        rag_engine = cl.user_session.get("rag_engine")
        if not rag_engine:
            await cl.Message(
                content="오류: RAG 엔진이 초기화되지 않았습니다. 페이지를 새로고침해주세요.",
                author="시스템"
            ).send()
            return

        # 사용자 질문
        query = message.content
        logger.info(f"사용자 질문: {query}")

        # 처리 중 표시
        await cl.Message(
            content="질문을 처리 중입니다...",
            author="시스템"
        ).send()

        # 답변 생성 준비
        with cl.Step(name="문서 검색") as step:
            start_time = time.time()
            
            # 스트림 방식으로 검색 결과 및 응답 생성 준비
            # query_stream은 바로 async generator를 반환합니다
            stream_generator = rag_engine.query_stream(query_text=query, top_k=5)
            
            # 이 단계에서는 문서 검색만 표시하고, 실제 스트림 처리는 다음 단계로 이동
            step.output = "관련 문서를 검색했습니다."
        
        # 스트리밍 답변 생성 (새 메시지 생성)
        answer_message = cl.Message(content="", author="챗봇")
        await answer_message.send()
        
        try:
            # 스트림 방식으로 응답 처리
            full_answer = ""
            
            # 비동기 생성기(async generator)에서 직접 청크를 가져와 처리
            async for chunk in stream_generator:
                if hasattr(chunk, 'text') and chunk.text:
                    # Gemini 형식의 청크
                    content = chunk.text
                    full_answer += content
                    answer_message.content = full_answer
                    await answer_message.update()
                elif isinstance(chunk, str):
                    # 문자열 형식의 청크
                    full_answer += chunk
                    answer_message.content = full_answer
                    await answer_message.update()
                
            # 최종 완성된 답변으로 업데이트
            answer_message.content = full_answer
            
            # 소요 시간 계산
            elapsed = time.time() - start_time
            
            # 소요 시간 표시
            logger.info(f"응답 생성 완료. 소요 시간: {elapsed:.2f}초")
            
        except Exception as e:
            error_msg = f"메시지 처리 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            
            # 오류 메시지 표시
            await cl.Message(
                content=f"죄송합니다. 오류가 발생했습니다: {error_msg}",
                author="시스템"
            ).send()
        
        # 전체 처리 시간 계산 및 로깅
        total_elapsed = time.time() - start_time
        logger.info(f"질문 처리 완료 (소요 시간: {total_elapsed:.2f}초)")
            
    except Exception as e:
        error_msg = f"메시지 처리 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        await cl.Message(
            content=f"오류: {error_msg}",
            author="시스템"
        ).send()

if __name__ == "__main__":
    # Chainlit 서버는 별도로 실행되므로 여기서는 아무것도 하지 않음
    # 실행 방법: chainlit run chat.py
    pass
