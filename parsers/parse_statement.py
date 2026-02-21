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
    s = raw.strip()
    dt = datetime.strptime(s, '%Y-%m-%d')
    return dt.strftime("%Y-%m-%d")

def _parse_date_sp(raw: str) -> str | None:
    s = raw.strip()
    dt = datetime.strptime(s, '%d-%m-%y')
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
    "date_sp": _parse_date_sp,
    "date yyyy-mm-dd": _parse_date_iso,
}


def load_parse_config(path: Path | str) -> dict:
    """Load parse config YAML. Must have 'columns' and either 'amount_from' or 'debit_credit'."""
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not cfg or "columns" not in cfg:
        raise ValueError("Config must have 'columns' list")
    has_amount_from = bool(cfg.get("amount_from"))
    has_debit_credit = bool(cfg.get("debit_credit"))
    if not has_amount_from and not has_debit_credit:
        raise ValueError("Config must have 'amount_from' or 'debit_credit'")
    if has_amount_from and has_debit_credit:
        raise ValueError("Config cannot have both 'amount_from' and 'debit_credit'")
    return cfg


def _derive_amount_amount_from(
    parsed: dict[str, Any], amount_from: dict[str, str]
) -> tuple[str | None, str | None]:
    """Amount from multi-currency columns (first non-empty positive wins)."""
    for dst, curr in amount_from.items():
        val = parsed.get(dst)
        if val is None or val == "":
            continue
        try:
            n = float(val)
            if n > 0:
                return str(round(n, 2)), curr
        except (ValueError, TypeError):
            continue
    return None, None


def _derive_amount_debit_credit(
    parsed: dict[str, Any], debit_credit: dict, table_key: str | None = None,
) -> tuple[str | None, str | None]:
    """
    Amount from debit/credit columns: one has value, other empty.
    Debit (money out) → positive amount. Credit (money in) → negative amount.
    """
    debit_dst = debit_credit.get("debit") or debit_credit.get("debit_column")
    credit_dst = debit_credit.get("credit") or debit_credit.get("credit_column")
    currency = debit_credit.get("currency")
    currency_by_table = debit_credit.get("currency_by_table") or {}
    if table_key and table_key in currency_by_table:
        currency = currency_by_table[table_key]
    if not currency:
        return None, None

    val = parsed.get(debit_dst) if debit_dst else None
    if val is not None and val != "":
        try:
            n = float(val)
            if n > 0:
                return str(round(n, 2)), currency
        except (ValueError, TypeError):
            pass

    val = parsed.get(credit_dst) if credit_dst else None
    if val is not None and val != "":
        try:
            n = float(val)
            if n > 0:
                return str(round(-n, 2)), currency
        except (ValueError, TypeError):
            pass
    return None, None


def parse_row_with_config(
    raw_row: dict[str, str],
    column_specs: list[dict],
    cfg: dict,
    table_key: str | None = None,
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

    if cfg.get("amount_from"):
        amount_str, currency = _derive_amount_amount_from(parsed, cfg["amount_from"])
    else:
        amount_str, currency = _derive_amount_debit_credit(
            parsed, cfg["debit_credit"], table_key
        )

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


def _table_key_from_stem(stem: str) -> str | None:
    """Extract table key from CSV stem, e.g. 'Estadodecuenta..._Movimientos' -> 'Movimientos'."""
    if "_" in stem:
        return stem.rsplit("_", 1)[-1]
    return None


def parse_extracted_csv(
    input_path: Path,
    config_path: Path,
    table_key: str | None = None,
) -> list[dict]:
    """
    Read an extracted CSV and return parsed rows (date, description, ref, currency, amount).
    table_key: optional table identifier for debit_credit.currency_by_table; defaults to stem suffix.
    """
    cfg = load_parse_config(config_path)
    column_specs = cfg["columns"]
    key = table_key if table_key is not None else _table_key_from_stem(
        Path(input_path).stem
    )

    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out = []
    for raw_row in rows:
        row = parse_row_with_config(raw_row, column_specs, cfg, table_key=key)
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
    *,
    verbose: bool = True,
) -> Path:
    """Parse extracted CSV and write parsed CSV. Returns output path."""
    rows = parse_extracted_csv(input_path, config_path=config_path)
    write_parsed_csv(rows, output_path)
    if verbose:
        print(f"  {input_path.name}: {len(rows)} rows")
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
