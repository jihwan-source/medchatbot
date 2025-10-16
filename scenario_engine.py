# scenario_engine.py
import yaml
from pathlib import Path
from typing import Dict, List, Optional

class Scenario:
    """단일 문진 시나리오를 관리하는 클래스"""
    def __init__(self, scenario_id: str, data: Dict):
        self.id = scenario_id
        self.name = data.get("name")
        self.initial_question_id = data.get("initial_question_id")
        self.nodes = {node["id"]: node for node in data.get("nodes", [])}

    def get_node(self, node_id: str) -> Optional[Dict]:
        """ID로 특정 질문 노드를 반환"""
        return self.nodes.get(node_id)

    def get_initial_node(self) -> Optional[Dict]:
        """시작 질문 노드를 반환"""
        return self.get_node(self.initial_question_id)

class ScenarioManager:
    """모든 문진 시나리오를 로드하고 관리하는 클래스"""
    def __init__(self, scenarios_path: str = "scenarios"):
        self.scenarios: Dict[str, Scenario] = {}
        self.load_all_scenarios(scenarios_path)

    def load_all_scenarios(self, scenarios_path: str):
        """지정된 경로에서 모든 YAML 시나리오 파일을 로드"""
        path = Path(scenarios_path)
        for yaml_file in path.glob("*.yaml"):
            scenario_id = yaml_file.stem
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data:
                    self.scenarios[scenario_id] = Scenario(scenario_id, data)
        print(f"Loaded {len(self.scenarios)} scenarios: {list(self.scenarios.keys())}")

    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """ID로 특정 시나리오 객체를 반환"""
        return self.scenarios.get(scenario_id)

# 매니저 인스턴스 생성 (서버 시작 시 한 번만 실행)
scenario_manager = ScenarioManager()
