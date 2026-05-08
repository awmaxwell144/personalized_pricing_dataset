# Data Processing Instructions

You will be given a company name as it appears in the `dataset/` directory (e.g., `booking-holdings`, `delta`, `kroger`). Complete the five steps below **in order**.

---

## Step 1: Locate the Company Directory

- Find the company's directory at `dataset/<industry>/<company>/`.
- List all subdirectories — each one is a source folder to process.
- Files in the company directory (e.g., `source_tracker.csv`, CSV outputs) are not source folders; skip them.

---

## Step 2: Data Cleanup

Audit every source folder before processing:

- **Duplicates**: Compare folder names and file contents across all source folders. If two folders cover the same source, report both names to the user and wait for guidance before continuing.
- **Scrape quality**: Open `raw.txt` in each source folder and confirm it contains the actual article or document text. If a page failed to scrape — returned a CAPTCHA, "verify you're human" wall, login prompt, or near-empty boilerplate — stop processing, and give the user a list of which sources need to be fixed


---

## Step 3: Build or Update `source_tracker.csv`

Create or update `dataset/<industry>/<company>/source_tracker.csv` with one row per source folder.

**Primary inputs**: `metadata.json` and `raw.txt`.  
**Fall back to** `raw.html` or `raw.pdf` only when `raw.txt` is missing or contains too little usable text.

### Field Definitions

| Field | Description |
|---|---|
| `source_id` | Short unique ID matching or closely resembling the source folder name. |
| `industry` | Industry category from `metadata.json`, e.g. `aviation`, `grocery`, `accommodation`. |
| `company` | Company name from `metadata.json`. |
| `source_title` | Title of the source, enclosed in double quotation marks in the cell, e.g. `"Delta Air Lines Q2 2025 Earnings Call Corrected Transcript"`. |
| `source_publisher` | Outlet, organization, agency, court, company, or platform that published the source. |
| `source_type` | Kind of source: `news article`, `company statement`, `privacy policy`, `lawsuit`, `letter`, `earnings call`, `social media post`, etc. |
| `source_origin` | `company`, `third party`, or `third party with company statement`. Use `third party with company statement` when an outside source includes a quoted, paraphrased, or otherwise attributable statement from the company. |
| `url` | Original URL from `metadata.json`. |
| `publication_date` | Date the source was published, filed, posted, released, or last updated. Infer from the content or URL if not in `metadata.json`. |
| `access_date` | Date the source was accessed or saved, from `metadata.json`. |
| `pricing_terms_used` | Exact pricing-related terms used in the source, e.g. `dynamic pricing`, `personalized pricing`, `AI pricing`, `surveillance pricing`, `personalized discounts`. List all that appear; separate with `, `. |
| `information_tracked` | Types of data the source says the company uses to set or display prices, in quotes, e.g. `"purchase history, browsing behavior, geolocation, device type"`. Use `"none stated"` if the source does not identify any data inputs. |
| `company_position` | The company's stance toward the pricing practice described, if discernible: `admits`, `denies`, `clarifies/qualifies`, `no response`, `third-party allegation only`, or `unclear`. |
| `summary` | Concise but informative summary covering: the source's main point, the pricing practice or allegation at issue, relevant data or AI claims, and any company response or legal/policy context. A few sentences. |
| `key_excerpts` | One or more excerpts that capture the source's main claim, framing, or evidence. Separate multiple excerpts with ` \| `. |

### CSV Formatting Rules

- Wrap any cell that contains commas, double quotes, or newlines in double quotes.
- Escape internal double quotes by doubling them (`""`).
- Verify the file parses as valid CSV before saving.

---

## Step 4: Extract Company Statements

For every source where `source_origin` is `third party with company statement`:

1. Read the full `raw.txt` for that source.
2. Extract every sentence or passage that conveys the company's official position, direct quotes, or attributable responses — anything a journalist or researcher would identify as the company speaking.
3. Save the extracted text as `extracted_company_statement.txt` inside that source's folder.

If no sources qualify, skip this step entirely.

---

## Step 5: Count Term Matches

Run the following command from the **repository root**:

```
python3 utilities/count_terms.py <company>
```

Example:

```
python3 utilities/count_terms.py booking-holdings
```

This reads regexes from `utilities/term_list.txt` and writes two CSVs to the company directory:

- `<company>_raw_term_counts.csv` — term counts across all `raw.txt` files.
- `<company>_statement_term_counts.csv` — term counts across all `extracted_company_statement.txt` files.

If Step 4 was skipped (no extracted statement files exist), the statement counts CSV will be empty — this is expected.
