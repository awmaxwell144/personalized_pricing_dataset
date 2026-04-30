"""
scrape.py

OVERVIEW:
---------
This script saves a webpage or PDF into the project dataset.

Dataset structure:

dataset/<industry>/<company>/<page-name>/
  raw.html      if available
  raw.pdf       if available
  raw.txt       if available
  metadata.json

USAGE:
------
python scrape.py "<URL>" "<industry>" "<company>"

Optional:
---------
python scrape.py "<URL>" "<industry>" "<company>" "<page-name>"
"""

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests
from bs4 import BeautifulSoup


DATASET_DIR = Path("dataset")


def clean_name(name: str) -> str:
    """Convert a user-provided name into a safe folder name."""
    name = name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"_+", "-", name)
    name = re.sub(r"\s+", "-", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-")


def fetch_url(url: str) -> requests.Response:
    """Fetch the URL and return the server response."""
    print("[1/8] Fetching URL...")

    headers = {
        "User-Agent": "Mozilla/5.0 dataset-scraper/1.0"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    print(f"      Fetched successfully. Status code: {response.status_code}")
    return response


def detect_source_type(response: requests.Response, url: str) -> str:
    """Detect whether the original URL points to HTML, PDF, or plain text."""
    print("[2/8] Detecting source type...")

    content_type = response.headers.get("Content-Type", "").lower()
    path = urlparse(url).path.lower()

    if "application/pdf" in content_type or path.endswith(".pdf"):
        print("      Detected source type: PDF")
        return "pdf"

    if "text/html" in content_type or b"<html" in response.content[:1000].lower():
        print("      Detected source type: HTML")
        return "html"

    print("      Detected source type: TXT")
    return "txt"


def get_domain_name(url: str) -> str:
    """Get a clean domain name from the URL."""
    domain = urlparse(url).netloc.lower()
    domain = domain.replace("www.", "")
    return domain


def get_url_path_name(url: str) -> str:
    """Create a readable name from the URL path."""
    path = unquote(urlparse(url).path)
    path = path.strip("/")

    if not path:
        return ""

    last_part = path.split("/")[-1]
    last_part = re.sub(r"\.(html|htm|pdf|txt)$", "", last_part, flags=re.IGNORECASE)

    return last_part


def extract_title_from_html(html: str) -> str:
    """Extract title from HTML, preferring <title>, then <h1>."""
    print("[3/8] Looking for page title...")

    soup = BeautifulSoup(html, "html.parser")

    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        print(f"      Found title from <title>: {title}")
        return title

    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
        print(f"      Found title from <h1>: {title}")
        return title

    print("      No HTML title found.")
    return ""


def build_descriptive_title(url: str, page_title: str, fallback_name: str) -> str:
    """Build a descriptive identifier using publisher/webpage + page name."""
    domain = get_domain_name(url)

    if page_title:
        return f"{domain} - {page_title}"

    if fallback_name:
        readable_fallback = fallback_name.replace("-", " ").replace("_", " ").strip()
        return f"{domain} - {readable_fallback}"

    return domain


def choose_page_name(
    url: str,
    source_type: str,
    html_title: str = "",
    user_page_name: str | None = None
) -> str:
    """Choose the folder name for this page."""
    print("[4/8] Choosing page folder name...")

    if user_page_name:
        page_name = clean_name(user_page_name)
        if page_name:
            print(f"      Using user-provided page name: {page_name}")
            return page_name

    if html_title:
        page_name = clean_name(html_title)
        if page_name:
            page_name = page_name[:80]
            print(f"      Using page title as folder name: {page_name}")
            return page_name

    path_name = get_url_path_name(url)
    if path_name:
        page_name = clean_name(path_name)
        if page_name:
            page_name = page_name[:80]
            print(f"      Using URL path as folder name: {page_name}")
            return page_name

    user_input = input(
        "      Could not automatically determine a page name. "
        "Please enter a short page name: "
    )
    page_name = clean_name(user_input)

    if not page_name:
        raise ValueError("A page name is required.")

    page_name = page_name[:80]
    print(f"      Using entered page name: {page_name}")
    return page_name


def ensure_unique_folder(folder: Path) -> Path:
    """If the folder already exists, create a numbered version."""
    if not folder.exists():
        print(f"      Destination folder will be: {folder}")
        return folder

    print(f"      Folder already exists: {folder}")
    print("      Creating a numbered folder to avoid overwriting existing data...")

    base = folder
    counter = 2

    while True:
        candidate = Path(f"{base}-{counter}")
        if not candidate.exists():
            print(f"      New destination folder will be: {candidate}")
            return candidate
        counter += 1


def html_to_text(html: str) -> str:
    """Extract readable plain text from HTML."""
    print("      Extracting readable text from HTML...")

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    return "\n".join(lines)


def pdf_to_text(pdf_path: Path) -> str:
    """Extract text from a PDF."""
    print("      Extracting readable text from PDF...")

    try:
        from pypdf import PdfReader
    except ImportError:
        print("      Skipping PDF text extraction: pypdf is not installed.")
        return ""

    try:
        reader = PdfReader(str(pdf_path))
        pages = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text.strip())

        if pages:
            print(f"      Extracted text from {len(pages)} PDF page(s).")
        else:
            print("      No extractable text found in PDF.")

        return "\n\n".join(pages)

    except Exception as e:
        print(f"      Skipping PDF text extraction: {e}")
        return ""


def save_html(response: requests.Response, folder: Path) -> Path:
    """Save raw HTML."""
    html_path = folder / "raw.html"
    html_path.write_text(response.text, encoding="utf-8")
    print(f"      Saved HTML: {html_path}")
    return html_path


def save_pdf_from_response(response: requests.Response, folder: Path) -> Path:
    """Save PDF bytes when the source URL is already a PDF."""
    pdf_path = folder / "raw.pdf"
    pdf_path.write_bytes(response.content)
    print(f"      Saved PDF: {pdf_path}")
    return pdf_path


def save_txt(text: str, folder: Path) -> Path | None:
    """Save raw.txt if there is non-empty text."""
    if not text or not text.strip():
        print("      No text available to save.")
        return None

    txt_path = folder / "raw.txt"
    txt_path.write_text(text.strip(), encoding="utf-8")
    print(f"      Saved text: {txt_path}")
    return txt_path


def convert_webpage_to_pdf(url: str, folder: Path) -> Path | None:
    """Save an HTML webpage as raw.pdf using Playwright."""
    print("      Attempting to save webpage as PDF...")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("      Skipping webpage-to-PDF: Playwright is not installed.")
        return None

    pdf_path = folder / "raw.pdf"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=45000)
            page.pdf(path=str(pdf_path), format="Letter", print_background=True)
            browser.close()

        print(f"      Saved webpage PDF: {pdf_path}")
        return pdf_path

    except Exception as e:
        print(f"      Skipping webpage-to-PDF: {e}")
        return None


