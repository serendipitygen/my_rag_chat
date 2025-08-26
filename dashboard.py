"""
파일 등록 대시보드 - Dash 기반 웹 인터페이스

이 모듈은 Dash를 사용하여 다음 기능을 제공합니다:
1. 파일 업로드 및 문서 처리
2. 처리 상태 표시 (처리 중 아이콘)
3. 등록된 파일 목록 표시
4. 파일 클릭 시 청크 목록 표시
"""

import os
import time
import base64
import json
import threading
import uuid
from pathlib import Path
from datetime import datetime
import tempfile
import pandas as pd
import shutil

# Dash 관련 패키지
import dash
from dash import html, dcc, callback, Input, Output, State, dash_table, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# 내부 모듈
from utils.common import setup_logger, get_project_root
from core.rag_engine import RAGEngine
from core.document_processor import DocumentProcessor
from core.embedding_model import EmbeddingModel
from core.vector_db import VectorDB

# 로거 설정
logger = setup_logger(
    "dashboard", 
    os.path.join(get_project_root(), "logs", "dashboard.log")
)

# 전역 변수: 처리 중인 작업 상태
processing_files = {}  # 파일 ID를 키로 하는 처리 상태 딕셔너리

# 벡터 DB 경로 설정
vector_db_path = os.path.join(get_project_root(), "data", "vector_db")
# 벡터 DB 디렉토리 생성
os.makedirs(vector_db_path, exist_ok=True)

# 임베딩 모델 초기화
embedding_model = EmbeddingModel(model_name="jhgan/ko-sroberta-multitask")

# 벡터 DB 초기화
vector_db = VectorDB(db_path=vector_db_path)

# RAG 엔진 초기화
def init_rag_engine():
    """RAG 엔진 초기화"""
    engine = RAGEngine(
        embedding_model_name="jhgan/ko-sroberta-multitask",
        llm_service="lm_studio",
        vector_db_path=vector_db_path
    )
    
    return engine

# DocumentProcessor 초기화
def init_document_processor():
    """DocumentProcessor 초기화"""
    processor = DocumentProcessor(
        embedding_model=embedding_model,
        vector_db=vector_db,
        chunk_size=1000,
        chunk_overlap=200
    )
    
    return processor

# RAG 엔진 객체
rag_engine = init_rag_engine()
# 문서 처리기 객체
doc_processor = init_document_processor()

# 파일 업로드 처리 (백그라운드 쓰레드에서 실행)
def process_file_async(file_id, file_path, filename):
    """
    파일을 비동기적으로 처리하는 함수
    
    Args:
        file_id (str): 파일 ID
        file_path (str): 임시 저장된 파일 경로
        filename (str): 원본 파일명
    """
    try:
        # 처리 상태 업데이트
        processing_files[file_id] = {
            "status": "processing",
            "filename": filename,
            "start_time": time.time(),
            "progress": 0
        }
        
        # 10% 진행 상태 업데이트
        processing_files[file_id]["progress"] = 10
        time.sleep(0.5)  # 진행 상태 표시 효과
        
        # 문서 처리기를 사용하여 문서 처리
        chunk_count, doc_info = doc_processor.process_file(file_path)
        
        # 50% 진행 상태 업데이트
        processing_files[file_id]["progress"] = 50
        time.sleep(0.5)  # 진행 상태 표시 효과
        
        # 처리 결과에 따라 상태 업데이트
        if chunk_count > 0:
            # 처리 성공
            processing_files[file_id] = {
                "status": "completed",
                "filename": filename,
                "doc_id": doc_info.get("doc_id", "unknown"),
                "chunk_count": chunk_count,
                "title": doc_info.get("title", filename),
                "completion_time": time.time(),
                "progress": 100
            }
            logger.info(f"파일 처리 완료: {filename} (ID: {file_id}, 문서 ID: {doc_info.get('doc_id', 'unknown')})")
        else:
            # 처리 실패
            processing_files[file_id] = {
                "status": "failed",
                "filename": filename,
                "error": "문서 처리 실패: 생성된 청크가 없습니다.",
                "completion_time": time.time(),
                "progress": 100
            }
            logger.error(f"파일 처리 실패: {filename} (ID: {file_id}) - 생성된 청크가 없습니다.")
            
    except Exception as e:
        # 예외 발생 시 처리
        processing_files[file_id] = {
            "status": "failed",
            "filename": filename,
            "error": str(e),
            "completion_time": time.time(),
            "progress": 100
        }
        logger.error(f"파일 처리 중 예외 발생: {filename} (ID: {file_id}) - {str(e)}")
        
    finally:
        # 임시 파일 삭제
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"임시 파일 삭제 중 오류: {file_path} - {str(e)}")

