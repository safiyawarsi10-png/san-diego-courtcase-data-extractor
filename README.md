# San Diego Criminal Cases -- Data Collection & Research

*An automation toolkit for building an auditable dataset of San Diego criminal court cases*

> **Audience:** Investigative journalists, public‑interest lawyers, researchers, and technically‑minded volunteers. Comfortable running Python scripts; no prior court‑data scraping experience required.

---

## 0. Core goal

**Purpose**  
This document outlines the research process and tools used by our team and volunteers to build a **transparent dataset for bias analysis**. We're building a structured, auditable dataset of San Diego criminal court cases so we can ask a set of **clear, testable questions** about fairness and consistency in charging and sentencing.

**Concretely, we're:**
- **Assembling core facts** (defendant name, birth‑year, filing date) directly from the Superior Court's public **Case Detail** pages (via the court index link).  
- **Pulling in crime dates and sentencing outcomes** from reputable local news or appellate opinions using a **custom GPT tool**.  
- **Computing exact or best‑available age at the time of the crime**, then bucketing into: Juvenile (<18), Emerging Adult (18–26), Adult (>26).  
- **Flagging any gaps or estimates** in our data (e.g., `DOB≈1993 inferred from press release`) so **nothing is hidden**.

**What questions can this dataset answer? (examples)**  
- Are juveniles or emerging adults more/less likely to receive harsher sentences?  
- Holding age and §190.2 status constant, do outcomes vary by race?  
- How often are special circumstances (§190.2) charged/applied, and do they explain sentence differences?  
- Do plea outcomes differ from trial outcomes across groups?  
- Do outcomes vary across court locations?  
- Are there shifts over time or between DA tenures?  
- Within the same case, do similarly situated co‑defendants receive different sentences?  

**Why this matters**  
Once every record has a verified crime date, a birth‑year, the sentence, and source URLs, you can pivot and filter across groups, and run statistics (rate ratios, chi‑square, logistic regression) to test for differences that are **material and reproducible**.

**Our pipeline, at a glance**  
Court lookup → GPT‑assisted news/legal research → Derived fields (ages, bands, §190.2 status) → QC flags.

---

## 1. Overview — Why this exists

### Background (plain English)
This toolkit supports research into potential **racial bias in criminal sentencing**, specifically examining how **age intersects with race** in criminal case outcomes.

- **Research Question:** Does sentencing vary by race for defendants who were **juveniles (<18)** or **emerging adults (18–26)** when they committed serious crimes in San Diego?  
- **Data Scope:** Approximately 1,300 case numbers covering San Diego criminal cases.  
- **Key variables:** demographics, crime details, outcomes, age analysis, filing dates, locations, and docket links.

### 1.1 The real‑world problem
Public criminal court records in California are **fragmented** across court index pages, opinions, and news. For fairness work, you need the same fields consistently, backed by links.

### 1.2 Our design goals
- **Auditability:** Every row has URLs and notes.  
- **Reproducibility:** Given the same input, another team should produce the same sheet.  
- **Accessibility:** Uses Excel, not databases.  
- **Human‑in‑the‑loop:** Avoids full automation; humans make the final call.

### 1.3 Why age and §190.2 matter
- **Age at crime** defines Juvenile / Emerging Adult / Adult.  
- **Special circumstances (Penal Code §190.2)** determine punishment exposure.

### 1.4 Workflow grounding
Each Step 2 session starts from the docket, attaches evidence, and produces JSON with sources.

### 1.5 What this unlocks
- Spot patterns (sentence distributions, presence/absence of §190.2).  
- Retrace any row back to a document.  
- Extend later with new counties, columns, or analyses.

### 1.6 Guardrails
- Don’t confuse crime date with filing/sentencing date.  
- Prefer official sources over media.  
- Confirm defendant identity when multiple exist.

---

## 2. What the toolkit does

