# kakao_integration.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Any

import crud
from database import get_db
# main.py에서 핵심 로직 함수를 가져옵니다.
from main import process_chat_message

# --- Pydantic 모델 정의 (카카오톡 스킬 API 형식에 맞춤) ---
# ... (Pydantic models remain the same) ...
class User(BaseModel):
    id: str

class UserRequest(BaseModel):
    user: User
    utterance: str

# 응답 모델
class SimpleText(BaseModel):
    text: str

class QuickReply(BaseModel):
    label: str
    action: str = "message"
    messageText: str

class SkillTemplate(BaseModel):
    outputs: List[Dict[str, Any]]
    quickReplies: List[QuickReply] = []

class SkillResponse(BaseModel):
    version: str = "2.0"
    template: SkillTemplate
# ... (Pydantic models remain the same) ...


# --- FastAPI 라우터 설정 ---
router = APIRouter()

@router.post("/kakaotalk/callback", response_model=SkillResponse)
async def handle_kakaotalk_callback(request: UserRequest, clinic_id: str, db: Session = Depends(get_db)):
    """
    카카오톡 챗봇의 요청을 받아 처리하고 응답을 반환하는 메인 핸들러
    """
    # 1. clinic_id로 병원 정보 조회
    clinic = crud.get_clinic_by_clinic_id(db, clinic_id=clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail=f"Clinic '{clinic_id}' not found.")

    # 2. 카카오톡 사용자 ID와 발화 내용 추출
    kakao_user_id = request.user.id
    user_message = request.utterance

    # 3. 멀티테넌시를 위한 고유 세션 ID 생성 (clinic_id + kakao_id)
    session_user_id = f"{clinic_id}-{kakao_user_id}"

    # 4. 핵심 챗봇 로직 호출
    response_data = process_chat_message(
        user_id=session_user_id,
        user_message=user_message,
        clinic_name=clinic.clinic_name
    )
    next_question = response_data["next_question"]
    options = response_data["options"]

    # 5. 카카오톡 응답 형식으로 변환
    simple_text = SimpleText(text=next_question).dict()
    quick_replies = [
        QuickReply(label=opt, messageText=opt) for opt in options
    ]

    return SkillResponse(
        template=SkillTemplate(
            outputs=[{"simpleText": simple_text}],
            quickReplies=quick_replies
        )
    )
