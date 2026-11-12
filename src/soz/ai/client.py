"""OpenAI-совместимый клиент. Без ключа слой остаётся на локальных правилах."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from soz.models import Entry, Finding


class LlmClient:
    def __init__(self) -> None:
        self.api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"

    def available(self) -> bool:
        return bool(self.api_key)

    def review(self, entry: Entry, system: str, user: str) -> list[Finding]:
        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code}") from exc
        content = body["choices"][0]["message"]["content"]
        return findings_from_model(entry, content)


def findings_from_model(entry: Entry, content: str) -> list[Finding]:
    data = _extract_json(content)
    issues = data.get("issues") if isinstance(data, dict) else None
    if not isinstance(issues, list):
        return []
    findings: list[Finding] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        key = str(issue.get("key") or entry.key)
        if key != entry.key:
            continue
        findings.append(
            Finding(
                file=entry.file,
                key=entry.key,
                locale=entry.locale,
                context=entry.context,
                severity=str(issue.get("severity") or "medium"),
                engine="ai",
                code=str(issue.get("code") or "meaning"),
                message=str(issue.get("message") or "").strip(),
                source=entry.source,
                target=entry.target,
                suggestion=str(issue.get("suggestion") or "").strip(),
            )
        )
    return findings


def _extract_json(content: str) -> dict[str, object]:
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        return {}
    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}
