# Personalized Pricing Dataset

This repository contains the source dataset and collection utilities for a COS 351 research project on personalized algorithmic pricing, dynamic pricing, AI pricing, and related company communications.

The dataset supports the paper's analysis of how companies characterize pricing practices and how those communications change around legal, media, and public-pressure events.

## Repository Structure

```text
.
├── dataset/                 # Collected source material, organized by industry and company
├── utilities/               # Term counting script, term list, and data templates
├── scrape.py                # Helper script for saving webpages and PDFs into dataset/
└── data_processing.md       # Step-by-step prompt for the agent processing a company
```

The dataset is organized as:

```text
dataset/<industry>/<company>/<source-id>/
```

Each source folder may contain:

- `raw.html` - saved HTML when available
- `raw.pdf` - saved PDF or PDF rendering when available
- `raw.txt` - extracted readable text
- `metadata.json` - URL, scrape date, source type, title, and saved-file metadata
- `extracted_company_statement.txt` - company statements extracted from third-party sources, when relevant

Each company directory may also contain:

- `<company>_source_tracker.csv` - source-level metadata and summaries
- `<company>_raw_term_counts.csv` - term counts across `raw.txt`
- `<company>_statement_term_counts.csv` - term counts across extracted company statements

## Dataset Scope

The current dataset covers companies in four broad industries:

- `accommodation`
- `aviation`
- `grocery`
- `rideshare`

Sources include company communications, privacy policies, investor materials, news coverage, legal or regulatory materials, watchdog reports, and public-pressure sources where they are directly relevant to a company's pricing practices.

## Setup

Install Python dependencies from the repository root:

```bash
pip3 install -r utilities/requirements.txt
python3 -m playwright install chromium
```

If your system uses `python` instead of `python3`, use the corresponding `pip` and `python` commands.

## Adding a Source

Use `scrape.py` to save a webpage, PDF, or plain-text URL into the dataset:

```bash
python3 scrape.py "<URL>" "<industry>" "<company>"
```

You can optionally provide the source folder name:

```bash
python3 scrape.py "<URL>" "<industry>" "<company>" "<source-id>"
```

Useful flags:

```bash
python3 scrape.py "<URL>" "<industry>" "<company>" --no-git
python3 scrape.py "<URL>" "<industry>" "<company>" --no-pdf
```

- `--no-git` saves files without committing or pushing.
- `--no-pdf` skips PDF rendering for HTML webpages.

By default, the script saves the source under `dataset/<industry>/<company>/<source-id>/`, writes `metadata.json`, extracts text into `raw.txt` when possible, and attempts to commit and push the new source.

## Processing a Company

After sources have been collected for a company, follow `data_processing.md`.

The basic workflow is:

1. Review each source folder for duplicates and scrape-quality problems.
2. Create or update `<company>_source_tracker.csv`.
3. Extract company statements from third-party sources when applicable.
4. Count pricing-related term matches.

Run term counts from the repository root:

```bash
python3 utilities/count_terms.py <company>
```

Example:

```bash
python3 utilities/count_terms.py delta
```

The script reads regex patterns from `utilities/term_list.txt` and writes updated count CSVs to the relevant company directory.

## Notes for Contributors

- Keep source folder names short, lowercase, and descriptive.
- Do not overwrite existing source folders. The scraper will create a numbered folder if a name already exists.
- Check `raw.txt` after scraping. Some websites return login pages, CAPTCHA pages, or incomplete text.
- Use `metadata.json` and `raw.txt` as the primary inputs for source trackers.
- Keep source summaries factual and distinguish company claims, third-party allegations, and legal or regulatory findings.
