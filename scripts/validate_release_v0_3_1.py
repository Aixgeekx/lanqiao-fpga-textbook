#!/usr/bin/env python3
"""Validate v0.3.1 PDF, Obsidian markdown and release zip."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "results" / "蓝桥杯FPGA开发教程_详细注释版.pdf"
ZIP_PATH = ROOT / "results" / "lanqiao-fpga-textbook-v0.3.1.zip"
OBSIDIAN_MD = ROOT / "蓝桥杯FPGA竞赛教程_Obsidian版.md"
EXAM_MD = ROOT / "蓝桥杯FPGA真题复盘_Obsidian索引.md"

REQUIRED_DOCS = [
    ROOT / "CHANGELOG.md",
    ROOT / "RELEASE_NOTES_v0.3.1.md",
    ROOT / "PRINT_QA_v0.3.1.md",
    ROOT / "PUBLISH_RUNBOOK_v0.3.1.md",
    OBSIDIAN_MD,
    EXAM_MD,
]

PDF_KEYWORDS = [
    "I2C",
    "UART",
    "SPI",
    "状态机",
    "按键消抖",
    "亚稳态",
    "数码管",
    "SRAM",
    "DS1302",
    "W25Q128",
]

MD_KEYWORDS = [
    "title: 蓝桥杯 FPGA 竞赛教程",
    "tags:",
    "[[#18 Obsidian 题目复盘模板]]",
    "> [!NOTE]",
    "> [!TIP]",
    "> [!WARNING]",
    "## 20 高频检索关键词",
]

EXAM_MD_KEYWORDS = [
    "第十六届省赛真题",
    "第十六届模拟试题 I",
    "第十六届模拟试题 II",
    "第十六届模拟试题 III",
    "第十六届国赛题",
    "第十七届模拟考试 I",
    "第十七届模拟考试 II",
    "提交前统一检查",
]


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def read_pdf_text(pdf_path: Path) -> tuple[int, str]:
    try:
        from pypdf import PdfReader
    except Exception as exc:  # pragma: no cover - dependency gate
        fail(f"pypdf is required: {exc}")
    if not pdf_path.exists():
        fail(f"PDF not found: {pdf_path}")
    reader = PdfReader(str(pdf_path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return len(reader.pages), text


def validate_pdf(pdf_path: Path) -> None:
    pages, text = read_pdf_text(pdf_path)
    if pages < 120:
        fail(f"PDF page count too small: {pages}")
    if len(text) < 100000:
        fail(f"PDF extracted text too short: {len(text)} chars")
    missing = [kw for kw in PDF_KEYWORDS if kw not in text]
    if missing:
        fail(f"PDF missing keywords: {missing}")
    footer_pattern = re.compile(r"[—-]\s*\d+\s*/\s*\d+\s*[—-]")
    if not footer_pattern.search(text):
        fail("PDF footer does not expose current page / total pages in text layer")
    ok(f"PDF validated: pages={pages}, chars={len(text)}")


def validate_docs() -> None:
    missing = [p for p in REQUIRED_DOCS if not p.exists()]
    if missing:
        fail("Missing release docs: " + ", ".join(str(p) for p in missing))
    text = OBSIDIAN_MD.read_text(encoding="utf-8")
    missing_md = [kw for kw in MD_KEYWORDS if kw not in text]
    if missing_md:
        fail(f"Obsidian markdown missing markers: {missing_md}")
    exam_text = EXAM_MD.read_text(encoding="utf-8")
    missing_exam = [kw for kw in EXAM_MD_KEYWORDS if kw not in exam_text]
    if missing_exam:
        fail(f"Exam Obsidian index missing markers: {missing_exam}")
    ok("Release docs and Obsidian markdown validated")


def validate_zip(zip_path: Path) -> None:
    if not zip_path.exists():
        fail(f"ZIP not found: {zip_path}")
    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
        if bad:
            fail(f"ZIP corruption at member: {bad}")
        names = set(zf.namelist())
    expected = [
        "CHANGELOG.md",
        "RELEASE_NOTES_v0.3.1.md",
        "PRINT_QA_v0.3.1.md",
        "PUBLISH_RUNBOOK_v0.3.1.md",
        "蓝桥杯FPGA竞赛教程_Obsidian版.md",
        "蓝桥杯FPGA真题复盘_Obsidian索引.md",
    ]
    missing = [name for name in expected if not any(item.endswith(name) for item in names)]
    if missing:
        fail(f"ZIP missing expected files: {missing}")
    ok(f"ZIP validated: entries={len(names)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, default=PDF_PATH)
    parser.add_argument("--zip", type=Path, default=ZIP_PATH)
    parser.add_argument("--skip-zip", action="store_true")
    args = parser.parse_args()

    validate_docs()
    validate_pdf(args.pdf)
    if not args.skip_zip:
        validate_zip(args.zip)
    ok("v0.3.1 release validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
