"""
Parse extracted statement CSVs into a normalized CSV using a YAML config.
Config defines: column → dst field + parsing_method (sp_amt | date_iso | str | etc).
"""

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import yaml


# Parsed CSV columns (contract with loaders)
PARSED_HEADER = ["date", "description", "ref", "currency", "amount"]


def _parse_sp_amount(raw: str) -> str | None:
    """Amount (e.g. 'U$S 5,00' or '$ 46.101,00') → decimal string or None."""
    s = raw.strip()
    s = re.sub(r"[^0-9,]", "", s)
    s = s.replace(",", ".")
    if not s:
        return None
    return str(round(float(s), 2))

def _parse_date_iso(raw: str) -> str | None:
    """Parse to YYYY-MM-DD."""
    s = raw.strip()
    dt = datetime.strptime(s, '%Y-%m-%d')
    return dt.strftime("%Y-%m-%d")

def _parse_str(raw: str) -> str:
    """Strip and return; never fail."""
    if not raw:
        return None
    return raw.strip()

# Registry: parsing_method name → function (raw_str) → value (None = skip/empty)
PARSERS: dict[str, Callable[[str], Any]] = {
    "str": _parse_str,
    "sp_amt": _parse_sp_amount,
    "date_iso": _parse_date_iso,
    "date yyyy-mm-dd": _parse_date_iso,
}


def load_parse_config(path: Path | str) -> dict:
    """Load parse config YAML. Must have 'columns' and 'amount_from'."""
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not cfg or "columns" not in cfg:
        raise ValueError("Config must have 'columns' list")
    if "amount_from" not in cfg:
        raise ValueError("Config must have 'amount_from' (dst → currency)")
    return cfg


def parse_row_with_config(
    raw_row: dict[str, str],
    column_specs: list[dict],
    amount_from: dict[str, str],
) -> dict[str, str] | None:
    """
    Apply config to one raw CSV row. Returns parsed row with keys from PARSED_HEADER,
    or None if row should be skipped (no valid date or amount).
    """
    parsed: dict[str, Any] = {}
    for spec in column_specs:
        col = spec.get("column")
        dst = spec.get("dst")
        method_name = spec.get("parsing_method")
        parser = PARSERS.get(method_name, _parse_str)
        raw_val = raw_row.get(col)
        parsed[dst] = parser(raw_val)

    # Derive amount + currency from amount_from (first non-empty positive wins)
    amount_str = None
    currency = None
    for dst, curr in amount_from.items():
        val = parsed.get(dst)
        if val is None or val == "":
            continue
        try:
            n = float(val)
            if n > 0:
                amount_str = str(round(n, 2))
                currency = curr
                break
        except (ValueError, TypeError):
            continue

    if amount_str is None or currency is None:
        return None

    date_str = parsed.get("date")
    if not date_str:
        return None

    return {
        "date": date_str,
        "description": parsed.get("description"),
        "ref": parsed.get("ref"),
        "currency": currency,
        "amount": amount_str,
    }


def parse_extracted_csv(
    input_path: Path,
    config_path: Path,
) -> list[dict]:
    """
    Read an extracted CSV and return parsed rows (date, description, ref, currency, amount).
    """
    cfg = load_parse_config(config_path)
    column_specs = cfg["columns"]
    amount_from = cfg["amount_from"]

    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out = []
    for raw_row in rows:
        row = parse_row_with_config(raw_row, column_specs, amount_from)
        if row is not None:
            out.append(row)
    return out


def write_parsed_csv(rows: list[dict], output_path: Path) -> None:
    """Write parsed rows to CSV with PARSED_HEADER."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=PARSED_HEADER, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def parse_extracted_csv_to_file(
    input_path: Path,
    output_path: Path,
    config_path: Path,
) -> Path:
    """Parse extracted CSV and write parsed CSV. Returns output path."""
    rows = parse_extracted_csv(input_path, config_path=config_path)
    write_parsed_csv(rows, output_path)
    print(f"Parsed {input_path} -> {output_path} ({len(rows)} rows)")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse extracted statement CSV using a config")
    parser.add_argument("input", type=Path, help="Extracted CSV path (or glob)")
    parser.add_argument("-c", "--config", type=Path, required=True, help="Parse config YAML")
    parser.add_argument("-o", "--out", type=Path, required=True, help="Output path")
    args = parser.parse_args()

    csv_paths = sorted(args.input.parent.glob(args.input.name))
    for csv_path in csv_paths:
        output_path = args.out / (csv_path.stem + ".parsed.csv")
        parse_extracted_csv_to_file(csv_path, output_path, args.config)


if __name__ == "__main__":
    main()
