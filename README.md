# San Diego Criminal Cases – Data Collection & Research

*An automation toolkit for building an auditable dataset of San Diego homicide cases*

> **Audience:** Investigative journalists, public-interest lawyers, researchers, and technically-minded volunteers. Comfortable running Python scripts; no prior court-data scraping experience required.

---

## Table of Contents

* [1. Overview — Why this exists](#1-overview--why-this-exists)
* [2. What the toolkit does](#2-what-the-toolkit-does)
* [3. Who should use this](#3-who-should-use-this)
* [4. What data we collect](#4-what-data-we-collect)
* [5. Ethics, transparency, and auditability](#5-ethics-transparency-and-auditability)
* [6. Requirements](#6-requirements)
* [7. Installation](#7-installation)
* [8. Getting your court session ID (JSESSIONID)](#8-getting-your-court-session-id-jsessionid)
* [9. Project layout](#9-project-layout)
* [10. Step 1 — Extract court data](#10-step-1--extract-court-data)
* [11. Step 2 — GPT‑assisted research for crime dates & sentences](#11-step-2--gptassisted-research-for-crime-dates--sentences)
* [12. Data model (columns & meanings)](#12-data-model-columns--meanings)
* [13. Quality control & manual review](#13-quality-control--manual-review)
* [14. Expected success rates](#14-expected-success-rates)
* [15. Troubleshooting](#15-troubleshooting)
* [16. Time & cost expectations](#16-time--cost-expectations)
* [17. Tips for success](#17-tips-for-success)
* [18. Roadmap — Ways to evolve this project](#18-roadmap--ways-to-evolve-this-project)
* [19. FAQ](#19-faq)
* [20. License & disclaimer](#20-license--disclaimer)
* [21. Acknowledgments](#21-acknowledgments)

---

## 1. Overview — Why this exists

We are building a **structured, auditable dataset** of San Diego homicide cases to answer a focused question: *Are juvenile and emerging‑adult defendants (under 26) treated more harshly—or more leniently—than older adults?* The pipeline is intentionally transparent:

**Court docket lookup → AI‑assisted news/legal research → derived age fields → human QC flags.**

This end‑to‑end process lets independent reviewers audit each record, reproduce results, and trust any bias analysis we publish.

---

## 2. What the toolkit does

This repo contains a **hybrid automation** that removes 85–90% of the manual toil:

### 2.1 Court Data Extraction — `step1_fetch_cases_playwright.py`

* Navigates the San Diego Superior Court public portal across all locations
* Manages sessions/authentication and common site errors
* Extracts **defendant name, birth year, filing date, location**, and docket URL
* Handles multi‑defendant cases and saves **Excel output** (resumable)

### 2.2 GPT‑Assisted Research (semi‑automated)

* A purpose‑built GPT workflow finds **crime dates, sentences, and source URLs**
* Prioritizes appellate decisions and official records; falls back to reputable news
* Returns **structured JSON** you paste into the spreadsheet

### 2.3 Human Oversight (critical)

* Calculate **age at crime** and categorize (Juvenile / Emerging Adult / Adult)
* Resolve conflicts, fill gaps, and add **confidence notes**

⏱ **Net impact:** months of manual research → **\~40–60 hours total** for \~1,300 cases (order‑of‑magnitude reduction).

---

## 3. Who should use this

* Journalists evaluating public‑interest questions about local justice systems
* Defense/prosecution analysts or policy advocates conducting **sentencing equity** reviews
* Researchers who need a **reproducible audit trail** for peer review

---

## 4. What data we collect

* **Defendant**: full name, birth year (YYYY), race (if explicitly stated in reliable sources)
* **Court**: case number, filing date, location, docket URL
* **Offense**: crime date (not the trial/sentencing date), crime type
* **Outcome**: specific sentence received; plea vs. trial; juvenile vs. adult court
* **Derived**: age at crime; age band (Juvenile <18, Emerging Adult 18–26, Adult >26)
* **Provenance**: article/opinion URLs; notes and confidence

---

## 5. Ethics, transparency, and auditability

* Every fact is **source‑linked**; ambiguous fields are annotated (e.g., “DOB≈1993 from press release”).
* **Verification order** (highest→lowest): appellate decisions → trial records/official documents → DA/LE releases → major newspapers → local outlets → general news.
* If details cannot be verified, leave fields blank and mark **confidence** accordingly.

---

## 6. Requirements

**OS:** Windows, macOS, or Linux
**Python:** 3.9+ recommended
**Storage:** \~500 MB software + \~50 MB data
**Network:** Stable broadband
**Time:** \~2–3 hours for setup; Step 1 can run unattended
**Accounts:** ChatGPT (for the custom extractor GPT)

### 6.1 Packages

```bash
pip install playwright pandas openpyxl requests
playwright install chromium
```

---

## 7. Installation

```bash
# 1) Create & activate a virtual environment (recommended)
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt  # if present
# or install explicitly
pip install playwright pandas openpyxl requests
playwright install chromium
```

---

## 8. Getting your court session ID (JSESSIONID)

1. Visit: [https://courtindex.sdcourt.ca.gov/CISPublic/](https://courtindex.sdcourt.ca.gov/CISPublic/)
2. Run any search to start a session.
3. Open **Developer Tools** → *Application* → *Storage* → *Cookies*.
4. Copy the value of `JSESSIONID` (looks like `A1B2C3D4E5F6.worker1`).

> Keep this private. Sessions expire; you may need a fresh ID during long runs.

---

## 9. Project layout

```
project/
├─ step1_fetch_cases_playwright.py
├─ your_cases.txt                  # one case number per line (e.g., CN367913)
├─ output/
│  ├─ san_diego_cases_dob_extracted.xlsx
│  └─ backups/ *_BACKUP_HHMMSS.xlsx
└─ README.md
```

---

## 10. Step 1 — Extract court data

Run the extractor (replace placeholders):

```bash
python step1_fetch_cases_playwright.py <JSESSIONID> <path/to/cases.txt>
```

**Example**

```bash
python step1_fetch_cases_playwright.py A1B2C3D4E5F6 san_diego_cases.txt
```

**What happens**

* Launches a headless Chromium session and visits the court portal for each case
* Collects **name, birth year, filing date, location**, and the **docket URL**
* Writes **`*_dob_extracted.xlsx`** to `./output` and creates rolling **backup files**
* **Resumable**: safe to interrupt with `Ctrl+C`; reruns skip finished rows

**Throughput:** \~5 seconds per case (≈100 minutes for 1,200 cases) depending on network and rate limits.

---

## 11. Step 2 — GPT‑assisted research for crime dates & sentences

This semi‑automated phase uses a specialized GPT workflow.

### 11.1 What you’ll do

1. Open the **Criminal Case Extractor GPT** in ChatGPT.
2. From the Excel row, copy **case title, case number, location, date filed**.
3. Paste into GPT and submit.
4. GPT returns **structured JSON** (crime date, sentence, up to 3 sources).
5. Paste results back into the spreadsheet (see mapping below).

### 11.2 Example JSON returned

```json
{
  "crime_date": "2009-12-20",
  "sentence": "25 years to life",
  "sources": [
    "https://example-news-source.com/article1",
    "https://court-documents.com/case2"
  ]
}
```

### 11.3 Mapping JSON → Spreadsheet

* `crime_date` → **CrimeDate**
* `sentence` → **Sentence**
* `sources[0]` → **Source\_ArticleURL** (or official source if available)

> Tip: Prefer appellate opinions and official documents. Use major outlets next; avoid blogs of dubious quality.

---

## 12. Data model (columns & meanings)

| Column             | Description                                        | Source     |
| ------------------ | -------------------------------------------------- | ---------- |
| CaseNumber         | Court case identifier                              | Input file |
| DefendantName      | Full name from court records                       | Step 1     |
| DOB                | Birth year (YYYY)                                  | Step 1     |
| DateFiled          | Filing date                                        | Step 1     |
| CaseLocation       | North County / San Diego / East / South            | Step 1     |
| CrimeDate          | Date the offense occurred                          | Step 2     |
| AgeAtCrime         | Calculated numeric age                             | Step 3     |
| AgeBand            | Juvenile / Emerging Adult / Adult                  | Step 3     |
| Sentence           | Specific sentence imposed                          | Step 2     |
| DefendantRace      | Only if explicitly stated in reliable sources      | Step 2     |
| DAEra              | e.g., "Bonnie Dumanis" (constant for this dataset) | Step 1     |
| Source\_DocketURL  | Court record link                                  | Step 1     |
| Source\_ArticleURL | News or opinion link                               | Step 2     |
| Notes              | QC flags, assumptions, comments                    | All steps  |

---

## 13. Quality control & manual review

* Compute **AgeAtCrime** = floor((CrimeDate − DOB)) and assign **AgeBand**.
* Add **confidence** notes (e.g., *low*: only one minor source; *high*: appellate opinion + docket).
* When GPT returns **no information**, leave cells blank or write `NO INFO` in **Notes** and revisit.
* Explicitly distinguish **crime date vs. filing/sentencing dates**.

---

## 14. Expected success rates

* Court data extraction: **95–98%** rows populated
* GPT‑assisted research: **75–90%** (case‑coverage dependent)
* Fully complete records: **70–85%**
* Manual follow‑up required: **15–30%**

---

## 15. Troubleshooting

**Session test failed**

* Refresh `JSESSIONID` (start a new search on the portal) and rerun.

**GPT finds nothing**

* Remove middle names/suffixes; try nickname variations; verify **DateFiled**.

**Rate limiting / site blocks**

* Pause 10–15 minutes. Run batches of **50–100** cases.

**Excel won’t open / partial writes**

* Use the auto‑generated backups in `output/backups/`.

---

## 16. Time & cost expectations

* **Setup:** 2–3 hours
* **Step 1:** 4–8 hours for \~1,300 cases (can run unattended)
* **Step 2:** 8–15 hours with human input
* **Manual QC:** 10–20 hours (data‑quality dependent)
* **ChatGPT usage:** Free tier is limited; Plus may be helpful for uninterrupted runs.

---

## 17. Tips for success

* Start with **10–20 test cases** to validate the full pipeline.
* Keep **backups** of input files and Excel outputs.
* Track which rows have been **GPT‑processed**.
* Prefer **legal sources**; cross‑check critical facts with at least two sources.

---

## 18. Roadmap — Ways to evolve this project

**Automation & Data Quality**

* Automate Step 2 with targeted search APIs; add **source‑ranking** by reliability
* Add **name‑disambiguation** and co‑defendant resolution heuristics
* Integrate appellate opinion scraping (e.g., California Courts opinions) with parsing
* Implement **retry/backoff & proxy rotation** for court portal stability
* Add **deduplication** and near‑duplicate article detection

**Engineering & Ops**

* Package as a CLI (`pipx`), add `pyproject.toml` and entry points
* Provide a **Dockerfile** for reproducible runs
* Continuous integration for lint/tests; structured logs & metrics
* Switch spreadsheet output to **CSV/Parquet** and ship to a lightweight DB
* Orchestrate with **Prefect/Airflow** for large batches; add caching

**Research Extensions**

* Generalize to other counties/states (configurable court portals/news sources)
* Add **bias‑analysis notebooks** (chi‑square, logistic regression) with ready‑made charts
* Publish an **interactive dashboard** (Streamlit) for filtering and exports
* Add **anonymization** or case‑redaction modes for public sharing

---

## 19. FAQ

**Is this legal advice?** No. This is a research utility and does not replace counsel.
**Does this scrape paywalled content?** No. Use only public pages or sources you have rights to access.
**Why not fully automate Step 2?** Jurisdictional variation, paywalls, and name collisions make human judgment valuable.
**Can I use another LLM?** Yes. The prompt design is model‑agnostic; accuracy depends on source selection and verification.

---

## 20. License & disclaimer

Released under the **MIT License**. Use at your own risk. Respect website terms of service and privacy laws. This repository is for research and journalism support, **not legal advice**.

---

## 21. Acknowledgments

Thanks to volunteers and contributors who helped build a transparent, reproducible workflow for public‑interest analysis.