This repo contains a **hybrid automation** that removes ~85–90% of manual toil:

- **Court Data Extraction** — fetches case basics into a spreadsheet.  
- **GPT‑Assisted Research** — semi‑automated, finds crime dates, sentences, and sources.  
- **Human Oversight** — compute ages, assign bands, resolve conflicts, mark confidence.

⏱ **Impact:** months of manual research → ~40–60 hours for ~1,300 cases.

---

## 3. Who should use this

- Investigative journalists and data editors  
- Public‑interest lawyers and policy advocates  
- Researchers who need a reproducible audit trail

---

## 4. What data we collect

- **Defendant**: name, birth year, race (if available)  
- **Court**: case number, filing date, location, docket URL  
- **Offense**: crime date, crime type  
- **Outcome**: sentence, plea vs. trial, juvenile vs. adult court  
- **Derived**: age at crime, age band  
- **Provenance**: URLs, notes, confidence

---

## 5. Ethics, transparency, and auditability

- Every fact is source‑linked.  
- Verification order: appellate decisions → trial/official docs → DA/LE releases → major newspapers → local outlets → general news.  
- Leave fields blank if not verifiable; mark confidence accordingly.

---

## 6. Requirements

**OS:** Windows, macOS, or Linux  
**Python:** 3.9+ recommended  
**Storage:** ~500 MB software + ~50 MB data  
**Network:** Stable broadband  
**Time:** ~2–3 hours for setup  
**Accounts:** ChatGPT (for the extractor GPT)

### Packages
```bash
pip install playwright pandas openpyxl requests
playwright install chromium
```

---

## 7. Installation

```bash
# 1) Create & activate a virtual environment
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt
playwright install chromium
```

---

## 8. Expected success rates

- Court data extraction: 95–98% rows populated  
- GPT‑assisted research: 75–90% (case‑coverage dependent)  
- Fully complete records: 70–85%  
- Manual follow‑up required: 15–30%

---

## 9. Troubleshooting

- **Session test failed** → Refresh `JSESSIONID`.  
- **GPT finds nothing** → Try nickname variations, check DateFiled.  
- **Rate limiting** → Pause 10–15 minutes. Run in batches.  
- **Excel won’t open** → Use auto‑generated backups in `output/backups/`.

---

## 10. Time & cost expectations

- Setup: 2–3 hours  
- Step 1: 4–8 hours for ~1,300 cases (unattended)  
- Step 2: 8–15 hours with human input  
- Manual QC: 10–20 hours  
- ChatGPT usage: Plus may help for uninterrupted runs

---

## 11. Roadmap — Ways to evolve this project

**Automation & Data Quality**  
- Automate Step 2 with targeted search APIs  
- Add name‑disambiguation heuristics  
- Integrate appellate opinion scraping  
- Retry/backoff & proxy rotation  
- Deduplication and near‑duplicate detection  

**Engineering & Ops**  
- Package as a CLI (`pipx`), add Dockerfile  
- CI for lint/tests, structured logs & metrics  
- Output CSV/Parquet to DB  
- Orchestrate with Prefect/Airflow  

**Research Extensions**  
- Generalize to other counties/states via config  
- Add bias‑analysis notebooks with charts  
- Publish interactive dashboard (Streamlit)  
- Add anonymization/redaction for public sharing

---

## 12. FAQ

- **Is this legal advice?** No.  
- **Does this scrape paywalled content?** No.  
- **Why not fully automate Step 2?** Human judgment is required.  
- **Can I use another LLM?** Yes, prompts are model‑agnostic.

---

## 13. License & disclaimer

Released under the **MIT License**. Use at your own risk. Respect website terms of service and privacy laws.  
This repository is for research and journalism support, **not legal advice**.

---

## 14. Acknowledgments

- **Pillars of the Community** — for getting this project started and defining requirements.  
- Thanks to volunteers and contributors for building a transparent, reproducible workflow.
