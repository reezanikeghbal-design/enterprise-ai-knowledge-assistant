from __future__ import annotations

import json
import threading
import uuid
from pathlib import Path


class ConversationService:
    def __init__(self, filename: str):
        self.path = Path(filename)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _load(self):
        with self.lock:
            return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data):
        with self.lock:
            self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def create(self) -> dict:
        data = self._load()
        cid = str(uuid.uuid4())
        data[cid] = {"id": cid, "messages": []}
        self._save(data)
        return data[cid]

    def list(self) -> list[dict]:
        return [{"id": c["id"], "messages": len(c["messages"])} for c in self._load().values()]

    def get(self, cid: str) -> dict | None:
        return self._load().get(cid)

    def add_message(self, cid: str, role: str, content: str):
        data = self._load()
        if cid not in data:
            data[cid] = {"id": cid, "messages": []}
        data[cid]["messages"].append({"role": role, "content": content})
        self._save(data)
