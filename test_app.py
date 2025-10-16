# test_app.py
import streamlit as st
import requests
import uuid

# FastAPI 서버 주소
API_URL = "http://127.0.0.1:8000/chat"

# Streamlit UI 설정
st.title("🤖 AI 문진 챗봇 시뮬레이터")
st.caption("카카오톡 챗봇을 테스트하기 위한 웹페이지입니다.")

# 세션 상태 초기화
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
    st.session_state.messages = []
    # 초기 메시지 전송
    try:
        initial_payload = {"user_id": st.session_state.user_id, "message": "시작"}
        response = requests.post(API_URL, json=initial_payload)
        response.raise_for_status()
        initial_data = response.json()
        
        st.session_state.messages.append({"role": "assistant", "content": initial_data["next_question"]})
        if initial_data.get("options"):
            st.session_state.options = initial_data["options"]
        else:
            st.session_state.options = []

    except requests.exceptions.RequestException as e:
        st.error(f"서버 연결 오류: {e}")
        st.session_state.messages.append({"role": "assistant", "content": "서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인하세요."})


# 이전 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
def handle_input(user_input):
    # 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 서버에 요청 전송
    try:
        payload = {"user_id": st.session_state.user_id, "message": user_input}
        response = requests.post(API_URL, json=payload)
        response.raise_for_status() # 오류 발생 시 예외 처리
        data = response.json()

        # 챗봇 응답 표시
        bot_response = data["next_question"]
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        
        # 다음 선택지 업데이트
        st.session_state.options = data.get("options", [])

    except requests.exceptions.RequestException as e:
        st.error(f"오류: {e}")
        st.session_state.messages.append({"role": "assistant", "content": f"요청 중 오류가 발생했습니다: {e}"})
        st.session_state.options = []
    
    # 입력창 초기화를 위해 스크립트 재실행
    st.rerun()

# 입력 방식 결정: 선택지 또는 자유 텍스트
if "options" in st.session_state and st.session_state.options:
    st.write("답변을 선택해주세요:")
    for option in st.session_state.options:
        if st.button(option, key=option):
            handle_input(option)
else:
    if prompt := st.chat_input("메시지를 입력하세요..."):
        handle_input(prompt)
