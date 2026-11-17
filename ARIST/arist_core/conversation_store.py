"""Persistencia local del historial de conversación y del contexto para el modelo."""

import json
from datetime import datetime, timezone
from pathlib import Path


class ConversationStore:
    def __init__(self, folder: Path):
        self.folder = folder
        self.folder.mkdir(parents=True, exist_ok=True)
        self.transcript_path = self.folder / "conversaciones.jsonl"
        self.ai_context_path = self.folder / "contexto_ia.json"
        self.memory_path = self.folder / "memoria.json"

    def log(self, role: str, content: str) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "content": content,
        }
        with self.transcript_path.open("a", encoding="utf-8") as transcript:
            transcript.write(json.dumps(record, ensure_ascii=False) + "\n")

    def load_ai_context(self, system_prompt: str) -> list[dict[str, str]]:
        if not self.ai_context_path.is_file():
            return [{"role": "system", "content": system_prompt}]
        try:
            saved = json.loads(self.ai_context_path.read_text(encoding="utf-8"))
            if not isinstance(saved, list):
                raise ValueError("El contexto guardado no es una lista.")
            turns = [
                item for item in saved
                if isinstance(item, dict)
                and item.get("role") in {"user", "assistant"}
                and isinstance(item.get("content"), str)
            ][-20:]
            return [{"role": "system", "content": system_prompt}, *turns]
        except (OSError, ValueError, json.JSONDecodeError):
            return [{"role": "system", "content": system_prompt}]

    def save_ai_context(self, history: list[dict[str, str]]) -> None:
        payload = json.dumps(history, ensure_ascii=False, indent=2)
        temporary = self.ai_context_path.with_suffix(".json.tmp")
        temporary.write_text(payload, encoding="utf-8")
        temporary.replace(self.ai_context_path)

    def load_memory(self, size: int) -> list[int]:
        if not self.memory_path.is_file():
            return [0] * size
        try:
            values = json.loads(self.memory_path.read_text(encoding="utf-8"))
            if isinstance(values, list) and len(values) == size and all(
                isinstance(value, int) and 0 <= value <= 255 for value in values
            ):
                return values
        except (OSError, ValueError, json.JSONDecodeError):
            pass
        return [0] * size

    def save_memory(self, values: list[int]) -> None:
        payload = json.dumps(values, ensure_ascii=False, indent=2)
        temporary = self.memory_path.with_suffix(".json.tmp")
        temporary.write_text(payload, encoding="utf-8")
        temporary.replace(self.memory_path)
