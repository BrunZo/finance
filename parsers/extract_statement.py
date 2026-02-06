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


def load_tables_config(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def process_pdf(
    tables: list[dict],
    pdf_path: Path,
    out_dir: Path,
    *,
    snap_tolerance: float = 10,
    offset: float = -10,
) -> None:
    """Find each section title in order, then extract table between consecutive pairs using explicit columns."""
    pdf = pdfplumber.open(pdf_path)
    
    headers = []
    ref_page, ref_bbox = None, None
    for t in tables:
        hit = find_text(pdf, t["title"], ref_page=ref_page, ref_bbox=ref_bbox)
        headers.append(hit)
        if hit:
            ref_page, ref_bbox = hit

    for i in range(len(headers) - 1):
        start, end = headers[i], headers[i + 1]
        if tables[i].get("parse") is False:
            continue
        table = extract_table_between(
            pdf, start, end, tables[i],
            snap_tolerance=snap_tolerance, offset=offset,
        )
        if table:
            title = tables[i]["title"]
            print(f"  — {title}: {len(table)} rows")
            out_name = f"{_safe_name(pdf_path.stem)}_{_safe_name(title)}.csv"
            _write_csv(out_dir / out_name, table)
            print(f"    -> {out_dir / out_name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="PDF path or glob (e.g. *.pdf or statements/**/*.pdf)")
    parser.add_argument("--config", "-c", type=Path, required=True, help="Path to tables YAML config")
    parser.add_argument("--out-dir", "-o", type=Path, required=True, help="Output directory")
    parser.add_argument("--snap-tolerance", type=float, default=10)
    parser.add_argument("--offset", type=float, default=-10)
    args = parser.parse_args()

    pdf_paths = sorted(args.path.parent.glob(args.path.name))
    tables = load_tables_config(args.config)
    
    for pdf_path in pdf_paths:
        print(pdf_path)
        process_pdf(
            tables, pdf_path, args.out_dir,
            snap_tolerance=args.snap_tolerance, offset=args.offset,
        )


if __name__ == "__main__":
    main()
