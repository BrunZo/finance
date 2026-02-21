"""
Run extract_statement then parse_statement for each subdirectory of the statements dir.
For each subdir xxx: extract with xxx_extract.yaml → pre/xxx/, parse with xxx_parse.yaml → post/xxx/.
"""

import argparse
import sys
from pathlib import Path

from .extract_statement import load_tables_config, process_pdf
from .parse_statement import parse_extracted_csv_to_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract and parse statements for all subdirs"
    )
    parser.add_argument(
        "dir",
        type=Path,
        nargs="?",
        default=Path("parsers/statements"),
        help="Root dir with subdirs (default: parsers/statements)",
    )
    parser.add_argument(
        "--configs-dir",
        type=Path,
        default=Path("parsers/configs"),
        help="Directory for *_extract.yaml and *_parse.yaml configs",
    )
    parser.add_argument(
        "--pre-dir",
        type=Path,
        default=Path("parsers/out/pre"),
        help="Output dir for extracted CSVs",
    )
    parser.add_argument(
        "--post-dir",
        type=Path,
        default=Path("parsers/out/post"),
        help="Output dir for parsed CSVs",
    )
    args = parser.parse_args()

    root = args.dir.resolve()
    configs_dir = args.configs_dir.resolve()
    pre_dir = args.pre_dir.resolve()
    post_dir = args.post_dir.resolve()

    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    subdirs = sorted(d for d in root.iterdir() if d.is_dir())
    if not subdirs:
        print(f"No subdirectories in {root}")
        return

    for subdir in subdirs:
        xxx = subdir.name
        extract_config = configs_dir / f"{xxx}_extract.yaml"
        parse_config = configs_dir / f"{xxx}_parse.yaml"
        out_pre = pre_dir / xxx
        out_post = post_dir / xxx

        if not extract_config.exists():
            print(f"{xxx}: skip, no extract config")
            continue

        pdfs = list(subdir.glob("*.pdf"))
        if not pdfs:
            print(f"{xxx}: skip, no PDFs")
            continue

        print(f"\n{xxx}")

        # Extract
        cfg = load_tables_config(extract_config)
        general = cfg["general"]
        tables = cfg["tables"]
        for pdf_path in sorted(pdfs):
            try:
                print(f"  {pdf_path.name}")
                process_pdf(tables, pdf_path, out_pre, opts=general)
            except Exception as e:
                print(f"  extract failed for {pdf_path.name}: {e}", file=sys.stderr)
                continue

        # Parse
        csvs = sorted(out_pre.glob("*.csv"))
        if not csvs:
            print(f"  skip parse: no CSVs")
            continue
        if not parse_config.exists():
            print(f"  skip parse: no parse config")
            continue

        for csv_path in csvs:
            try:
                output_path = out_post / (csv_path.stem + ".parsed.csv")
                parse_extracted_csv_to_file(
                    csv_path, output_path, parse_config
                )
            except Exception as e:
                print(f"  parse failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