# Dash 앱 초기화
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# 앱 제목 설정
app.title = "RAG 파일 등록 대시보드"

# 레이아웃 컴포넌트

# 상단 헤더
header = dbc.Row([
    dbc.Col(html.H1("RAG 파일 등록 대시보드", className="text-primary"), width=12),
    dbc.Col(html.P("문서를 업로드하여 벡터 DB에 등록하고 관리합니다."), width=12),
    html.Hr()
], className="mb-4 mt-4")

# 파일 업로드 컴포넌트
upload_component = dbc.Card([
    dbc.CardHeader(html.H4("파일 업로드")),
    dbc.CardBody([
        dcc.Upload(
            id='upload-files',
            children=html.Div([
                html.P('파일을 여기에 끌어다 놓거나 클릭하여 선택하세요'),
                html.P('지원 형식: PDF, DOCX, TXT, MD, EML')
            ]),
            style={
                'width': '100%',
                'height': '150px',
                'lineHeight': '150px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px 0'
            },
            # 여러 파일 업로드 허용
            multiple=True
        ),
        html.Div(id='upload-status')
    ])
], className="mb-4")

# 진행 중인 처리 상태 표시 컴포넌트
processing_status = dbc.Card([
    dbc.CardHeader(html.H4("처리 상태")),
    dbc.CardBody([
        html.Div(id='processing-status'),
        dcc.Interval(
            id='interval-component',
            interval=1000,  # 1초마다 업데이트
            n_intervals=0
        )
    ])
], className="mb-4")

# 등록된 파일 목록 컴포넌트
file_list = dbc.Card([
    dbc.CardHeader(html.H4("등록된 파일 목록")),
    dbc.CardBody([
        html.Div(id='file-list'),
        dcc.Interval(
            id='file-list-interval',
            interval=3000,  # 3초마다 업데이트
            n_intervals=0
        )
    ])
], className="mb-4")

# 청크 목록 표시 컴포넌트
chunk_list = dbc.Card([
    dbc.CardHeader(html.H4("청크 목록")),
    dbc.CardBody([
        html.Div(id='chunk-info', children=[
            html.P('파일을 선택하면 청크 목록이 표시됩니다.')
        ]),
        html.Div(id='chunk-list')
    ])
])

# 메인 레이아웃
app.layout = dbc.Container([
    header,
    dbc.Row([
        dbc.Col([
            upload_component,
            processing_status
        ], width=6),
        dbc.Col([
            file_list
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            chunk_list
        ], width=12)
    ]),
    dcc.Store(id='selected-file')
], fluid=True)

# 콜백 함수

