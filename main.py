from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from kakao_integration import router as kakao_router
from core_logic import process_chat_message

app = FastAPI()

# 카카오톡 연동 라우터 추가
app.include_router(kakao_router)

# Pydantic 모델 정의
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    next_question: str
    options: List[str] = []

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Streamlit 테스트 앱을 위한 엔드포인트.
    핵심 로직은 core_logic.py의 process_chat_message 함수를 호출합니다.
    """
    response_data = process_chat_message(request.user_id, request.message)
    return ChatResponse(**response_data)
