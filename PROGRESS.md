# 개발 진행 상황 (PROGRESS.md)

이 문서는 AI 문진 챗봇 프로젝트의 개발 과정을 시간 순서대로 기록합니다.

---

### 단계 1: 프로젝트 초기 설정 (2025년 10월 5일)

- **요청:** `README.md`를 기반으로 AI 문진 챗봇 개발 시작.
- **작업:**
    1.  `requirements.txt` 파일 생성 (`fastapi`, `uvicorn`, `pyyaml`, `google-generativeai` 명시).
    2.  `main.py` 파일 생성, "Hello World"를 반환하는 기본 FastAPI 서버 구현.
    3.  Python 시스템 패키지 충돌 문제를 해결하기 위해 `venv` 가상 환경 생성 및 활성화.
    4.  가상 환경 내에 모든 라이브러리 설치 및 서버 실행 확인.

---

### 단계 2: 핵심 시나리오 엔진 구현

- **요청:** YAML 파일을 기반으로 문진을 진행하는 시나리오 엔진 구현.
- **작업:**
    1.  `scenarios/gastroenteritis.yaml` 파일을 분석하여 시나리오 구조 파악.
    2.  `scenario_engine.py` 파일 생성:
        - `scenarios` 폴더 내의 모든 `.yaml` 파일을 자동으로 로드하는 `ScenarioManager` 클래스 구현.
        - 각 시나리오를 객체로 관리하는 `Scenario` 클래스 구현.
    3.  `main.py` 수정:
        - `/chat` 엔드포인트 추가.
        - 사용자별 대화 상태를 추적하는 인메모리 `user_sessions` 딕셔너리 추가.
        - 사용자가 "시작"을 입력하면 `gastroenteritis` 시나리오의 첫 질문을 반환하도록 구현.

---

### 단계 3: 멀티 시나리오 지원 확장

- **요청:** `scenarios` 폴더 내의 4가지 질환(`gastroenteritis`, `headache`, `rhinitis`, `uri`)을 모두 지원.
- **작업:**
    1.  `main.py` 수정:
        - 대화 시작 시, `ScenarioManager`에 로드된 모든 시나리오의 이름을 가져와 사용자에게 선택지로 제공.
        - 사용자가 선택한 시나리오로 문진을 시작하도록 로직 변경.
    2.  기존 코드가 이미 모듈식으로 각 YAML 파일을 독립적으로 로드하고 있어, 파일 통합 없이 확장 가능함을 확인.

---

### 단계 4: 테스트 환경 개선 (Streamlit 시뮬레이터 도입)

- **요청:** `curl`을 사용하는 번거로운 테스트 방식 개선.
- **작업:**
    1.  `requirements.txt`에 `streamlit`과 `requests` 라이브러리 추가 및 설치.
    2.  `test_app.py` 파일 생성:
        - FastAPI 서버(`/chat`)와 실시간으로 통신하는 웹 기반 채팅 UI 구현.
        - 대화 기록, 사용자 입력창, 선택지 버튼 등 실제 채팅과 유사한 경험 제공.
    3.  FastAPI 서버(`main.py`)와 Streamlit 앱(`test_app.py`)을 각각 다른 터미널에서 동시에 실행하는 방법 안내.

---

### 단계 5: Gemini API 연동 및 집중 디버깅

- **요청:** `500 Internal Server Error` 해결 및 Gemini API 연동.
- **작업:**
    1.  **API 키 관리:**
        - `python-dotenv` 라이브러리 추가.
        - API 키를 안전하게 보관하기 위한 `.env` 파일 생성.
    2.  **Gemini 클라이언트 구현:**
        - `gemini_client.py` 파일 생성.
        - `.env` 파일에서 API 키를 로드하여 Gemini 모델(`gemini-1.5-flash`)을 초기화하는 로직 구현.
        - 동적 심화 질문 생성(`generate_dynamic_question`) 및 PA 노트 요약(`summarize_conversation`) 함수 구현.
    3.  **API 사용량 추적 기능 추가:**
        - `usage_tracker.py` 파일 생성하여 토큰 사용량 및 예상 비용을 계산하는 `UsageTracker` 클래스 구현.
        - 문진 종료 시, PA 노트와 함께 API 사용량 리포트를 출력하도록 `main.py` 수정.
    4.  **반복적인 `500 Server Error` 디버깅:**
        - **`UnboundLocalError: next_node_id`:** `next_node_id` 변수를 미리 `None`으로 선언하여 해결.
        - **`KeyError: 'text'`:** `uri.yaml`의 `type: condition` 분기 노드를 처리하지 못하는 문제 발견. `main.py`에 `condition` 노드를 해석하고 사용자의 이전 답변을 추적하여 올바른 경로로 분기하는 로직 추가.
        - **`KeyError: 'next_id'`:** `multiple_choice`를 `buttons`로 변경하며 발생한 구조 불일치 문제. `main.py`의 `buttons` 처리 로직을 수정하여, 옵션 자체에 `next_id`가 없는 경우 노드 레벨의 `next_id`를 사용하도록 개선.
        - **`KeyError: 'user_id'`:** 문진 종료 시 이미 삭제된 세션을 다시 삭제하려 할 때 발생. `del` 대신 `.pop()`을 사용하여 안전하게 세션을 제거하도록 수정.
        - **상세 로깅 추가:** 오류의 원인이 터미널에 출력되지 않는 문제를 해결하기 위해, `main.py`, `gemini_client.py`, `usage_tracker.py`에 `traceback.print_exc()`를 사용한 상세 오류 로깅 로직 추가.

---

### 단계 6: 모델 변경 및 시나리오 확장

- **요청:** Gemini 모델을 `gemini-2.5-flash`로 변경하고, 새로운 시나리오 추가.
- **작업:**
    1.  `gemini_client.py`의 모델 초기화 부분을 `gemini-2.5-flash`로 수정.
    2.  사용자 요청에 따라 `indigestion.yaml`, `uti.yaml`, `skin.yaml` 파일 생성 및 기본 문진 내용 작성.
    3.  `multiple_choice` 타입을 모두 단일 선택인 `buttons` 타입으로 변경.

---