@app.callback(
    Output('upload-status', 'children'),
    Input('upload-files', 'contents'),
    State('upload-files', 'filename'),
    State('upload-files', 'last_modified')
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    """파일 업로드 처리 콜백"""
    if list_of_contents is None:
        raise PreventUpdate
    
    upload_statuses = []
    
    for content, name, date in zip(list_of_contents, list_of_names, list_of_dates):
        try:
            # 파일 확장자 확인
            ext = name.lower().split('.')[-1]
            if ext not in ['pdf', 'docx', 'txt', 'md', 'eml']:
                upload_statuses.append(
                    dbc.Alert(f"지원하지 않는 파일 형식입니다: {name}", color="danger")
                )
                continue
            
            # 고유 ID 생성
            file_id = str(uuid.uuid4())
            
            # 파일 데이터 파싱 (Base64 디코딩)
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            
            # 임시 파일로 저장
            temp_dir = os.path.join(get_project_root(), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            temp_file_path = os.path.join(temp_dir, name)
            
            with open(temp_file_path, 'wb') as f:
                f.write(decoded)
            
            # 백그라운드 쓰레드에서 파일 처리 시작
            thread = threading.Thread(
                target=process_file_async,
                args=(file_id, temp_file_path, name)
            )
            thread.daemon = True  # 메인 프로세스 종료 시 쓰레드도 종료
            thread.start()
            
            upload_statuses.append(
                dbc.Alert(f"파일 업로드 성공: {name}", color="success")
            )
            
        except Exception as e:
            upload_statuses.append(
                dbc.Alert(f"파일 처리 중 오류 발생: {name} - {str(e)}", color="danger")
            )
    
    return upload_statuses

@app.callback(
    Output('processing-status', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_processing_status(n):
    """처리 상태 업데이트 콜백"""
    if not processing_files:
        return html.P("처리 중인 파일이 없습니다.")
    
    status_cards = []
    
    for file_id, status in list(processing_files.items()):
        filename = status.get("filename", "알 수 없음")
        process_status = status.get("status", "unknown")
        progress = status.get("progress", 0)
        
        if process_status == "processing":
            elapsed = time.time() - status.get("start_time", time.time())
            
            status_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H5(filename, className="card-title"),
                        html.P(f"처리 중... ({elapsed:.1f}초)", className="card-text"),
                        dbc.Progress(value=progress, animated=True, striped=True),
                        html.Div(className="spinner-border text-primary mt-2", style={"width": "2rem", "height": "2rem"})
                    ])
                ], className="mb-2")
            )
        
        elif process_status == "completed":
            # 완료된 항목은 일정 시간 후 제거 (UI에서만)
            if "completion_time" in status and (time.time() - status["completion_time"]) > 5:
                continue
                
            status_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H5(filename, className="card-title"),
                        html.P(f"처리 완료: {status.get('chunk_count', 0)}개 청크", className="card-text text-success"),
                        dbc.Progress(value=100)
                    ])
                ], className="mb-2", color="success", outline=True)
            )
        
        elif process_status == "failed":
            # 실패한 항목은 일정 시간 후 제거 (UI에서만)
            if "completion_time" in status and (time.time() - status["completion_time"]) > 10:
                continue
                
            status_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H5(filename, className="card-title"),
                        html.P(f"처리 실패: {status.get('error', '알 수 없는 오류')}", className="card-text text-danger"),
                        dbc.Progress(value=100, color="danger")
                    ])
                ], className="mb-2", color="danger", outline=True)
            )
    
    return html.Div(status_cards)

@app.callback(
    Output('file-list', 'children'),
    Input('file-list-interval', 'n_intervals')
)
def update_file_list(n):
    """등록된 파일 목록 업데이트 콜백"""
    try:
        # 벡터 DB에서 문서 목록 가져오기
        documents = vector_db.get_all_documents()
        
        if not documents:
            return html.P("등록된 파일이 없습니다.")
        
        # 문서 목록을 데이터프레임으로 변환
        doc_list = []
        for doc_id, doc_info in documents.items():
            doc_info['doc_id'] = doc_id
            doc_list.append(doc_info)
            
        df = pd.DataFrame(doc_list)
        
        # 파일 경로에서 파일명만 추출
        df['filename'] = df['file_path'].apply(lambda x: os.path.basename(x) if x else 'N/A')
        
        # 테이블 컬럼 설정
        columns = [
            {"name": "문서 제목", "id": "title"},
            {"name": "파일명", "id": "filename"},
            {"name": "청크 수", "id": "chunk_count"},
            {"name": "등록일", "id": "created_at"}
        ]
        
        # 필요한 필드만 선택하여 데이터 테이블용 데이터 생성
        table_data = []
        for _, row in df.iterrows():
            table_data.append({
                "doc_id": row.get("doc_id"),
                "title": row.get("title", "제목 없음"),
                "filename": row.get("filename", "N/A"),
                "chunk_count": row.get("chunk_count", 0),
                "created_at": row.get("created_at", "N/A")
            })
        
        # 데이터 테이블 생성
        table = dash_table.DataTable(
            id='document-table',
            columns=columns,
            data=table_data,
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'whiteSpace': 'normal',
                'height': 'auto'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            row_selectable='single',
            selected_rows=[],
            page_size=10
        )
        
        return html.Div([
            table,
            html.P(f"총 {len(documents)}개 문서가 등록되어 있습니다.", className="mt-2 text-info")
        ])
        
    except Exception as e:
        logger.error(f"파일 목록 업데이트 중 오류: {str(e)}")
        return html.P(f"파일 목록을 가져오는 중 오류가 발생했습니다: {str(e)}")

