# ... (imports remain the same) ...
from kakao_integration import router as kakao_router

app = FastAPI()

# 카카오톡 연동 라우터 추가
app.include_router(kakao_router)

# ... (scenario_name_to_id and Pydantic models remain the same) ...
scenario_name_to_id = {
    scenario.name: scenario_id
    for scenario_id, scenario in scenario_manager.scenarios.items()
}
class ChatRequest(BaseModel):
    user_id: str
    message: str
class ChatResponse(BaseModel):
    next_question: str
    options: List[str] = []
user_sessions = {}
# ... (user_sessions remains the same) ...


def process_chat_message(user_id: str, user_message: str, clinic_name: str = None):
    """
    사용자 메시지를 처리하는 핵심 챗봇 로직.
    Streamlit, 카카오톡 등 다양한 채널에서 재사용됩니다.
    """
    try:
        user_message = user_message.strip()

        # 1. 기존 대화가 있는지 확인
        if user_id in user_sessions:
            session = user_sessions[user_id]
            usage_tracker = session["usage_tracker"]
            scenario = scenario_manager.get_scenario(session["scenario_id"])
            current_node = scenario.get_node(session["current_node_id"])

            # 만약 현재 노드가 'final' 타입이면, 사용자가 안내 메시지를 보고 응답한 것이므로
            # 바로 PA 노트 생성 로직을 실행합니다.
            if current_node.get("type") == "final":
                summary_response = summarize_conversation(session["history"])
                if isinstance(summary_response, str):
                    summary_text = summary_response
                else:
                    usage_tracker.update_usage(summary_response)
                    summary_text = summary_response.text.strip()

                usage_report = usage_tracker.get_summary_report()
                final_text = f"{current_node['text']}\n\n[생성된 PA 노트 초안]\n{summary_text}\n\n---\n\n{usage_report}"
                
                # 세션 정리
                user_sessions.pop(user_id, None)
                return {"next_question": final_text, "options": []}

            session["history"].append(f"환자: {user_message}")
            # 사용자의 답변을 ID별로 기록 (조건 분기용)
            session["answers"][current_node["id"]] = user_message

            next_node_id = None

            if session.get("dynamic_question_pending"):
                session["dynamic_question_pending"] = False
                next_node_id = session["original_next_node_id"]
            
            elif current_node.get("type") == "buttons":
                selected_option = None
                for option in current_node.get("options", []):
                    if option["text"] == user_message:
                        selected_option = option
                        break

                if selected_option:
                    next_node_id = selected_option.get("next_id")
                    if not next_node_id:
                        next_node_id = current_node.get("next_id")

                if not next_node_id:
                    question_text = f"잘못된 선택입니다. 다시 선택해주세요.\n\n{current_node['text']}"
                    session["history"].append(f"챗봇: {question_text}")
                    return {
                        "next_question": question_text,
                        "options": [opt["text"] for opt in current_node.get("options", [])]
                    }
            
            elif current_node.get("type") == "multiple_choice":
                next_node_id = current_node.get("next_id")

            elif current_node.get("type") == "free_text":
                response = generate_dynamic_question(user_message, session["history"])
                
                if isinstance(response, str):
                    return {"next_question": response, "options": []}

                usage_tracker.update_usage(response)
                dynamic_question = response.text.strip()
                
                session["original_next_node_id"] = current_node.get("next_id")
                session["dynamic_question_pending"] = True
                
                session["history"].append(f"챗봇 (AI): {dynamic_question}")
                return {"next_question": dynamic_question, "options": []}

            next_node = scenario.get_node(next_node_id)
            while next_node and next_node.get("type") == "condition":
                condition_data = next_node.get("check_answer", {})
                node_to_check = condition_data.get("node_id")
                text_to_find = condition_data.get("contains")

                previous_answer = session.get("answers", {}).get(node_to_check, "")

                if text_to_find in previous_answer:
                    next_node_id = next_node.get("next_id_if_true")
                else:
                    next_node_id = next_node.get("next_id_if_false")
                
                if not next_node_id:
                    raise ValueError(f"Condition node '{next_node['id']}' has no valid next node.")
                
                next_node = scenario.get_node(next_node_id)

            if next_node.get("type") == "final":
                user_sessions[user_id]["current_node_id"] = next_node_id
                notice_text = "문진이 모두 완료되었습니다. 원장님께 내용을 전달중입니다..."
                session["history"].append(f"챗봇: {notice_text}")
                return {"next_question": notice_text, "options": []}

            user_sessions[user_id]["current_node_id"] = next_node_id
            
            question_text = next_node["text"]
            options = [opt["text"] for opt in next_node.get("options", [])]
            session["history"].append(f"챗봇: {question_text}")

            return {"next_question": question_text, "options": options}

        # 2. 새 대화 시작
        else:
            if user_message in scenario_name_to_id:
                scenario_id = scenario_name_to_id[user_message]
                scenario = scenario_manager.get_scenario(scenario_id)
                
                initial_node = scenario.get_initial_node()
                user_sessions[user_id] = {
                    "scenario_id": scenario_id,
                    "current_node_id": initial_node["id"],
                    "history": [],
                    "answers": {},
                    "usage_tracker": UsageTracker()
                }
                
                question_text = initial_node["text"]
                options = [opt["text"] for opt in initial_node.get("options", [])]
                user_sessions[user_id]["history"].append(f"챗봇: {question_text}")

                return {"next_question": question_text, "options": options}
            else:
                available_scenarios = list(scenario_name_to_id.keys())
                greeting = f"안녕하세요! {clinic_name or 'AI 문진 챗봇'}입니다. 어떤 증상으로 오셨나요?"
                return {
                    "next_question": greeting,
                    "options": available_scenarios
                }
    except Exception as e:
        print("\n\n--- [오류 발생 in process_chat_message] ---")
        traceback.print_exc()
        print("--- [오류 끝] ---\n\n")
        # 사용자에게 보여줄 일반적인 오류 메시지
        error_message = "죄송합니다, 시스템에 예상치 못한 오류가 발생했습니다. 대화를 다시 시작해주세요."
        # 세션이 있다면 정리
        user_sessions.pop(user_id, None)
        return {"next_question": error_message, "options": ["시작"]}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response_data = process_chat_message(request.user_id, request.message)
    return ChatResponse(**response_data)
