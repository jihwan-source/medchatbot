from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scenario_engine import scenario_manager
from gemini_client import generate_dynamic_question, summarize_conversation
from usage_tracker import UsageTracker
from typing import List
import traceback  # [디버깅용] 상세한 오류 출력을 위해 추가

app = FastAPI()

# ... (이전 코드와 동일) ...
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
# ... (이전 코드와 동일) ...

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # [디버깅용] 함수 전체를 try-except로 감싸서 모든 오류를 포착
    try:
        user_id = request.user_id
        user_message = request.message.strip()

        # 1. 기존 대화가 있는지 확인
        if user_id in user_sessions:
            session = user_sessions[user_id]
            usage_tracker = session["usage_tracker"]
            scenario = scenario_manager.get_scenario(session["scenario_id"])
            current_node = scenario.get_node(session["current_node_id"])

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
                    # 옵션에 next_id가 있으면 그것을 사용 (분기용)
                    next_node_id = selected_option.get("next_id")
                    # 옵션에 next_id가 없으면, 노드 레벨의 next_id를 사용 (단순 진행용)
                    if not next_node_id:
                        next_node_id = current_node.get("next_id")

                if not next_node_id:
                    question_text = f"잘못된 선택입니다. 다시 선택해주세요.\n\n{current_node['text']}"
                    session["history"].append(f"챗봇: {question_text}")
                    return ChatResponse(
                        next_question=question_text,
                        options=[opt["text"] for opt in current_node.get("options", [])]
                    )
            
            elif current_node.get("type") == "multiple_choice":
                # multiple_choice는 답변 내용과 상관없이 정해진 다음 노드로 이동
                next_node_id = current_node.get("next_id")

            elif current_node.get("type") == "free_text":
                response = generate_dynamic_question(user_message, session["history"])
                
                if isinstance(response, str):
                    return ChatResponse(next_question=response, options=[])

                usage_tracker.update_usage(response)
                dynamic_question = response.text.strip()
                
                session["original_next_node_id"] = current_node.get("next_id")
                session["dynamic_question_pending"] = True
                
                session["history"].append(f"챗봇 (AI): {dynamic_question}")
                return ChatResponse(next_question=dynamic_question, options=[])

            # --- 조건 분기 노드 처리 루프 ---
            # next_node가 표시할 텍스트가 없는 논리 노드(예: condition)인 경우,
            # 실제 질문 노드가 나올 때까지 계속 다음 노드를 찾아나감.
            next_node = scenario.get_node(next_node_id)
            while next_node.get("type") == "condition":
                condition_data = next_node.get("check_answer", {})
                node_to_check = condition_data.get("node_id")
                text_to_find = condition_data.get("contains")

                previous_answer = session.get("answers", {}).get(node_to_check, "")

                if text_to_find in previous_answer:
                    next_node_id = next_node.get("next_id_if_true")
                else:
                    next_node_id = next_node.get("next_id_if_false")
                
                if not next_node_id:
                    raise HTTPException(status_code=500, detail=f"Condition node '{next_node['id']}' has no valid next node.")
                
                next_node = scenario.get_node(next_node_id)
            # --- 루프 끝 ---

            if next_node.get("type") == "final":
                summary_response = summarize_conversation(session["history"])
                if isinstance(summary_response, str):
                    summary_text = summary_response
                else:
                    usage_tracker.update_usage(summary_response)
                    summary_text = summary_response.text.strip()

                usage_report = usage_tracker.get_summary_report()
                final_text = f"{next_node['text']}\n\n[생성된 PA 노트 초안]\n{summary_text}\n\n---\n\n{usage_report}"
                
                # 세션 정리 (오류 방지를 위해 pop 사용)
                user_sessions.pop(user_id, None)
                return ChatResponse(next_question=final_text)

            user_sessions[user_id]["current_node_id"] = next_node_id
            
            question_text = next_node["text"]
            options = [opt["text"] for opt in next_node.get("options", [])]
            session["history"].append(f"챗봇: {question_text}")

            return ChatResponse(next_question=question_text, options=options)

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
                    "answers": {}, # 답변 기록용 딕셔너리 초기화
                    "usage_tracker": UsageTracker()
                }
                
                question_text = initial_node["text"]
                options = [opt["text"] for opt in initial_node.get("options", [])]
                user_sessions[user_id]["history"].append(f"챗봇: {question_text}")

                return ChatResponse(next_question=question_text, options=options)
            else:
                available_scenarios = list(scenario_name_to_id.keys())
                return ChatResponse(
                    next_question="안녕하세요! AI 문진 챗봇입니다. 어떤 증상으로 오셨나요?",
                    options=available_scenarios
                )
    except Exception as e:
        print("\n\n--- [오류 발생] ---")
        traceback.print_exc()
        print("--- [오류 끝] ---\n\n")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