@app.callback(
    [Output('chunk-info', 'children'),
     Output('chunk-list', 'children'),
     Output('selected-file', 'data')],
    [Input('document-table', 'selected_rows')],
    [State('document-table', 'data')]
)
def display_chunk_list(selected_rows, table_data):
    """선택한 파일의 청크 목록 표시 콜백"""
    if not selected_rows or not table_data:
        raise PreventUpdate
    
    # 선택한 행의 문서 정보
    row_idx = selected_rows[0]
    doc_data = table_data[row_idx]
    doc_id = doc_data.get('doc_id')
    title = doc_data.get('title', 'N/A')
    
    if not doc_id:
        return html.P("문서 ID를 찾을 수 없습니다."), None, None
    
    try:
        # 문서 정보 가져오기
        doc_info = vector_db.get_document_by_id(doc_id)
        
        if not doc_info:
            return html.P(f"문서 정보를 찾을 수 없습니다: {doc_id}"), None, None
        
        # 문서 청크 가져오기
        chunks = []
        chunk_data = vector_db.get_all_chunks()
        
        for chunk_id, chunk_info in chunk_data.items():
            if chunk_info.get('doc_id') == doc_id:
                chunk_info['chunk_id'] = chunk_id
                chunks.append(chunk_info)
        
        # 청크 정보 헤더
        chunk_info_header = html.Div([
            html.H5(f"문서: {title}"),
            html.P(f"파일: {os.path.basename(doc_info.get('file_path', 'N/A'))}"),
            html.P(f"청크 수: {len(chunks)}개"),
            html.Hr()
        ])
        
        if not chunks:
            return chunk_info_header, html.P("이 문서에는 청크가 없습니다."), doc_id
        
        # 청크를 인덱스 순으로 정렬
        chunks.sort(key=lambda x: x.get('chunk_index', 0))
        
        # 청크 목록 테이블에 표시될 데이터 생성
        chunk_records = []
        for chunk in chunks:
            # 청크 텍스트는 필요한 경우에만 로드
            text = chunk.get('text', '텍스트 없음')
            # 미리보기용으로 텍스트 일부만 표시
            preview = text[:100] + ('...' if len(text) > 100 else '')
            
            chunk_records.append({
                'chunk_id': chunk.get('chunk_id', 'N/A'),
                'chunk_index': chunk.get('chunk_index', 0),
                'text_length': len(text),
                'preview': preview
            })
        
        # 청크 목록 테이블 생성
        chunk_table = dash_table.DataTable(
            id='chunk-table',
            columns=[
                {"name": "청크 번호", "id": "chunk_index"},
                {"name": "텍스트 길이", "id": "text_length"},
                {"name": "미리보기", "id": "preview"}
            ],
            data=chunk_records,
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'whiteSpace': 'normal',
                'height': 'auto'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            page_size=5
        )
        
        return chunk_info_header, chunk_table, doc_id
        
    except Exception as e:
        logger.error(f"청크 목록 표시 중 오류: {str(e)}")
        return html.P(f"청크 정보를 가져오는 중 오류가 발생했습니다: {str(e)}"), None, None

# 앱 실행 (메인 함수)
def main():
    """메인 함수"""
    # 앱 실행
    app.run(debug=True, port=8050)

if __name__ == "__main__":
    main()
