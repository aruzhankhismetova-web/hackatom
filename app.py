"""Веб-интерфейс TilTekser: файл на вход, отчёт и выверенный казахский на выход."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import streamlit as st

from qazaq_loc_qa.catalog import bundle_from_catalog, suggestion_map
from qazaq_loc_qa.models import CheckConfig
from qazaq_loc_qa.parsers import load_path
from qazaq_loc_qa.pipeline import apply_verified, run_checks
from qazaq_loc_qa.report import render_html, summarize

st.set_page_config(page_title="TilTekser", page_icon="✦", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.4rem; max-width: 1180px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("TilTekser")
st.caption("Поиск ошибок в казахской и узбекской локализации и выверенный казахский текст.")

with st.sidebar:
    st.header("Файл")
    uploaded = st.file_uploader("JSON, CSV, XLSX или PO", type=["json", "csv", "xlsx", "xlsm", "po"])
    use_sample = st.button("Открыть учебный корпус", type="primary")
    source = st.selectbox("Язык источника", ["en", "ru"], index=0)
    targets = st.multiselect("Проверять", ["kk", "uz"], default=["kk", "uz"])
    apply_kk = st.checkbox("Подставить выверенный казахский", value=False)
    normalize_uz = st.checkbox("Починить апостроф oʻ/gʻ в узбекском", value=False)
    st.caption("Эталон kk лежит в data/corrected/kk.json и в учебном корпусе.")

if "bundle" not in st.session_state or use_sample:
    st.session_state["bundle"] = bundle_from_catalog()
    st.session_state["origin"] = "Учебный корпус Grand Mobile"

if uploaded is not None:
    suffix = Path(uploaded.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(uploaded.getvalue())
        temp_path = handle.name
    try:
        st.session_state["bundle"] = load_path(temp_path)
        st.session_state["origin"] = uploaded.name
    except Exception as exc:  # показываем ошибку формата, не падаем всем приложением
        st.error(f"Не удалось прочитать файл: {exc}")

bundle = st.session_state["bundle"]
if apply_kk or normalize_uz:
    bundle = apply_verified(
        bundle,
        suggestion_map(),
        languages=("kk",) if apply_kk else (),
        normalize_uz=normalize_uz,
    )

config = CheckConfig(
    source_language=source,
    targets=tuple(targets) or ("kk", "uz"),
    suggestions=suggestion_map(),
)
findings = run_checks(bundle, config)
summary = summarize(findings)

kk_count = sum(1 for item in findings if item.language == "kk")
uz_count = sum(1 for item in findings if item.language == "uz")
st.write(
    f"Источник: **{st.session_state['origin']}** · строк: **{len(bundle.segments)}** "
    f"· kk: **{kk_count}** · uz: **{uz_count}**"
)
columns = st.columns(5)
columns[0].metric("Оценка", f"{summary['score']}/100")
columns[1].metric("Всего", summary["total"])
columns[2].metric("Critical", summary["by_severity"]["critical"])
columns[3].metric("High", summary["by_severity"]["high"])
columns[4].metric("Medium", summary["by_severity"]["medium"])

if apply_kk and kk_count == 0:
    st.success("Выверенный казахский подставлен. Находок по kk не осталось.")

if findings:
    st.dataframe(
        [
            {
                "уровень": item.severity,
                "язык": item.language,
                "ключ": item.key,
                "проверка": item.checker,
                "что не так": item.message,
                "сейчас": item.target_text,
                "эталон": item.suggestion,
            }
            for item in findings
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.success("Серьёзных и прочих находок нет.")

report = render_html(findings, title="TilTekser — отчёт", summary=summary)
fixed_rows = []
for segment in apply_verified(bundle, suggestion_map(), languages=("kk",)).segments:
    fixed_rows.append({"key": segment.key, "context": segment.context, **segment.texts})

download_cols = st.columns(3)
download_cols[0].download_button(
    "Скачать HTML-отчёт",
    data=report.encode("utf-8"),
    file_name="tiltekser-report.html",
    mime="text/html",
)
download_cols[1].download_button(
    "Скачать находки JSON",
    data=json.dumps(
        [
            {
                "severity": item.severity,
                "language": item.language,
                "key": item.key,
                "checker": item.checker,
                "message": item.message,
                "suggestion": item.suggestion,
            }
            for item in findings
        ],
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8"),
    file_name="findings.json",
    mime="application/json",
)
download_cols[2].download_button(
    "Скачать бандл с выверенным kk",
    data=json.dumps(fixed_rows, ensure_ascii=False, indent=2).encode("utf-8"),
    file_name="kk-verified.json",
    mime="application/json",
)

with st.expander("Как читать отчёт"):
    st.markdown(
        """
        **Critical** — строка сломает клиент или будет пустой: плейсхолдер, тег, кодировка, нет перевода.

        **High** — игрок увидит чужой язык, запрещённый термин или ошибку сингармонизма.

        **Эталон** — казахский текст из выверенного файла. Его можно отдать в сборку после подписи носителя.
        """
    )
