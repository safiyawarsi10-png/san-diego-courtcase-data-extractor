# Step 1 — Required Python Packages

This document lists the Python dependencies needed for **Step 1: Court Data Extraction** to work.  
These packages should be installed in your virtual environment before running the extractor script.

---

## Package List

```
et_xmlfile==2.0.0
greenlet==3.2.3
numpy==2.3.2
openpyxl==3.1.5
pandas==2.3.1
playwright==1.54.0
pyee==13.0.0
python-dateutil==2.9.0.post0
pytz==2025.2
six==1.17.0
typing_extensions==4.14.1
tzdata==2025.2
```

---

## Why these packages are needed

- **et_xmlfile** — a low-level dependency used by *openpyxl* to write Excel files in XML format.  
- **greenlet** — provides lightweight coroutines; used internally by async frameworks that *playwright* depends on.  
- **numpy** — core numerical computing library, required by *pandas* for efficient array handling.  
- **openpyxl** — enables reading/writing of Excel files (.xlsx), which Step 1 outputs.  
- **pandas** — data analysis library used to manipulate case data and store it in spreadsheets.  
- **playwright** — browser automation library used to fetch case details from the San Diego Superior Court portal.  
- **pyee** — event-emitter library required by *playwright* for async handling of browser events.  
- **python-dateutil** — provides powerful date/time parsing and arithmetic; used in age/date calculations.  
- **pytz** — historical timezone library, required by *pandas* for datetime localization.  
- **six** — Python 2/3 compatibility utilities; some libraries still rely on it.  
- **typing_extensions** — backports of newer typing features for Python, ensuring compatibility.  
- **tzdata** — IANA timezone database, needed by *pandas* and *dateutil* to handle timezones consistently.

---

## Installation

Run the following inside your virtual environment:

```bash
pip install -r requirements.txt
```

Or, if installing manually:

```bash
pip install et_xmlfile==2.0.0 greenlet==3.2.3 numpy==2.3.2 openpyxl==3.1.5 pandas==2.3.1 playwright==1.54.0 pyee==13.0.0 python-dateutil==2.9.0.post0 pytz==2025.2 six==1.17.0 typing_extensions==4.14.1 tzdata==2025.2
```

---

## Notes

- These exact versions are pinned for reproducibility.  
- After installing *playwright*, also run:

```bash
playwright install chromium
```

to ensure the browser engine is available.  