def make_metadata(
    url: str,
    industry: str,
    company: str,
    page_name: str,
    source_type: str,
    title: str,
    saved_files: list[str],
):
    """Create metadata for the page folder."""
    print("[6/8] Creating metadata...")

    return {
        "url": url,
        "title": title,
        "industry": industry,
        "company": company,
        "page_name": page_name,
        "source_type": source_type,
        "saved_files": saved_files,
        "date_scraped": datetime.now(timezone.utc).isoformat(),
        "notes": ""
    }


def write_metadata(folder: Path, metadata: dict) -> Path:
    """Write metadata.json."""
    metadata_path = folder / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"      Saved metadata: {metadata_path}")
    return metadata_path


def git_commit_and_push(folder: Path, url: str):
    """Add, commit, and push the page folder to GitHub."""
    print("[8/8] Committing and pushing to GitHub...")

    try:
        print("      Running: git add")
        subprocess.run(["git", "add", str(folder)], check=True)

        commit_message = f"Add source page: {url}"

        print("      Running: git commit")
        commit = subprocess.run(
            ["git", "commit", "-m", commit_message],
            text=True,
            capture_output=True
        )

        if commit.returncode != 0:
            output = commit.stdout.lower() + commit.stderr.lower()

            if "nothing to commit" in output:
                print("      No changes to commit.")
                return

            print(commit.stdout)
            print(commit.stderr)
            raise RuntimeError("Git commit failed.")

        print("      Running: git push")
        subprocess.run(["git", "push"], check=True)

        print("      Changes pushed to GitHub.")

    except Exception as e:
        print("\nSaved files successfully, but Git failed.")
        print("Run manually:")
        print("  git add .")
        print('  git commit -m "added page"')
        print("  git push")
        print(f"Git error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape a webpage or PDF into the dataset folder."
    )

    parser.add_argument("url", help="URL of the webpage or PDF")
    parser.add_argument("industry", help="Industry folder name")
    parser.add_argument("company", help="Company folder name")
    parser.add_argument(
        "page_name",
        nargs="?",
        default=None,
        help="Optional page folder name. If omitted, the script will choose one automatically."
    )

    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Save files but do not commit or push to GitHub"
    )

    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip converting webpages to PDF"
    )

    args = parser.parse_args()

    print("\nStarting scrape process...")
    print(f"URL: {args.url}")

    print("\nPreparing folder names...")
    industry = clean_name(args.industry)
    company = clean_name(args.company)
    print(f"Industry folder: {industry}")
    print(f"Company folder: {company}")

    response = fetch_url(args.url)
    source_type = detect_source_type(response, args.url)

    html_title = ""
    if source_type == "html":
        html_title = extract_title_from_html(response.text)
    else:
        print("[3/8] Looking for page title...")
        print("      Source is not HTML, so no HTML title extraction.")

    page_name = choose_page_name(
        url=args.url,
        source_type=source_type,
        html_title=html_title,
        user_page_name=args.page_name
    )

    folder = DATASET_DIR / industry / company / page_name
    folder = ensure_unique_folder(folder)

    print("\nCreating dataset folder...")
    folder.mkdir(parents=True, exist_ok=True)
    print(f"Created folder: {folder}")

    saved_files = []
    title = build_descriptive_title(
        url=args.url,
        page_title=html_title,
        fallback_name=page_name
    )

    print("[5/8] Saving page content...")

    if source_type == "pdf":
        print("      Source is a PDF.")
        pdf_path = save_pdf_from_response(response, folder)
        saved_files.append(pdf_path.name)

        text = pdf_to_text(pdf_path)
        txt_path = save_txt(text, folder)
        if txt_path:
            saved_files.append(txt_path.name)

    elif source_type == "html":
        print("      Source is HTML.")
        html_path = save_html(response, folder)
        saved_files.append(html_path.name)

        text = html_to_text(response.text)
        txt_path = save_txt(text, folder)
        if txt_path:
            saved_files.append(txt_path.name)

        if not args.no_pdf:
            pdf_path = convert_webpage_to_pdf(args.url, folder)
            if pdf_path:
                saved_files.append(pdf_path.name)
        else:
            print("      Skipping PDF conversion because --no-pdf was used.")

    else:
        print("      Source is plain text or unknown type.")
        txt_path = save_txt(response.text, folder)
        if txt_path:
            saved_files.append(txt_path.name)

    metadata = make_metadata(
        url=args.url,
        industry=industry,
        company=company,
        page_name=folder.name,
        source_type=source_type,
        title=title,
        saved_files=saved_files,
    )

    metadata_path = write_metadata(folder, metadata)
    saved_files.append(metadata_path.name)

    print("[7/8] Final check...")
    print(f"      Saved dataset item to: {folder}")
    print(f"      Title: {title}")
    print("      Files saved:")
    for file in saved_files:
        print(f"        - {file}")

    if not args.no_git:
        git_commit_and_push(folder, args.url)
    else:
        print("[8/8] Skipping Git commit/push because --no-git was used.")

    print("\nDone.")


if __name__ == "__main__":
    main()