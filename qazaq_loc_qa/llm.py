"""Необязательный разбор смысловых ошибок через OpenAI-совместимый API.

Без ключа модуль ничего не выдумывает: отчёт остаётся на детерминированных
чекерах. Секреты читаются только из окружения и не попадают в вывод.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from qazaq_loc_qa.models import Finding, Segment

SYSTEM_PROMPT = """Ты редактор локализации мобильной RP-игры Grand Mobile (открытый мир, работа, фракции, машины, магазин).
Игроки — носители казахского (кириллица) и узбекского (латиница, oʻ и gʻ).
Системные фразы на казахском — на «сіз», коротко, как кнопки и тосты.
Не калькируй русский и английский, если в глоссарии есть свой термин.
Плейсхолдеры (%s, %d, {name}, {amount}) и теги (<b>, <color=#...>) нельзя терять, переименовывать и переводить.
Ответь ТОЛЬКО JSON-объектом:
{"issues":[{"key":"...","language":"kk","severity":"high","message":"...","suggestion":"..."}]}
Если строка уже хорошая, не добавляй её в issues. Не больше 8 замечаний."""


@dataclass
class LLMConfig:
    api_key: str
    base_url: str
    model: str

    @classmethod
    def from_env(cls) -> "LLMConfig | None":
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("QAZAQ_LLM_API_KEY")
        if not api_key:
            return None
        base = os.environ.get("OPENAI_BASE_URL") or os.environ.get("QAZAQ_LLM_BASE_URL")
        base = (base or "https://api.openai.com/v1").rstrip("/")
        model = os.environ.get("OPENAI_MODEL") or os.environ.get("QAZAQ_LLM_MODEL") or "gpt-4o-mini"
        return cls(api_key=api_key, base_url=base, model=model)


def build_user_prompt(segments: list[Segment], glossary_lines: list[str]) -> str:
    rows = []
    for segment in segments[:20]:
        rows.append(
            {
                "key": segment.key,
                "context": segment.context,
                "en": segment.texts.get("en", ""),
                "ru": segment.texts.get("ru", ""),
                "kk": segment.texts.get("kk", ""),
                "uz": segment.texts.get("uz", ""),
            }
        )
    return (
        "Глоссарий (придерживайся его):\n"
        + "\n".join(glossary_lines[:40])
        + "\n\nСтроки:\n"
        + json.dumps(rows, ensure_ascii=False)
    )


def parse_llm_payload(payload: str) -> list[dict]:
    text = payload.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return []
    data = json.loads(text[start : end + 1])
    issues = data.get("issues", [])
    if not isinstance(issues, list):
        return []
    cleaned = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        language = str(issue.get("language") or "kk")
        if language not in {"kk", "uz"}:
            continue
        severity = str(issue.get("severity") or "medium")
        if severity not in {"critical", "high", "medium", "low"}:
            severity = "medium"
        cleaned.append(
            {
                "key": str(issue.get("key") or ""),
                "language": language,
                "severity": severity,
                "message": str(issue.get("message") or "").strip(),
                "suggestion": str(issue.get("suggestion") or "").strip(),
            }
        )
    return [item for item in cleaned if item["key"] and item["message"]]


def findings_from_issues(issues: list[dict], segments: dict[str, Segment]) -> list[Finding]:
    findings: list[Finding] = []
    for issue in issues:
        segment = segments.get(issue["key"])
        if segment is None:
            continue
        language = issue["language"]
        findings.append(
            Finding(
                checker="llm_review",
                severity=issue["severity"],
                language=language,
                key=issue["key"],
                message="Модель: " + issue["message"],
                source_text=segment.texts.get("en", ""),
                target_text=segment.texts.get(language, ""),
                suggestion=issue["suggestion"],
                context=segment.context,
            )
        )
    return findings


def request_review(config: LLMConfig, user_prompt: str, timeout: int = 45) -> str:
    body = json.dumps(
        {
            "model": config.model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        config.base_url + "/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"LLM ответил {exc.code}: {detail}") from exc
    data = json.loads(raw)
    return data["choices"][0]["message"]["content"]


def glossary_lines() -> list[str]:
    from qazaq_loc_qa.glossary_data import TERMS

    lines = []
    for term in TERMS:
        lines.append(
            f"{term['id']}: kk={', '.join(term['kk'])}; uz={', '.join(term['uz'])}; "
            f"нельзя kk={', '.join(term['kk_bad'])}"
        )
    return lines
