# usage_tracker.py
# [테스트용] Gemini API 사용량 및 비용 추적기
import traceback  # 상세한 오류 로깅을 위해 추가

# 참고: Gemini 1.5 Flash 모델의 가격 (2024년 5월 기준)
# - 입력: $0.000125 / 1K tokens
# - 출력: $0.000375 / 1K tokens
# ※ 실제 비용은 Google Cloud의 공식 가격 정책을 항상 확인하세요.
PRICE_INPUT_PER_1K_TOKENS = 0.000125
PRICE_OUTPUT_PER_1K_TOKENS = 0.000375

class UsageTracker:
    """
    API 사용량을 세션 단위로 추적하고 비용을 계산하는 클래스.
    나중에 이 기능을 제거하고 싶다면, 이 클래스를 호출하는 부분만 삭제하면 됩니다.
    """
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def update_usage(self, response):
        """API 응답 객체에서 토큰 사용량을 추출하여 누적합니다."""
        try:
            usage_metadata = response.usage_metadata
            self.total_input_tokens += usage_metadata.prompt_token_count
            self.total_output_tokens += usage_metadata.candidates_token_count
        except Exception:
            print("토큰 사용량 업데이트 중 오류 발생:")
            traceback.print_exc()  # 전체 Traceback 출력

    def get_summary_report(self) -> str:
        """현재까지의 사용량과 예상 비용에 대한 요약 리포트를 문자열로 반환합니다."""
        
        # 비용 계산
        input_cost = (self.total_input_tokens / 1000) * PRICE_INPUT_PER_1K_TOKENS
        output_cost = (self.total_output_tokens / 1000) * PRICE_OUTPUT_PER_1K_TOKENS
        total_cost = input_cost + output_cost

        # 리포트 생성
        report = (
            f"[API 사용량 리포트 (테스트용)]\n"
            f"----------------------------------------\n"
            f"- 입력 토큰: {self.total_input_tokens}\n"
            f"- 출력 토큰: {self.total_output_tokens}\n"
            f"- 총 토큰: {self.total_input_tokens + self.total_output_tokens}\n"
            f"----------------------------------------\n"
            f"- 예상 비용: ${total_cost:.6f}\n"
            f"----------------------------------------"
        )
        return report
