# gemini_client.py
import os
import traceback  # 상세한 오류 로깅을 위해 추가
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키 설정
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "YOUR_API_KEY_HERE":
    raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")

genai.configure(api_key=api_key)

# 모델 초기화
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_dynamic_question(symptom: str, history: list):
    """
    환자의 증상과 이전 대화 내용을 바탕으로 동적 심화 질문을 생성합니다.
    성공 시 API 응답 객체 전체를, 실패 시 에러 메시지 문자열을 반환합니다.
    """
    try:
        prompt = f"""
        환자가 다음과 같은 증상을 호소하고 있습니다: '{symptom}'
        지금까지의 대화 내용입니다:
        {history}
        
        환자의 상태를 더 명확히 파악하기 위한 간단하고 핵심적인 추가 질문을 하나만 생성해주세요.
        질문은 한국어로, 존댓말로, 한 문장으로 만들어주세요.
        """
        
        response = model.generate_content(prompt)
        return response
    except Exception:
        print("Gemini API 'generate_dynamic_question' 호출 중 오류 발생:")
        traceback.print_exc()  # 전체 Traceback 출력
        return "죄송합니다, AI 모델 호출 중 오류가 발생했습니다. 다음 질문으로 넘어가겠습니다."

def summarize_conversation(history: list):
    """
    전체 대화 내용을 바탕으로 PA 노트 형식의 요약을 생성합니다.
    성공 시 API 응답 객체 전체를, 실패 시 에러 메시지 문자열을 반환합니다.
    """
    try:
        prompt = f"""
        다음은 환자와의 문진 대화 내용이야.
        {history}

        위 대화 내용을 바탕으로 의사가 보기 편한 PA Note 형식으로 요약해줘.
        Chief Complaint, Present Illness, Past Medical History 등을 구분하여 작성해.
        양식은 아래와 같아.

Chief Complaint
- [환자의 주호소 증상]

Present Illness
- [첫 번째 상세 내용]
- [두 번째 상세 내용]
- [세 번째 상세 내용]
...

Past Medical History
- [첫 번째 과거력]
- [두 번째 과거력]
...
        """
        response = model.generate_content(prompt)
        return response
    except Exception:
        print("Gemini API 'summarize_conversation' 호출 중 오류 발생:")
        traceback.print_exc()  # 전체 Traceback 출력
        return "대화 내용을 요약하는 데 실패했습니다."
