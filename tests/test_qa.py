"""Проверки чекеров, парсеров и эталона kk."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from qazaq_loc_qa.catalog import STRINGS, bundle_from_catalog, suggestion_map
from qazaq_loc_qa.dataset import write_dataset
from qazaq_loc_qa.llm import parse_llm_payload
from qazaq_loc_qa.models import CheckConfig
from qazaq_loc_qa.parsers import load_path
from qazaq_loc_qa.pipeline import apply_verified, run_checks
from qazaq_loc_qa.textutil import normalize_uz_apostrophes, placeholder_counts

ROOT = Path(__file__).resolve().parents[1]


def _index(findings):
    grouped: dict[tuple[str, str], set[str]] = {}
    for item in findings:
        grouped.setdefault((item.key, item.language), set()).add(item.checker)
    return grouped


@pytest.fixture(scope="module")
def sample_findings():
    config = CheckConfig(suggestions=suggestion_map())
    return run_checks(bundle_from_catalog(), config)


def test_known_bugs_are_found(sample_findings):
    found = _index(sample_findings)
    expected = {
        ("menu.play", "kk"): "copy_from_ru",
        ("menu.play", "uz"): "uz_cyrillic",
        ("menu.continue", "uz"): "untranslated",
        ("menu.exit", "kk"): "whitespace",
        ("ui.start", "kk"): "placeholder_mismatch",
        ("shop.buy", "kk"): "placeholder_mismatch",
        ("shop.buy", "uz"): "placeholder_mismatch",
        ("profile.welcome", "kk"): "placeholder_mismatch",
        ("chat.message", "kk"): "tag_mismatch",
        ("reward.coins", "kk"): "tag_mismatch",
        ("shop.mojibake", "kk"): "mojibake",
        ("auth.login", "kk"): "script_mix",
        ("ui.houses", "kk"): "kk_vowel_harmony",
        ("social.friends", "kk"): "kk_suffix_consonant",
        ("nav.home", "kk"): "kk_vowel_harmony",
        ("quest.new", "kk"): "glossary",
        ("quest.new", "uz"): "uz_cyrillic",
        ("dialog.ok", "kk"): "length_overflow",
        ("dialog.confirm", "kk"): "punctuation",
        ("shop.gap", "kk"): "whitespace",
        ("inv.title", "kk"): "untranslated",
        ("help.lines", "kk"): "newline_mismatch",
        ("news.empty", "kk"): "missing_translation",
        ("news.empty", "uz"): "missing_translation",
        ("economy.case", "uz"): "glossary",
        ("season.pass", "uz"): "untranslated",
        ("vehicle.fuel", "kk"): "glossary",
        ("world.garage", "kk"): "kk_foreign_letter",
        ("char.skin", "kk"): "kk_foreign_letter",
        ("dialog.no", "uz"): "uz_apostrophe",
        ("auth.password", "uz"): "uz_apostrophe",
        ("job.got", "kk"): "placeholder_mismatch",
        ("house.buy", "kk"): "placeholder_mismatch",
    }
    missing = {
        key: checker
        for key, checker in expected.items()
        if checker not in found.get(key, set())
    }
    assert not missing, missing


def test_clean_rows_stay_clean(sample_findings):
    found = _index(sample_findings)
    clean = [
        ("menu.back", "kk"),
        ("menu.back", "uz"),
        ("time.left", "kk"),
        ("time.left", "uz"),
        ("combat.hp", "kk"),
        ("combat.hp", "uz"),
        ("ui.warn", "kk"),
        ("ui.warn", "uz"),
        ("ui.error", "uz"),
        ("tutor.skip", "uz"),
        ("dialog.save", "uz"),
        ("vehicle.ready", "uz"),
        ("dialog.ok", "uz"),
    ]
    noisy = {key: found[key] for key in clean if key in found}
    assert not noisy, noisy


def test_verified_kazakh_has_no_findings():
    bundle = bundle_from_catalog(fixed_languages=("kk",))
    findings = run_checks(bundle, CheckConfig(suggestions=suggestion_map()))
    kk = [item for item in findings if item.language == "kk"]
    assert kk == []


def test_every_placeholder_survives_in_kazakh_fix():
    for row in STRINGS:
        assert placeholder_counts(row["en"]) == placeholder_counts(row["kk_fixed"]), row["key"]


def test_dataset_roundtrip(tmp_path: Path):
    write_dataset(tmp_path)
    from_json = load_path(tmp_path / "data" / "sample" / "strings.json")
    from_csv = load_path(tmp_path / "data" / "sample" / "strings.csv")
    from_po = load_path(tmp_path / "data" / "sample" / "kk.po")
    json_map = {segment.key: segment.texts["kk"] for segment in from_json.segments}
    csv_map = {segment.key: segment.texts["kk"] for segment in from_csv.segments}
    po_map = {segment.key: segment.texts["kk"] for segment in from_po.segments}
    assert json_map["menu.play"] == "Играть"
    assert csv_map["nav.home"] == "Үйға оралу"
    assert po_map["ui.houses"] == "Үйлар"
    assert "\n" in next(segment.texts["en"] for segment in from_po.segments if segment.key == "help.lines")
    fixed = json.loads((tmp_path / "data" / "corrected" / "kk.json").read_text(encoding="utf-8"))
    assert fixed["ui.houses"] == "Үйлер"
    assert fixed["menu.play"] == "Ойнау"
    xlsx = tmp_path / "data" / "sample" / "strings.xlsx"
    if xlsx.exists():
        from_xlsx = load_path(xlsx)
        assert any(segment.key == "shop.buy" for segment in from_xlsx.segments)


def test_directory_merge_prefers_multilingual_table(tmp_path: Path):
    write_dataset(tmp_path)
    bundle = load_path(tmp_path / "data" / "sample")
    play = next(segment for segment in bundle.segments if segment.key == "menu.play")
    assert play.texts["en"] == "Play"
    assert play.texts["kk"] == "Играть"
    assert play.texts["uz"] == "Играть"


def test_nested_json_and_flat_language_file(tmp_path: Path):
    payload = {"ui": {"play": "Ойнау", "exit": "Шығу"}}
    path = tmp_path / "kk.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    bundle = load_path(path)
    texts = {segment.key: segment.texts["kk"] for segment in bundle.segments}
    assert texts == {"ui.play": "Ойнау", "ui.exit": "Шығу"}


def test_uz_apostrophe_normalizer():
    assert normalize_uz_apostrophes("Yo'q") == "Yo\u02bbq"
    assert normalize_uz_apostrophes("noto'g'ri") == "noto\u02bbg\u02bbri"
    assert normalize_uz_apostrophes("noto\u02bbg\u02bbri") == "noto\u02bbg\u02bbri"


def test_llm_payload_parser_ignores_markdown():
    raw = """```json
    {"issues":[
      {"key":"menu.play","language":"kk","severity":"high","message":"калька","suggestion":"Ойнау"},
      {"key":"","language":"kk","message":"пусто"}
    ]}
    ```"""
    issues = parse_llm_payload(raw)
    assert len(issues) == 1
    assert issues[0]["suggestion"] == "Ойнау"


def test_apply_verified_clears_kazakh(sample_findings):
    assert sample_findings
    fixed = apply_verified(
        bundle_from_catalog(),
        suggestion_map(),
        languages=("kk",),
        normalize_uz=False,
    )
    findings = run_checks(fixed, CheckConfig())
    assert [item for item in findings if item.language == "kk"] == []
