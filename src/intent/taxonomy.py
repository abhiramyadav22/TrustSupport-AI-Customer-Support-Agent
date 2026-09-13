"""Intent taxonomy definition, schema validation, and operational mapping."""

from typing import Dict, List, Any, Optional
import yaml
from dataclasses import dataclass


@dataclass
class IntentDefinition:
    name: str
    display_name: str
    description: str
    expected_action: str
    escalation_risk: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    positive_examples: List[str]
    confusing_neighbors: List[str]
    negative_examples: List[str]
    is_mandatory_escalation: bool = False


class IntentTaxonomy:
    """Manages brand intent taxonomy definitions and provides semantic lookup."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.intents: Dict[str, IntentDefinition] = {}
        self._load_taxonomy()

    def _load_taxonomy(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for item in data.get("intents", []):
            defn = IntentDefinition(
                name=item["name"],
                display_name=item.get("display_name", item["name"]),
                description=item["description"],
                expected_action=item.get("expected_action", ""),
                escalation_risk=item.get("escalation_risk", "MEDIUM"),
                positive_examples=item.get("positive_examples", []),
                confusing_neighbors=item.get("confusing_neighbors", []),
                negative_examples=item.get("negative_examples", []),
                is_mandatory_escalation=item.get("is_mandatory_escalation", False),
            )
            self.intents[defn.name] = defn

    def get_intent_names(self) -> List[str]:
        return list(self.intents.keys())

    def get_definition(self, intent_name: str) -> Optional[IntentDefinition]:
        return self.intents.get(intent_name)

    def is_mandatory_escalate(self, intent_name: str) -> bool:
        defn = self.get_definition(intent_name)
        return defn.is_mandatory_escalation if defn else False
