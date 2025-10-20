# 개발 진행 상황 (PROGRESS.md)

이 문서는 AI 문진 챗봇 프로젝트의 개발 과정을 상세히 기록하여, 각 단계의 목표, 구현 내용, 발생한 문제 및 해결 과정을 추적합니다.

---

### 단계 1: 프로젝트 초기 설정 (2025년 10월 5일)

- **요청:** `README.md`를 기반으로 AI 문진 챗봇 개발 시작.
- **파일:** `requirements.txt`, `main.py`, `venv`
- **내용:**
    - **`requirements.txt`**: 프로젝트의 기본 라이브러리 의존성을 정의. (`fastapi`, `uvicorn`, `pyyaml`, `google-generativeai`)
    - **`main.py`**: FastAPI 웹 서버의 진입점. "Hello World"를 반환하는 기본 `/` 엔드포인트를 구현하여 서버 작동을 확인.
    - **`venv`**: Python 가상 환경. 시스템 패키지와의 충돌을 방지하고 프로젝트별 의존성을 격리하기 위해 생성. 모든 라이브러리는 이 가상 환경 내에 설치됨.

---

### 단계 2: 핵심 시나리오 엔진 구현

- **요청:** YAML 파일 기반의 문진 시나리오 엔진 구현.
- **파일:** `scenario_engine.py`, `main.py`
- **내용:**
    - **`scenario_engine.py`**:
        - **역할**: YAML 파일을 읽어 문진 시나리오를 객체로 관리하는 핵심 엔진.
        - **코드**: `ScenarioManager` 클래스가 `scenarios` 폴더 내의 모든 `.yaml` 파일을 자동으로 로드. `Scenario` 클래스는 각 시나리오의 질문(node)들을 관리.
    - **`main.py` 수정**:
        - **역할**: 시나리오 엔진과 FastAPI를 연동.
        - **코드**: `/chat` 엔드포인트를 추가. 사용자별 대화 상태를 추적하기 위한 인메모리 딕셔너리 `user_sessions`를 도입. 사용자가 "시작"을 입력하면 `gastroenteritis` 시나리오의 첫 질문을 반환하도록 초기 로직 구현.

---

### 단계 3: 멀티 시나리오 지원 확장

- **요청:** `scenarios` 폴더 내의 여러 질환을 모두 지원.
- **파일:** `main.py`
- **내용:**
    - **`main.py` 수정**:
        - **역할**: 사용자가 여러 시나리오 중 하나를 선택하여 문진을 시작할 수 있도록 확장.
        - **코드**: 대화 시작 시, `ScenarioManager`에 로드된 모든 시나리오의 이름을 사용자에게 선택지로 제공. 사용자가 선택한 시나리오로 문진을 시작하도록 로직 변경.

---

### 단계 4: 테스트 환경 개선 (Streamlit 시뮬레이터 도입)

- **요청:** `curl`을 사용하는 번거로운 테스트 방식 개선.
- **파일:** `test_app.py`, `requirements.txt`
- **내용:**
    - **`requirements.txt` 수정**: `streamlit`, `requests` 라이브러리 추가.
    - **`test_app.py`**:
        - **역할**: FastAPI 서버와 실시간으로 통신하는 웹 기반 채팅 UI를 제공하여, 실제 사용자 경험과 유사한 테스트 환경을 구축.
        - **코드**: Streamlit을 사용하여 채팅 UI를 구현. 사용자가 메시지를 입력하거나 버튼을 클릭하면 `requests` 라이브러리를 통해 백엔드 `/chat` 엔드포인트로 API 요청을 전송하고, 응답을 받아 화면에 표시.

---

### 단계 5: Gemini API 연동 및 집중 디버깅

- **요청:** Gemini API 연동 및 반복적인 `500 Internal Server Error` 해결.
- **파일:** `gemini_client.py`, `usage_tracker.py`, `.env`, `main.py`
- **내용:**
    - **`.env`**:
        - **역할**: `GEMINI_API_KEY`와 같은 민감한 정보를 코드와 분리하여 안전하게 보관.
    - **`gemini_client.py`**:
        - **역할**: Google Gemini API와의 통신을 담당.
        - **코드**: `.env` 파일에서 API 키를 로드하여 Gemini 모델(`gemini-1.5-flash`)을 초기화. 동적 심화 질문 생성(`generate_dynamic_question`) 및 PA 노트 요약(`summarize_conversation`) 함수를 구현.
    - **`usage_tracker.py`**:
        - **역할**: Gemini API의 토큰 사용량을 추적하고 예상 비용을 계산.
        - **코드**: `UsageTracker` 클래스가 API 응답의 `usage_metadata`를 분석하여 토큰 수를 누적하고, 미리 정의된 단가에 따라 비용을 계산하는 리포트를 생성.
    - **`main.py` 수정 및 디버깅**:
        - **오류**: `UnboundLocalError`, `KeyError` 등 다양한 런타임 오류 발생.
        - **해결**:
            - `condition` 타입의 분기 노드를 처리하는 로직을 추가.
            - 사용자의 이전 답변을 `session["answers"]`에 기록하여 분기 조건에 활용.
            - 옵션에 `next_id`가 없는 경우를 처리하는 로직을 개선.
            - 세션 종료 시 `del` 대신 `.pop()`을 사용하여 `KeyError` 방지.
            - `traceback.print_exc()`를 사용한 상세 로깅을 추가하여 오류의 원인을 명확히 파악.

