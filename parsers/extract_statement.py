"""
Extract tables from bank statement PDFs by section titles. Config via YAML.
"""

import argparse
import csv
import re
from pathlib import Path

import pdfplumber
import yaml

from .helpers import find_text, extract_table_between


def _safe_name(s: str) -> str:
    return re.sub(r"[^\w\-.]", "", s)


def _write_csv(path: Path, rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(
            ["" if c is None else str(c).strip() for c in row] for row in rows
        )


def load_tables_config(path: Path) -> dict:
    """Load config with optional general section and tables list."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return raw


def process_pdf(
    tables: list[dict],
    pdf_path: Path,
    out_dir: Path,
    opts: dict,
    *,
    verbose: bool = True,
) -> None:
    """Find each section title in order, then extract table between consecutive pairs using explicit columns."""
    snap_tolerance = opts["snap_tolerance"]
    offset = opts["offset"]
    margin = opts["margin"]

    pdf = pdfplumber.open(pdf_path)

    headers = []
    ref_page, ref_bbox = None, None
    for t in tables:
        hit = find_text(pdf, t["title"], ref_page=ref_page, ref_bbox=ref_bbox)
        headers.append(hit)
        if hit:
            ref_page, ref_bbox = hit

    last_page_idx = len(pdf.pages) - 1
    last_page = pdf.pages[last_page_idx]
    doc_end = (last_page_idx, {"top": last_page.height, "bottom": last_page.height})

    for i in range(len(headers)):
        start = headers[i]
        end = headers[i + 1] if i + 1 < len(headers) else doc_end
        if tables[i].get("parse") is False:
            continue
        if start is None:
            continue
        table = extract_table_between(
            pdf, start, end, tables[i],
            snap_tolerance=snap_tolerance, offset=offset, margin=margin,
        )
        if table:
            name = tables[i].get("name") or tables[i]["title"]
            out_name = f"{_safe_name(pdf_path.stem)}_{_safe_name(name)}.csv"
            _write_csv(out_dir / out_name, table)
            if verbose:
                print(f"  {name}: {len(table)} rows → {out_name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="PDF path or glob (e.g. *.pdf or statements/**/*.pdf)")
    parser.add_argument("--config", "-c", type=Path, required=True, help="Path to tables YAML config")
    parser.add_argument("--out-dir", "-o", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    pdf_paths = sorted(args.path.parent.glob(args.path.name))
    cfg = load_tables_config(args.config)
    general = cfg["general"]
    tables = cfg["tables"]

    for pdf_path in pdf_paths:
        print(pdf_path.name)
        process_pdf(tables, pdf_path, args.out_dir, opts=general)


if __name__ == "__main__":
    main()
