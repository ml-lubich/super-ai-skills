"""Voice learner, stylistic RAG, and self-improving prompt optimizer."""

import os
import json
import re
from typing import List, Dict, Any, Optional
from rich.console import Console

console = Console()

AI_FLUFF_PATTERNS = [
    r"\bdelve\b", r"\bleverage\b", r"\btapestry\b", r"\btestament\b",
    r"\bcertainly\b", r"\bi'd be happy to\b", r"\bplease don't hesitate\b",
    r"\bexceptional\b", r"\boutstanding\b", r"\bcutting-edge\b", r"—", r"–"
]

class VoiceLearner:
    """Extracts, scores, and refines authentic human voice patterns for outreach and replies."""

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or os.path.expanduser("~/.config/superai-skills/voice_memory.json")
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        self.memory = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"samples": [], "vocabulary": {}, "average_sentence_length": 12, "few_shots": []}

    def save(self) -> None:
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2)

    def learn_sample(self, text: str, context: str = "general") -> Dict[str, Any]:
        """Ingest a real human message to learn stylistic characteristics."""
        cleaned = text.strip()
        if not cleaned:
            return {"status": "empty"}

        words = re.findall(r"\b\w+\b", cleaned.lower())
        sentences = [s.strip() for s in re.split(r"[.!?]+", cleaned) if s.strip()]
        avg_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)

        entry = {
            "text": cleaned,
            "context": context,
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_len": round(avg_len, 1)
        }
        self.memory["samples"].append(entry)
        if len(self.memory["samples"]) > 50:
            self.memory["samples"] = self.memory["samples"][-50:]

        self.memory["average_sentence_length"] = round(
            sum(s["avg_sentence_len"] for s in self.memory["samples"]) / len(self.memory["samples"]), 1
        )
        self.save()
        return entry

    def audit_draft(self, draft: str) -> Dict[str, Any]:
        """Audit a proposed draft against AI buzzwords and human voice heuristics."""
        flagged = []
        for pat in AI_FLUFF_PATTERNS:
            if re.search(pat, draft, re.IGNORECASE):
                flagged.append(pat.replace(r"\b", ""))

        char_len = len(draft)
        score = 100 - (len(flagged) * 20)
        if char_len > 400:
            score -= 15  # Penalty for excessive verbosity

        return {
            "score": max(score, 0),
            "clean": len(flagged) == 0,
            "flagged_ai_fluff": flagged,
            "char_count": char_len,
            "recommendation": "Passes humanizer check" if len(flagged) == 0 else f"Remove buzzwords: {', '.join(flagged)}"
        }

    def get_grounding_few_shots(self, limit: int = 3) -> List[str]:
        """Return the best natural human few-shots stored in memory for in-context RAG."""
        return [s["text"] for s in self.memory["samples"][-limit:]]
