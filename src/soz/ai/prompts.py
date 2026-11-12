"""Сборка промпта из system.md, игрового контекста и few-shot."""

from __future__ import annotations

import json
from pathlib import Path

from soz.models import Entry
from soz.tokens import shield


def load_prompt_assets(root: Path) -> dict[str, object]:
    few_shot = json.loads((root / "prompts" / "few_shot.json").read_text(encoding="utf-8"))
    system = (root / "prompts" / "system.md").read_text(encoding="utf-8").strip()
    game = (root / "prompts" / "game_context.md").read_text(encoding="utf-8").strip()
    return {
        "version": str(few_shot.get("version") or "soz-ai"),
        "system": system,
        "game": game,
        "few_shot": few_shot,
    }


def system_prompt(assets: dict[str, object]) -> str:
    few_shot = assets["few_shot"]
    assert isinstance(few_shot, dict)
    return (
        f"{assets['system']}\n\n"
        f"{assets['game']}\n\n"
        f"Версия промпта: {assets['version']}.\n\n"
        f"{render_few_shot(few_shot)}"
    )


def user_prompt(
    entry: Entry,
    glossary_slice: list[dict[str, object]],
    technical_codes: list[str],
) -> str:
    shielded, tokens = shield(entry.target)
    legend = [{"token": f"⟦{index}⟧", "keep": value} for index, value in enumerate(tokens)]
    payload = {
        "key": entry.key,
        "locale": entry.locale,
        "context": entry.context,
        "source": entry.source,
        "target_shielded": shielded,
        "immutable_tokens": legend,
        "glossary": glossary_slice,
        "already_found_by_technical_layer": technical_codes,
        "reply_schema": {
            "issues": [
                {
                    "key": entry.key,
                    "code": "calque_ru | calque_en | glossary_term | register | meaning",
                    "severity": "high | medium",
                    "message": "коротко, по-русски",
                    "suggestion": "целая строка перевода или пусто, если issue нет",
                }
            ]
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_few_shot(few_shot: dict[str, object]) -> str:
    lines = ["Эталонные примеры. Повторяй решение, а не уверенный тон.", ""]
    lines.append("Молчать, issues = []:")
    for example in few_shot.get("silent", []):
        assert isinstance(example, dict)
        lines.append(
            f"- [{example.get('locale')}/{example.get('context')}] "
            f"«{example.get('target')}» — {example.get('why')}"
        )
    lines.append("")
    lines.append("Менять строку целиком:")
    for example in few_shot.get("fix", []):
        assert isinstance(example, dict)
        lines.append(
            f"- [{example.get('locale')}/{example.get('context')}] "
            f"«{example.get('target')}» → «{example.get('suggestion')}» "
            f"({example.get('code')}). {example.get('why')}"
        )
    lines.append("")
    lines.append("Запреты:")
    for example in few_shot.get("hold", []):
        assert isinstance(example, dict)
        lines.append(f"- {example.get('id')}: {example.get('why')}")
    return "\n".join(lines)


def normalize_text(text: str) -> str:
    collapsed = " ".join((text or "").strip().casefold().split())
    return collapsed.replace("?", "").replace("!", "").replace(".", "").strip()
