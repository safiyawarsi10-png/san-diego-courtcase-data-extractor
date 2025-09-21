# Step 1 — Court Data Extraction

This folder contains scripts for extracting San Diego Superior Court case data into a spreadsheet.

---

## 8. Getting your court session ID (JSESSIONID)

The San Diego Superior Court public portal issues a **JSESSIONID** cookie when you start a search.  
We inject that cookie so automated requests are treated like a live session.

Sessions expire; that’s why you copy a fresh ID when needed.

### How to obtain:
1. Open the court’s public portal in your browser.  
2. Perform any case search.  
3. Open Developer Tools → Application → Cookies.  
4. Copy the `JSESSIONID` value.  
5. Use this as the first argument when running the script.

---

## 8.1 San Diego–specific behavior & adapting to other counties

This repository’s Step 1 script and instructions are tuned to the **San Diego Superior Court** public index.  

### What’s special about San Diego
- **Session handling via `JSESSIONID`.**  
- **Multiple locations in one portal.** Script cycles through North County, San Diego, East, South.  
- **Stable deep links.** We store the direct docket URL for audit.  
- **Polite throttling.** Built-in delays/retries prevent blocking.  
- **Case-number search works well.** Avoids name collisions.

### Adapting to other counties
- Identify the session model (cookie/token name).  
- Confirm search mode (case number vs. name).  
- Check for CAPTCHAs / access walls (may require manual Step 1).  
- Note HTML layout & selectors; update script accordingly.  
- Rate-limit expectations: 1–2.5s between actions, with jitter.  
- Deep links vs. postbacks: if no stable link, save PDF/HTML snapshot.  
- Case-number formats: update regex to match county format.  
- Location mapping: capture division/district info.

### Minimal-change port using a config file
Define `county_config.yaml` with keys for `base_url`, `session_cookie_name`, `locations`, `selectors`, etc.

If a portal blocks automation, fall back to **manual Step 1**.

---

## 9. Project layout (Step 1 perspective)

```
project/
├─ step1_fetch_cases_playwright.py
├─ your_cases.txt                  # one case number per line
├─ output/
│  ├─ san_diego_cases_dob_extracted.xlsx
│  └─ backups/ *_BACKUP_HHMMSS.xlsx
```

---

## 10. Step 1 — Extract court data

### 10.1 Prepare your case list
Create a plain-text file with **one case number per line**:

```
CN367913
CN367895
CD270095
CE366120
CS290571
```

### 10.2 Run the extractor
```bash
python step1_fetch_cases_playwright.py <JSESSIONID> <path/to/cases.txt>
```

**Example:**
```bash
python step1_fetch_cases_playwright.py A1B2C3D4E5F6 san_diego_cases.txt
```

### 10.3 What Step 1 writes into the spreadsheet
For each case, Step 1 creates a row with:

- **CaseNumber** (from your TXT)  
- **DataStatus** (success/failed/partial)  
- **DefendantName**  
- **DOB** (birth year; YYYY)  
- **DateFiled**  
- **AgeAtCrime** (blank for now — filled in Step 2)  
- **AgeAtFiling** (optional)  
- **DefendantRole** (primary/co-defendant if available)  
- **TotalDefendants**  
- **DefendantIndex**  
- **CaseLocation** (North County / San Diego / East / South)  
- **Source_DocketURL** (direct link to court record)

This gives you a **working spreadsheet** to move on to Step 2 (crime dates and sentences).
