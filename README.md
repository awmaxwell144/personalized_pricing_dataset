# Personalized Pricing Dataset

## Dataset Generation
After you have done the setup:

Run 
```
python3 scrape.py "<URL>" "<industry>" "<company>"
```
If you get an error saying something like "python3 not found," try it with `python` instead of `python3`

Scrape.py does:
- Downloads a webpage, PDF, or text URL and saves it into:
  ```
  dataset/<industry>/<company>/<page-name>/
  ```
- Automatically chooses a page folder name from the webpage title or URL path, or you can provide one:
  ```
  python3 scrape.py "<URL>" "<industry>" "<company>" "<page-name>"
  ```
- Saves the source as `raw.html`, `raw.pdf`, and/or `raw.txt`, depending on the URL type.
- Extracts readable text into `raw.txt` when possible.
- Writes `metadata.json` with basic information about the source.
- Avoids overwriting existing folders by creating a numbered folder if needed.
- Commits and pushes the new dataset item to GitHub automatically.

Optional flags:
```
python3 scrape.py "<URL>" "<industry>" "<company>" --no-git
python3 scrape.py "<URL>" "<industry>" "<company>" --no-pdf
```

- `--no-git` saves the files but skips the automatic Git commit and push.
- `--no-pdf` skips converting an HTML webpage into a PDF.

## Setup

Follow these steps to get the dataset set up locally. If something doesn't work, try putting the error in an LLM. If not, text me

### 1. Accept the GitHub Invite
- Go to the email you used to sign up for GitHub
- Find the email inviting you to the repository
- Click the link and **accept the invite**

---

### 2. Open VSCode
- Open **VSCode**
- Open whatever folder you want this dataset to live in  
  (for example, a `COS351` folder)

---

### 3. Open a Terminal in VSCode
- In the top menu, click **Terminal**
- Click **New Terminal**

---

### 4. Install Git (if not already installed)

Run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git
```

---

### 5. Configure Git

Replace with your username and email:
```
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

---

### 6. Clone the Repository

```
git clone https://github.com/awmaxwell144/personalized_pricing_dataset.git
```
At this point, you should see a new folder called: `personalized_pricing_dataset` in your VSCode

---

### 7. Open the Project Folder
- In VSCode, go to File → Open Folder
- Navigate to the `personalized_pricing_dataset` folder
- Open it

---

### 8. Install Python (if you don't have it)

1. Go to: https://www.python.org/downloads/macos/
2. Download the latest **Python 3 installer (.pkg)** (the one at the top)
3. Open the downloaded file and follow the installation steps

---

#### Verify Installation

After installing, restart your terminal and run:

```bash
python3 --version
```
You should see something like: `Python 3.x.x`

---

### 9. Install Dependencies
Run the following:
```
pip3 install -r utilities/requirements.txt
python -m playwright install chromium
```
