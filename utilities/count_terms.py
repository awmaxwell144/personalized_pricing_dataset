#!/usr/bin/env python3
"""Count term-list regex matches in a company's saved source text files.

What it does:
  - Reads one regex per line from utilities/term_list.txt by default.
  - Finds a company directory such as dataset/aviation/delta.
  - Writes one CSV for counts in each source's raw.txt file.
  - Writes a second CSV for counts in each source's extracted_company_statement.txt file.
  - Each CSV has one row per scanned source and one column per regex.

Basic usage:
  python3 utilities/count_terms.py delta

Optional examples:
  python3 utilities/count_terms.py dataset/aviation/delta
  python3 utilities/count_terms.py delta --raw-output dataset/aviation/delta/custom_raw_counts.csv
  python3 utilities/count_terms.py delta --statement-output dataset/aviation/delta/custom_statement_counts.csv
  python3 utilities/count_terms.py delta --terms utilities/term_list.txt --case-sensitive
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


DEFAULT_TERMS = Path("utilities/term_list.txt")
DEFAULT_DATASET = Path("dataset")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Count occurrences of each regex in utilities/term_list.txt across a "
            "company's raw.txt files and extracted_company_statement.txt files."
        )
    )
    parser.add_argument(
        "company",
        help=(
            "Company folder name, such as 'delta'. You can also pass a direct "
            "path to a company directory."
        ),
    )
    parser.add_argument(
        "--terms",
        type=Path,
        default=DEFAULT_TERMS,
        help=f"Path to the regex term list. Default: {DEFAULT_TERMS}",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help=f"Path to the dataset directory. Default: {DEFAULT_DATASET}",
    )
    parser.add_argument(
        "--raw-output",
        type=Path,
        help=(
            "Output CSV path for raw.txt counts. Default: "
            "<company_directory>/<company>_raw_term_counts.csv"
        ),
    )
    parser.add_argument(
        "--statement-output",
        type=Path,
        help=(
            "Output CSV path for extracted_company_statement.txt counts. Default: "
            "<company_directory>/<company>_statement_term_counts.csv"
        ),
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Use case-sensitive regex matching. Default matching ignores case.",
    )
    return parser.parse_args()


def load_patterns(term_path: Path, *, case_sensitive: bool) -> list[tuple[str, re.Pattern[str]]]:
    if not term_path.is_file():
        raise FileNotFoundError(f"Term list not found: {term_path}")

    flags = re.MULTILINE if case_sensitive else re.IGNORECASE | re.MULTILINE
    patterns: list[tuple[str, re.Pattern[str]]] = []
    for line_number, line in enumerate(term_path.read_text(encoding="utf-8").splitlines(), 1):
        term = line.strip()
        if not term or term.startswith("#"):
            continue
        try:
            patterns.append((term, re.compile(term, flags)))
        except re.error as exc:
            raise ValueError(f"Invalid regex in {term_path} line {line_number}: {term}") from exc

    if not patterns:
        raise ValueError(f"No regex terms found in {term_path}")
    return patterns


def resolve_company_dir(company: str, dataset_dir: Path) -> Path:
    company_path = Path(company)
    if company_path.is_dir():
        return company_path

    matches = sorted(path for path in dataset_dir.glob(f"*/{company}") if path.is_dir())
    if not matches:
        raise FileNotFoundError(
            f"Could not find company directory for '{company}' under {dataset_dir}"
        )
    if len(matches) > 1:
        joined = "\n".join(f"  {path}" for path in matches)
        raise ValueError(
            f"Found multiple company directories for '{company}'. Pass a path instead:\n{joined}"
        )
    return matches[0]


def count_file(path: Path, patterns: list[tuple[str, re.Pattern[str]]]) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {term: len(pattern.findall(text)) for term, pattern in patterns}


def iter_company_documents(company_dir: Path, file_name: str) -> list[tuple[Path, Path]]:
    documents: list[tuple[Path, Path]] = []
    for source_dir in sorted(path for path in company_dir.iterdir() if path.is_dir()):
        text_path = source_dir / file_name
        if text_path.is_file():
            documents.append((source_dir, text_path))

    return documents


def write_counts(
    output_path: Path,
    company_dir: Path,
    patterns: list[tuple[str, re.Pattern[str]]],
    file_name: str,
) -> int:
    documents = iter_company_documents(company_dir, file_name)
    headers = ["source_id", *[term for term, _pattern in patterns]]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

        for source_dir, text_path in documents:
            counts = count_file(text_path, patterns)
            writer.writerow(
                {
                    "source_id": source_dir.name,
                    **counts,
                }
            )

    return len(documents)


def main() -> int:
    args = parse_args()

    try:
        company_dir = resolve_company_dir(args.company, args.dataset)
        patterns = load_patterns(args.terms, case_sensitive=args.case_sensitive)
        raw_output_path = args.raw_output or company_dir / f"{company_dir.name}_raw_term_counts.csv"
        statement_output_path = (
            args.statement_output
            or company_dir / f"{company_dir.name}_statement_term_counts.csv"
        )
        raw_row_count = write_counts(raw_output_path, company_dir, patterns, "raw.txt")
        statement_row_count = write_counts(
            statement_output_path,
            company_dir,
            patterns,
            "extracted_company_statement.txt",
        )
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {raw_row_count} raw rows to {raw_output_path}")
    print(f"Wrote {statement_row_count} statement rows to {statement_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
