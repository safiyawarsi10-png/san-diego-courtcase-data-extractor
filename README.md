# Data Collection & Research

*San Diego Criminal Cases Automation Toolkit*

---

## 📖 Purpose

This toolkit builds a **transparent, auditable dataset** of San Diego homicide cases to investigate whether the District Attorney’s office treats juvenile and emerging-adult defendants more harshly than older adults.

We aim to:

* Extract core facts (defendant name, birth year, filing date) from court records.
* Collect crime dates and sentencing outcomes using AI-assisted research.
* Compute defendant ages at crime time and classify into:

  * Juvenile (<18)
  * Emerging Adult (18–26)
  * Adult (>26)
* Provide a reproducible and transparent process with clear audit trails.

---

## 📂 Background

The research question: **Does sentencing vary by race for juveniles and emerging adults?**

Scope: \~1,300 San Diego homicide cases.

Data collected includes:

* Defendant demographics
* Crime details (date, type)
* Case outcomes (sentence length/type)
* Filing dates & court info

---

## ⚠️ Challenges Without Automation

Manual research for 1,300+ cases would take **480+ hours** due to:

* Court website session expirations
* Paywalled/broken news archives
* Name variations & co-defendant confusion
* Ambiguous dates
* Incomplete data

---

## 🤖 Automated Hybrid Approach

This toolkit automates \~85–90% of the work:

### 1. Court Data Extraction (`step1_fetch_cases_playwright.py`)

* Automates court website lookups
* Extracts defendant names, birth years, filing dates
* Handles multi-defendant cases
* Saves results into Excel

### 2. GPT-Assisted News Research

* Uses custom GPT tool to find crime dates, sentences, and sources
* Extracts structured facts for each case
* Provides source URLs for transparency

### 3. Human Oversight

* Calculate ages & categorize into Juvenile/Emerging Adult/Adult
* Review cases with missing or low-confidence data
* Validate sources before analysis

⏱ **Time savings**: 480+ hours → \~40–60 hours total.

---

## 🖥️ Requirements

* **OS:** Windows, macOS, or Linux
* **Python:** 3.x installed
* **Storage:** \~500MB for software, \~50MB for data
* **Accounts:** ChatGPT (for custom extractor GPT)

### Python Packages

```bash
pip install playwright pandas openpyxl requests
playwright install chromium
```

---

## ⚙️ Setup & Usage

### Step 1: Court Data Extraction

```bash
python step1_fetch_cases_playwright.py SESSION_ID cases.txt
```

* Inputs: session ID + case numbers file
* Output: `cases_dob_extracted.xlsx`

### Step 2: GPT-Assisted Research

* Open the **Criminal Case Extractor GPT**
* Copy case details from Excel → paste into GPT
* Get JSON output with crime date, sentence, sources
* Paste results back into Excel

### Step 3: Manual Review

* Compute age at crime
* Assign age category
* Review flagged cases
* Fill gaps via manual research if needed

---

## 📊 Expected Results

* **Court Data Extraction:** \~95–98% success
* **GPT-Assisted Research:** \~75–90% success
* **Complete Dataset:** \~70–85% of cases fully populated
* **Manual Review Needed:** \~15–30% of cases

---

## 🛠️ Troubleshooting

* **Expired Session:** Get a fresh `JSESSIONID` from the court site.
* **GPT Not Finding Cases:** Try alternate spellings or remove middle names.
* **Rate Limits:** Pause or upgrade to ChatGPT Plus.
* **Excel Issues:** Use backup files with `_BACKUP_` suffix.

---

## 💡 Tips for Success

* Start with 10–20 test cases before scaling.
* Monitor progress — scripts print updates and save frequently.
* Expect 15–30% of cases to require manual review.
* Keep backups of all input and output files.

---

## 📌 Why This Matters

This dataset helps us understand whether the justice system treats young defendants differently from older adults. The transparent, reproducible workflow ensures credible findings that can be audited and trusted.

---

## 📎 Appendix: Example Command

```bash
python3 step1_fetch_cases_playwright.py A1B2C3D4E5F6 san_diego_cases.txt
```

Output:

* Extracted defendant data
* Excel file with crime dates & sentencing (after GPT step)
* Audit trail with source URLs

---

## 🙌 Contributing

If you’d like to help, please:

1. Clone the repo
2. Run the pipeline on a subset of cases
3. Submit improvements (documentation, bug fixes, validation checks)

---

## 📄 License

MIT License — free to use, modify, and distribute with attribution.
