"""Калибровка парсера, үндестік и смыслового слоя."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from soz.ai.client import findings_from_model
from soz.ai.guardrails import breaks_agreement, filter_findings, suggestion_ok
from soz.ai.prompts import load_prompt_assets, system_prompt, user_prompt
from soz.ai.reviewer import semantic_review
from soz.eval import evaluate
from soz.glossary import load_glossary, slice_for_prompt
from soz.harmony import fix_kk_word, fix_uz_word
from soz.models import Entry, Finding
from soz.parse import load_path
from soz.paths import repo_root
from soz.pipeline import run
from soz.tokens import shield, unshield

ROOT = repo_root()
BOOKS = load_glossary(ROOT / "glossary")
ASSETS = load_prompt_assets(ROOT)
FEW = ASSETS["few_shot"]


def _entry(example: dict) -> Entry:
    return Entry(
        key=str(example.get("key") or "sample"),
        source=str(example.get("source") or ""),
        target=str(example["target"]),
        locale=str(example["locale"]),
        context=str(example.get("context") or "system"),
        file="few-shot",
    )


def test_harmony_repairs_known_kazakh_forms() -> None:
    assert fix_kk_word("Үйда")[0] == "Үйде"
    assert fix_kk_word("Кітаплер")[0] == "Кітаптар"
    assert fix_kk_word("Әнлер")[0] == "Әндер"
    assert fix_kk_word("Мектепде")[0] == "Мектепте"
    assert fix_kk_word("бонуслар")[0] == "бонустар"


def test_harmony_leaves_correct_and_short_words() -> None:
    for word in ("Үйде", "Кітаптар", "Әндер", "Мектепте", "бонустар", "ата", "Ойнау", "Артқа"):
        assert fix_kk_word(word) is None, word


def test_uzbek_morphology() -> None:
    assert fix_uz_word("kitobler")[0] == "kitoblar"
    assert fix_uz_word("uyde")[0] == "uyda"
    assert fix_uz_word("yurakga")[0] == "yurakka"
    assert fix_uz_word("Dokon")[0] == "Do\u02bbkon"
    assert fix_uz_word("O'ynash")[0] == "O\u02bbynash"
    assert fix_uz_word("uyda") is None
    assert fix_uz_word("kitoblar") is None


def test_agreement_blocks_pronoun_only_fix() -> None:
    assert breaks_agreement("Сіз сыйлық алдың", "kk")
    assert not breaks_agreement("Сіз сыйлық алдыңыз", "kk")
    assert not breaks_agreement("Сен сыйлық алдың", "kk")
    assert not breaks_agreement("Растайсыз ба?", "kk")
    assert breaks_agreement("Siz sovgʻa olding", "uz")
    assert not breaks_agreement("Siz sovgʻa oldingiz", "uz")
    assert not breaks_agreement("Chiqasizmi?", "uz")


def test_few_shot_silent_examples_have_no_findings() -> None:
    assert isinstance(FEW, dict)
    for example in FEW["silent"]:
        result = run([_entry(example)], BOOKS, ai_mode="local")
        assert result.findings == [], example["target"]


def test_few_shot_fixes_are_what_the_prompt_says() -> None:
    assert isinstance(FEW, dict)
    for example in FEW["fix"]:
        result = run([_entry(example)], BOOKS, ai_mode="local")
        suggestions = [item.suggestion for item in result.findings if item.engine == "ai"]
        assert example["suggestion"] in suggestions, example["target"]
        assert any(item.code == example["code"] for item in result.findings)


def test_hold_rules_reject_bad_suggestions() -> None:
    assert isinstance(FEW, dict)
    glossary = BOOKS["kk"]
    for example in FEW["hold"]:
        if "bad_suggestion" not in example:
            continue
        entry = _entry(example)
        assert suggestion_ok(str(example["bad_suggestion"]), entry, glossary) is False


def test_prompt_contains_game_and_calibration() -> None:
    text = system_prompt(ASSETS)
    assert "Алтын Жол" in text
    assert "Растайсыз ба?" in text
    assert "Chiqasizmi?" in text
    assert "Батырманы басыңыз" in text
    assert ASSETS["version"] == "soz-ai-2"
    assert "issues" in text


def test_glossary_slice_is_not_the_whole_book() -> None:
    entry = Entry(
        key="btn_settings",
        source="Settings",
        target="Настройкалар",
        locale="kk",
        context="ui_button",
        file="mem",
    )
    payload = user_prompt(entry, slice_for_prompt(entry, BOOKS["kk"]), ["vowel_harmony"])
    assert "Баптаулар" in payload
    assert "Асыл тас" not in payload
    assert "vowel_harmony" in payload


def test_placeholders_roundtrip_and_block_a_rewrite() -> None:
    original = "Қуат: %d, {name}"
    shielded, tokens = shield(original)
    assert "%d" not in shielded and "{name}" not in shielded
    assert unshield(shielded, tokens) == original
    entry = Entry("energy", "Energy: %d", original, "kk", "system", "mem")
    assert suggestion_ok("Қуат: %s, {name}", entry, BOOKS["kk"]) is False
    assert suggestion_ok("Энергия: %d, {name}", entry, BOOKS["kk"]) is False
    assert suggestion_ok("Күш: %d, {name}", entry, BOOKS["kk"]) is True


def test_model_cannot_rewrite_a_clean_toast() -> None:
    entry = _entry(
        {
            "locale": "kk",
            "context": "toast",
            "key": "gift_toast",
            "source": "You received a gift",
            "target": "Сен сыйлық алдың",
        }
    )
    bad = Finding(
        file=entry.file,
        key=entry.key,
        locale="kk",
        context="toast",
        severity="high",
        engine="ai",
        code="register",
        message="Повысить регистр",
        source=entry.source,
        target=entry.target,
        suggestion="Сіз сыйлық алдың",
    )
    kept, dropped = filter_findings([bad], entry, BOOKS["kk"], known_clean=True)
    assert kept == []
    assert dropped == 1


def test_api_is_asked_only_for_unsolved_calques() -> None:
    class FakeClient:
        model = "fake"

        def __init__(self) -> None:
            self.calls: list[str] = []

        def available(self) -> bool:
            return True

        def review(self, entry: Entry, system: str, user: str) -> list[Finding]:
            self.calls.append(entry.key)
            assert "Алтын Жол" in system
            if entry.key != "journey":
                return []
            return [
                Finding(
                    file=entry.file,
                    key=entry.key,
                    locale=entry.locale,
                    context=entry.context,
                    severity="high",
                    engine="ai",
                    code="calque_ru",
                    message="Калька с русского.",
                    source=entry.source,
                    target=entry.target,
                    suggestion="Сапарың басталады",
                )
            ]

    client = FakeClient()
    entries = [
        Entry("journey", "Your journey begins", "Ваш путь начинается", "kk", "system", "mem"),
        Entry("btn_play", "Play", "Ойнау", "kk", "ui_button", "mem"),
        Entry("at_home", "At home", "Үйда", "kk", "system", "mem"),
        _entry(
            {
                "locale": "kk",
                "context": "toast",
                "key": "gift_toast",
                "source": "You received a gift",
                "target": "Сен сыйлық алдың",
            }
        ),
    ]
    result = run(entries, BOOKS, ai_mode="api", client=client)
    assert client.calls == ["journey"]
    assert any(item.key == "journey" and item.suggestion == "Сапарың басталады" for item in result.findings)
    assert any(item.key == "at_home" and item.code == "vowel_harmony" for item in result.findings)
    assert not any(item.key == "gift_toast" for item in result.findings)
    assert result.ai.llm_called == 1


def test_model_json_ignores_foreign_keys_and_fences() -> None:
    entry = Entry("sure", "Are you sure?", "Сенімдісіз бе?", "kk", "confirm", "mem")
    raw = """```json
    {"issues": [
      {"key": "other", "code": "meaning", "suggestion": "Жоқ"},
      {"key": "sure", "code": "calque_ru", "severity": "high", "message": "Калька", "suggestion": "Растайсыз ба?"}
    ]}
    ```"""
    found = findings_from_model(entry, raw)
    assert len(found) == 1
    assert found[0].suggestion == "Растайсыз ба?"


def test_parsers_read_each_format(tmp_path: Path) -> None:
    kk = load_path(ROOT / "samples" / "broken_kk.json")
    assert any(item.key == "sure" and item.locale == "kk" for item in kk)
    uz = load_path(ROOT / "samples" / "broken_uz.csv")
    assert any(item.key == "exit_q" and item.target.startswith("Siz ") for item in uz)
    po = load_path(ROOT / "samples" / "broken_ui.po")
    assert [item.key for item in po] == ["btn_back", "books", "btn_play"]
    assert po[0].locale == "kk"
    shop = load_path(ROOT / "samples" / "shop_uz.xlsx")
    assert [item.key for item in shop] == ["btn_shop", "item_heart", "item_books", "item_home"]
    flat = tmp_path / "flat_kk.json"
    flat.write_text(json.dumps({"btn_ok": "Жарайды"}), encoding="utf-8")
    loaded = load_path(flat, "kk")
    assert loaded[0].key == "btn_ok"
    assert loaded[0].target == "Жарайды"


def test_register_fix_keeps_the_toast_verb() -> None:
    entry = Entry(
        key="gift_toast_bad",
        source="You received a gift",
        target="Сіз сыйлық алдың",
        locale="kk",
        context="toast",
        file="mem",
    )
    reviewed = semantic_review(entry, BOOKS["kk"], FEW)
    assert [item.suggestion for item in reviewed] == ["Сен сыйлық алдың"]


def test_formal_ui_repairs_the_verb_instead() -> None:
    entry = Entry(
        key="ui_gift",
        source="You received a gift",
        target="Сіз сыйлық алдың",
        locale="kk",
        context="system",
        file="mem",
    )
    reviewed = semantic_review(entry, BOOKS["kk"], FEW)
    assert [item.suggestion for item in reviewed] == ["Сіз сыйлық алдыңыз"]


def test_gold_calibration() -> None:
    failures = evaluate(ROOT)
    assert failures == []