---

### 단계 6: 모델 변경 및 시나리오 확장

- **요청:** 최신 모델로 변경하고, 신규 시나리오 추가.
- **파일:** `gemini_client.py`, `scenarios/*.yaml`
- **내용:**
    - **`gemini_client.py` 수정**: 초기화 모델을 `gemini-1.5-flash`에서 `gemini-2.5-flash`로 변경.
    - **`scenarios/*.yaml` 추가**: `indigestion.yaml`, `uti.yaml`, `skin.yaml` 파일 생성 및 기본 문진 내용 작성.

---

### 단계 7: 테스트 배포 및 사용자 경험 개선

- **요청:** 외부 테스트를 위한 임시 배포 및 사용성 개선.
- **파일:** `deploy_app.py`, `.gitignore`, `usage_tracker.py`, `main.py`
- **내용:**
    - **`deploy_app.py`**:
        - **역할**: Streamlit Cloud 배포를 위한 전용 프론트엔드 앱.
        - **코드**: 기존 `test_app.py`를 복사하고, 백엔드 API 주소를 `ngrok` URL로 쉽게 교체할 수 있도록 상단에 변수로 분리.
    - **`.gitignore`**:
        - **역할**: Git이 추적하지 말아야 할 파일(예: `.env`, `venv`, `__pycache__`)을 지정하여, 민감 정보나 불필요한 파일이 원격 저장소에 올라가는 것을 방지.
    - **보안 사고 대응**:
        - **오류**: `.env` 파일이 실수로 GitHub에 커밋되어 API 키가 노출됨.
        - **해결**: `git filter-branch` 명령으로 Git의 모든 히스토리에서 `.env` 파일을 완전히 삭제. `.gitignore`를 추가한 후, 수정된 히스토리를 강제 푸시하여 원격 저장소를 덮어씀.
    - **`usage_tracker.py` 수정**: `gemini-2.5-flash` 모델의 최신 가격 정책을 반영하여 비용 계산 정확도를 높임.
    - **`main.py` 수정 (UX 개선)**:
        - **역할**: PA 노트 생성 시 발생하는 지연 시간 동안 사용자가 시스템 멈춤으로 오인하는 문제 해결.
        - **코드**: `final` 노드에 도달하면 PA 노트를 즉시 생성하지 않고, "원장님께 내용을 전달중입니다..." 라는 안내 메시지를 먼저 반환. 사용자의 다음 입력이 있을 때 실제 PA 노트 생성을 시작하도록 로직을 2단계로 분리.

---

### 단계 8: 확장 가능한 카카오톡 연동 시스템 구축

- **요청:** 단일 서버로 여러 병원의 카카오톡 챗봇을 운영할 수 있는 '멀티테넌시' 구조 구축.
- **파일:** `database.py`, `models.py`, `crud.py`, `init_db.py`, `kakao_integration.py`, `main.py`, `core_logic.py`
- **내용:**
    - **DB 환경 구축**:
        - **`database.py`**: SQLite 데이터베이스 연결을 위한 SQLAlchemy 엔진 및 세션 설정.
        - **`models.py`**: `Clinic` 테이블의 스키마(병원 ID, 이름 등)를 SQLAlchemy 모델로 정의.
        - **`crud.py`**: `clinic_id`로 DB에서 병원 정보를 조회하는 `get_clinic_by_clinic_id` 함수 구현.
        - **`init_db.py`**: DB 테이블을 생성하고 파일럿 병원 정보를 초기 데이터로 삽입하는 일회성 스크립트.
        - **오류**: `ModuleNotFoundError` (라이브러리 미설치), `ImportError` (상대 경로) 발생.
        - **해결**: `pip install sqlalchemy` 실행 및 `models.py`, `crud.py`의 임포트 구문을 절대 경로로 수정하여 해결.
    - **카카오톡 연동 구현**:
        - **`kakao_integration.py`**:
            - **역할**: 카카오톡 스킬 API의 요청/응답 처리.
            - **코드**: 카카오톡 API의 JSON 형식을 Pydantic 모델로 정의. `clinic_id`를 쿼리 파라미터로 받는 `/kakaotalk/callback` 엔드포인트를 구현.
    - **아키텍처 리팩토링**:
        - **오류**: `main.py`와 `kakao_integration.py`가 서로를 임포트하는 '순환 참조(Circular Import)' 오류 발생.
        - **`core_logic.py`**:
            - **역할**: 순환 참조를 해결하고 코드 재사용성을 높이기 위해, 여러 파일이 공통으로 사용하는 핵심 로직을 분리.
            - **코드**: `process_chat_message` 함수와 `user_sessions` 딕셔너리를 이 파일로 이동.
        - **`main.py`, `kakao_integration.py` 수정**: 두 파일 모두 `core_logic.py`를 임포트하도록 수정하여 순환 참조를 해결하고 의존성 구조를 개선.

---