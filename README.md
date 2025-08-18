San Diego Criminal Cases -- Data Collection & Research
=====================================================

An automation toolkit for building an auditable dataset of San Diego criminal court cases

Audience: Investigative journalists, public‑interest lawyers, researchers, and technically‑minded volunteers. Comfortable running Python scripts; no prior court‑data scraping experience required.

* * * * *

Table of Contents
-----------------

-   0\. Core goal in plain English

-   1\. Overview --- Why this exists

-   2\. What the toolkit does

-   3\. Who should use this

-   4\. What data we collect

-   5\. Ethics, transparency, and auditability

-   6\. Requirements

-   7\. Installation

-   8\. Getting your court session ID (JSESSIONID)

-   8.1 San Diego--specific behavior & adapting to other counties

-   9\. Project layout

-   10\. Step 1 --- Extract court data

-   11\. Step 2 --- GPT‑assisted research for crime dates & sentences

-   12\. Spreadsheet formulas (Age at Crime & Age Band)

-   13\. Data model (columns & meanings)

-   14\. Quality control & manual review

-   15\. Expected success rates

-   16\. Troubleshooting

-   17\. Time & cost expectations

-   18\. Roadmap --- Ways to evolve this project

-   19\. FAQ

-   20\. License & disclaimer

-   21\. Acknowledgments

* * * * *

0\. Core goal in plain English
------------------------------

Purpose\
This document outlines the research process and tools used by our team and volunteers to build a transparent dataset for bias analysis. We're building a structured, auditable dataset of San Diego criminal court cases so we can ask a set of clear, testable questions about fairness and consistency in charging and sentencing.

Concretely, we're:

-   Assembling core facts (defendant name, birth‑year, filing date) directly from the Superior Court's public Case Detail pages (via the court index link).

-   Pulling in crime dates and sentencing outcomes from reputable local news or appellate opinions using a custom GPT tool.

-   Computing exact or best‑available age at the time of the crime, then bucketing into:

-   Juvenile (< 18)

-   Emerging Adult (18--26)

-   Adult (> 26)

-   Flagging any gaps or estimates in our data (e.g., DOB≈1993 inferred from press release) so nothing is hidden.

What questions can this dataset answer? (examples, not exhaustive)

-   Age bands: Are juveniles or emerging adults more/less likely to receive harsher sentences than older adults for comparable charges?

-   Race/ethnicity: Holding age band and §190.2 status constant, do sentence outcomes vary by race when race is explicitly stated in reliable sources?

-   Special circumstances (§190.2): How often are special‑circumstance allegations charged and applied (the SC_* field), and how much do they explain sentence differences across groups?

-   Charge severity: Do outcomes differ by charges convicted (e.g., first‑ vs. second‑degree), and are those differences uniform across age bands and races?

-   Plea vs. trial: Are plea outcomes systematically different from trial outcomes across groups? (e.g., plea discounts by age band/race)

-   Geography: Do outcomes vary across court locations (North County / San Diego / East / South)?

-   DA tenures/time trends: Are there shifts over time or between DA eras once you control for charge type and §190.2 status?

-   Co‑defendant parity: Within the same case, do similarly situated co‑defendants receive different sentences (age/race held constant)?

You can extend the sheet with more columns (e.g., enhancements, counts, statute cites) to answer additional questions as needed.

Why this matters\
Once every record has a verified crime date, a birth‑year (or exact DOB), the resulting sentence length/type, and source URLs, you can:

-   Pivot and filter across age bands, race (when known), charges, §190.2 status, plea/trial, location, and DA era; and

-   Run straightforward statistics (rate ratios, chi‑square, logistic regression, etc.) to test for differences that are material and reproducible.

Our pipeline, at a glance\
Court lookup → GPT‑assisted news/legal research → derived fields (ages, bands, §190.2 status) → QC flags.\
This transparent, repeatable process lets anyone audit every cell, reproduce our steps, and trust whatever analysis we publish.

1\. Overview --- Why this exists
------------------------------

Overview --- Why this exists

### Background (plain‑English)

This toolkit supports research into potential racial bias in criminal sentencing, specifically examining how age intersects with race in criminal case outcomes.

-   Research Question: Does sentencing vary by race for defendants who were juveniles (<18) or emerging adults (18--26) when they committed serious crimes in San Diego?

-   Data Scope: Approximately 1,300 case numbers covering San Diego criminal cases prosecuted during a District Attorney's tenure (or any comparable set visible on the court website).

-   Key variables to collect:

-   Defendant demographics: name; birth year; race (when available in reliable sources)

-   Crime details: exact date the crime was committed

-   Case outcomes: specific sentence imposed (e.g., years‑to‑life, LWOP, probation)

-   Age analysis: defendant's age when the crime occurred and resulting age band

-   Court information: filing dates; locations; direct docket link (court index URL)

### 1.1 The real‑world problem

Public criminal court records in California are fragmented. A case's basic facts are often split between:

-   a court index page (names, filing date, location),

-   one or more opinions or minute orders (crime facts, enhancements, outcomes), and

-   news reports that can be accurate, incomplete, or occasionally wrong.

For fairness work (e.g., Racial Justice Act inquiries), you need the same fields for every case, collected in a consistent way and backed by links---otherwise any disparity claim is easy to challenge as anecdotal or cherry‑picked.

### 1.2 Our design goals

-   Auditability: Every row has provable provenance (URLs and notes). If someone disagrees, they can click the link and see what you saw.

-   Reproducibility: Given the same input case list, a second team should produce the same spreadsheet (within minor judgment calls), because the steps are explicit and simple.

-   Accessibility: Uses Excel and copy‑paste, not databases or custom GUIs. Non‑coders can follow it.

-   Human‑in‑the‑loop: We deliberately avoid full automation where names collide or sources conflict. People make the final call, and that call is documented.

### 1.3 Why age and §190.2 matter here

-   Age at crime lets you label Juvenile (<18), Emerging Adult (18--26), and Adult (>26). Many policy debates---and some legal standards---treat emerging adults differently because of developing neuroscience and sentencing norms.

-   Special circumstances (Penal Code §190.2) affect punishment exposure. Tracking whether a special circumstance was alleged and/or applied (via the SC_* code) helps separate harsher sentences that stem from statutory factors from those that might indicate unequal treatment.

### 1.4 How the workflow keeps you grounded in facts

-   Every Step 2 session starts from the docket: you copy the actual Case Title, Case Number, Location, Type, Date Filed from the court page linked in your spreadsheet.

-   You can attach PDFs (opinions, minute orders) and paste article links so the GPT reads them before returning JSON.

-   The output JSON includes a sources list. You keep or discard entries; the sheet stores the final URL(s) you accept.

### 1.5 What this unlocks for a reviewer or court

-   A single file to spot patterns (e.g., sentence distributions by AgeBand; presence/absence of §190.2).

-   A fast way to retrace any number back to a document.

-   A platform you can extend later (additional columns, county configs, or formal statistical notebooks).

### 1.6 Guardrails against common pitfalls

-   Don't confuse crime date with filing or sentencing dates.

-   Prefer opinions/official records over media; if media is all you have, mark confidence accordingly.

-   When multiple defendants exist, confirm you're attaching facts to the correct person using the docket details (number, location, filed date).

Pipeline in seven words: Court index → Evidence → JSON → Spreadsheet → Formulas → Filters → Analysis.

2\. What the toolkit does
-------------------------

This repo contains a hybrid automation that removes ~85--90% of manual toil:

### 2.1 Court Data Extraction --- step1_fetch_cases_playwright.py

-   Visits the San Diego Superior Court public portal across all locations

-   Manages sessions/authentication and common site errors

-   Reads your case numbers from a TXT file and writes an Excel spreadsheet

-   Extracts: defendant name, birth year, filing date, location, and docket URL

-   Handles multi‑defendant cases (separate rows)

-   Resumable: saves progress and creates backup files

### 2.2 GPT‑Assisted Research (semi‑automated)

-   A purpose‑built GPT workflow finds crime dates, sentences, and sources

-   Prioritizes appellate opinions and official records; falls back to reputable news

-   Returns structured JSON you can map into the spreadsheet

### 2.3 Human Oversight (critical)

-   Compute age at crime and assign age band

-   Resolve conflicts and mark confidence

-   Investigate rows where no reliable sources are found

⏱ Impact: months of manual research → ~40--60 hours total for ~1,300 cases.

* * * * *

3\. Who should use this
-----------------------

-   Investigative journalists and data editors

-   Public‑interest lawyers and policy advocates

-   Researchers who need a reproducible audit trail for peer review

* * * * *

4\. What data we collect
------------------------

-   Defendant: full name, birth year (YYYY), race (if explicitly stated in reliable sources)

-   Court: case number, filing date, location, docket URL

-   Offense: crime date (not trial/sentencing date), crime type

-   Outcome: sentence; plea vs. trial; juvenile vs. adult court

-   Derived: age at crime; age at filing; age band (Juvenile <18, Emerging Adult 18--26, Adult >26)

-   Provenance: article/opinion URLs; notes and confidence

* * * * *

5\. Ethics, transparency, and auditability
------------------------------------------

-   Every fact is source‑linked; ambiguous fields are annotated (e.g., "DOB≈1993 from press release").

-   Verification order (highest→lowest): appellate decisions → trial/official documents → DA/LE releases → major newspapers → local outlets → general news.

-   If details cannot be verified, leave fields blank and mark confidence accordingly.

* * * * *

6\. Requirements
----------------

OS: Windows, macOS, or Linux\
Python: 3.9+ recommended\
Storage: ~500 MB software + ~50 MB data\
Network: Stable broadband\
Time: ~2--3 hours for setup; Step 1 can run unattended\
Accounts: ChatGPT (for the custom extractor GPT)

### 6.1 Packages

-   pip install playwright pandas openpyxl requests

playwright install chromium

* * * * *

7\. Installation
----------------

-   # 1) Create & activate a virtual environment (recommended)

-   python -m venv .venv

-   # Windows

-   .\.venv\Scripts\activate

-   # macOS/Linux

-   source .venv/bin/activate

-   # 2) Install dependencies

-   pip install -r requirements.txt  # if present

-   # or install explicitly

-   pip install playwright pandas openpyxl requests

playwright install chromium

* * * * *

$1

### 8.1 San Diego--specific behavior & adapting to other counties

This repository's Step 1 script and instructions are tuned to the San Diego Superior Court public index. Here's what's special about San Diego, why we do things a certain way, and how you'd adapt the process to Alameda, Los Angeles, or another county.

#### What's special about San Diego (why we do it this way)

-   Session handling via JSESSIONID. The portal issues a JSESSIONID cookie when you start a search. We inject that cookie so automated requests are treated like a live session. Sessions expire; that's why we copy a fresh ID when needed.

-   Multiple locations in one portal. San Diego exposes North County / San Diego / East / South in a single interface. Our script cycles locations or reads the location field so rows indicate where the case lives.

-   Stable deep links. The index provides a direct docket URL that remains valid during a session window; we store it as Source_DocketURL for auditing.

-   Polite throttling. The site tolerates gentle automation if you include delays between requests and explicit waits (wait for specific elements, not just page load). We build in small sleeps and retries to avoid 429s/blocks.

-   Case‑number search works well. For San Diego, case‑number queries are sufficient; we avoid name‑only searches to prevent collisions.

#### Adapting to another county (Alameda, Los Angeles, others)

Different counties run different public portals. Before porting, open the county site and run a 5‑minute reconnaissance:

1.  Identify the session model. Note the cookie/token name (may not be JSESSIONID). Some sites rotate tokens per request or embed hidden fields. Plan to capture and reuse whatever the site sets after a test search.

2.  Confirm search mode. If case‑number search exists, great. If not, you may need defendant‑name search plus extra disambiguation (DOB, filing date, location) and more human checks.

3.  Check for CAPTCHAs / access walls. If a county uses CAPTCHAs, mandatory user agreements, or paywalls, full automation stops. Use Step 1 manually for that county, then proceed with Step 2 and the spreadsheet.

4.  Note layout & selectors. Portals vary in HTML structure and labels. You'll need to update the script's selectors (the strings that tell it what to click/read).

5.  Rate‑limit expectations. Start with 1--2.5 seconds between actions plus jitter; back off on errors. Keep concurrency = 1.

6.  Deep links vs. postbacks. Some sites don't provide stable direct URLs to a case detail. If a stable URL isn't possible, store a search URL + case ID and consider saving a PDF/HTML snapshot of the page into your output/ folder for audit.

7.  Case‑number formats. Update the regex that validates input case numbers (prefixes, dashes, year digits differ by county). Store the raw string in CaseNumber so you can refine later.

8.  Location mapping. If the county uses divisions (e.g., René C. Davidson / East County, or LA districts), capture that as CaseLocation so analyses remain comparable.

#### Minimal‑change port using a config file

You can keep one script and swap a config per county. Create a county_config.yaml like:

-   county_name: "San Diego"

-   base_url: "https://courtindex.sdcourt.ca.gov/CISPublic/"

-   session_cookie_name: "JSESSIONID"

-   search_mode: "case_number"   # or "name"

-   locations:

-   - "North County"

-   - "San Diego"

-   - "East"

-   - "South"

-   rate_limit_ms: 1800             # base delay between actions

-   rate_jitter_ms: 400             # +/- random jitter

-   selectors:

-   search_input: "input[name='caseNumber']"

-   submit_button: "button[type='submit']"

-   result_row: "table.results tr"

-   case_detail_link: "a.case-detail"

-   fields:

-   defendant_name: "#defendantName"

-   dob_year: "#dob"

-   date_filed: "#dateFiled"

  case_location: "#location"

For Alameda/LA, copy that file and update base_url, session_cookie_name, selectors, and locations. If the site uses tokenized postbacks or doesn't allow deep links, add a flag like store_snapshot: true and have the script save a PDF/HTML of the details page for the audit trail.

#### When a portal blocks automation

-   Respect terms of use and robots/anti‑bot measures.

-   Fall back to manual Step 1 (open the page from your case list, copy the key fields into the spreadsheet), then continue with Step 2 using the GPT and attached PDFs/articles.

Bottom line: San Diego's portal is unusually workable for case‑number lookups with a session cookie and polite delays. Other counties can work too, but you'll likely tweak session handling, selectors, rate limits, and how you store the audit link.

$2

9\. Project layout
------------------

-   project/

-   ├─ step1_fetch_cases_playwright.py

-   ├─ your_cases.txt                  # one case number per line (e.g., CN367913)

-   ├─ output/

-   │  ├─ san_diego_cases_dob_extracted.xlsx

-   │  └─ backups/ *_BACKUP_HHMMSS.xlsx

└─ README.md

* * * * *

10\. Step 1 --- Extract court data
--------------------------------

### 10.1 Prepare your case list

Create a plain‑text file with one case number per line:

-   CN367913

-   CN367895

-   CD270095

-   CE366120

CS290571

### 10.2 Run the extractor

python step1_fetch_cases_playwright.py <JSESSIONID> <path/to/cases.txt>

Example

python step1_fetch_cases_playwright.py A1B2C3D4E5F6 san_diego_cases.txt

### 10.3 What Step 1 writes into the spreadsheet

For each case, Step 1 creates a row and fills the columns it can read from the court index site:

-   CaseNumber (from your TXT)

-   DataStatus (e.g., success/failed/partial --- for monitoring)

-   DefendantName

-   DOB (birth year; YYYY)

-   DateFiled (court filing date)

-   AgeAtCrime (left blank for now --- filled after Step 2)

-   AgeAtFiling (optional, see formulas below)

-   DefendantRole (e.g., primary/co‑defendant when available)

-   TotalDefendants (if the portal shows multiple defendants)

-   DefendantIndex (row/position among co‑defendants)

-   CaseLocation (North County / San Diego / East / South)

-   Source_DocketURL (direct link to the case on the court site)

These columns give you a working spreadsheet so you can immediately proceed to Step 2 to retrieve crime dates and sentences.

* * * * *

11\. Step 2 --- GPT‑assisted research for crime dates, sentences & special circumstances
--------------------------------------------------------------------------------------

This semi‑automated phase uses a specialized GPT workflow and keeps you in control of verification.

Specialized GPT (San Diego): https://chatgpt.com/g/g-68992f4b52a4819197a6166755b35d4b-criminal-case-extractor-san-diego

Preferred workflow: For each spreadsheet row, start from the Source_DocketURL (the court index link). Open that page, copy the key fields exactly as displayed, and paste them into the GPT. You may also attach supporting PDFs (court filings/opinions) and news articles---the GPT will read them before producing the JSON.

### 11.1 What you'll copy from the court page (strongly recommended)

From the court index page for the case, copy the visible text for: Case Title, Case Number, Case Location, Case Type, and Date Filed.

Concrete example (taken from your spreadsheet/court page):

-   Case Title:   DEFENDANT KEVIN PHAN

-   Case Number:  SCN367895

-   Case Location: North County

-   Case Type:    Criminal

Date Filed:   12/29/2016

### 11.2 Attaching evidence (PDFs & articles)

-   Court documents: Drag‑and‑drop PDFs (e.g., appellate opinions, minute orders) into the GPT window before you click Submit.

-   Articles: Paste links to relevant news stories. If you saved them as PDFs, you can upload those as well.

-   The GPT will consider everything you attach and include helpful links under sources in its JSON.

### 11.3 Example JSON returned by the specialized GPT

-   {

-   "defendant_name": "Kevin Phan",

-   "crime_date": "2016-12-24",

-   "defendant_age_at_crime": "22",

-   "sentence": "25 years to life plus 3 years (total 28 years)",

-   "charges_convicted": "First-degree murder",

-   "crime_type": "Homicide (shooting)",

-   "defendant_race": "",

-   "juvenile_adult_court": "Adult",

-   "plea_or_trial": "Guilty plea",

-   "confidence_level": "high",

-   "case_summary": "Kevin Phan shot and killed a 22-year-old Fallbrook man on Christmas Eve 2016 in Vista. He later pleaded guilty to first-degree murder and, in March 2018, was sentenced to 25 years to life plus 3 years (28 years total). There is no indication that any Penal Code §190.2 special-circumstance allegation was charged or found true.",

-   "special_circumstance_overall_status": "SC_N_NOAPPL",

-   "sources": [

-   "https://www.nbcsandiego.com/news/local/vista-man-sentenced-to-28-years-in-prison-in-christmas-eve-2016-killing/163575/",

-   "https://timesofsandiego.com/crime/2016/12/27/vista-man-22-suspected-fatal-christmas-eve-shooting/",

-   "https://codes.findlaw.com/ca/penal-code/pen-sect-190-2/"

-   ]

}

About special circumstances: The field special_circumstance_overall_status follows California Penal Code §190.2 categories and returns one of:

-   SC_N_NOAPPL --- no special circumstance, not applied

-   SC_Y_NOAPPL --- yes special circumstance, not applied

-   SC_Y_APPL --- yes special circumstance, yes applied

-   SC_N_APPL --- no special circumstance, applied (edge case/anomaly; double‑check sources)

Note: §190.2 special circumstances apply to murder cases. For non‑homicide criminal cases, this field will typically be SC_N_NOAPPL or left blank.

### 11.4 Mapping JSON → Spreadsheet columns

Paste values from the JSON into these columns (add the column to your sheet if it doesn't exist yet):

-   defendant_name → DefendantName (use to fix capitalization if needed)

-   crime_date → CrimeDate

-   defendant_age_at_crime → AgeAtCrime (optional; you may also rely on the formula)

-   sentence → Sentence

-   charges_convicted → ChargesConvicted

-   crime_type → CrimeType

-   defendant_race → DefendantRace (only if clearly stated in reliable sources)

-   juvenile_adult_court → JuvenileOrAdultCourt

-   plea_or_trial → PleaOrTrial

-   confidence_level → Confidence

-   case_summary → CaseSummary (1--3 sentences)

-   special_circumstance_overall_status → SpecialCircumstance

-   sources[0..] → Source_ArticleURL (primary) and Notes (list any additional links)

### 11.5 Quality hints for Step 2

-   Prefer appellate opinions and official documents; use major outlets next.

-   Be careful with crime date vs. filing/sentencing dates---they are often different.

-   When names collide, cross‑check with filing date and location from the docket.

### 11.6 If GPT returns nothing or is uncertain

-   Remove middle names/suffixes; try nickname variants.

-   Re‑attach any PDFs and include one or two reputable article links.

-   Add a note in Notes (e.g., NO INFO) and return to the row later.

12\. Spreadsheet formulas (Age at Crime & Age Band)
---------------------------------------------------

Below are ready‑to‑paste Excel formulas that compute age and assign age bands. Adjust column letters if your sheet layout differs.

Assumptions for the examples below:

-   DOB (birth year, YYYY) is in column E

-   CrimeDate (a date) is in column G

-   AgeAtCrime is column H

-   AgeBand is column I

If your sheet uses different columns, update the letters in the formulas. If you later store a full date of birth (not just a year), see the "More precise age" variant in 12.1‑B.

### 12.1 Age at Crime

Paste into H12 (then fill down the column):

=IF(OR(ISBLANK(E12),ISBLANK(G12)),"", YEAR(G12)-E12)

What this does (in plain English):

-   If either the birth year (E12) or the crime date (G12) is missing, it leaves the cell blank so you don't get misleading numbers.

-   Otherwise, it takes the year of the crime date and subtracts the birth year --- giving a good approximation of the defendant's age at the time of the crime.

Why we use it:

-   In many cases we only know the birth year from the court index; month/day are unknown. This simple subtraction is transparent and consistent across all rows, so your age bands (next step) are reproducible.

Edge cases to know:

-   If the crime happened before the person's birthday that year, the exact age could be one year lower than this approximation. That's acceptable for banding purposes because we're grouping into broad categories (Juvenile / 18--26 / >26). If you later obtain full DOB, use the precise variant below.

#### 12.1‑B (optional) More precise age when you have full DOB

If you later store the full DOB as a date (e.g., 1994-05-12) in E12, use this instead:

=IF(OR(ISBLANK(E12),ISBLANK(G12)),"", DATEDIF(E12, G12, "Y"))

This counts completed years between DOB and CrimeDate (correct around birthdays). Only use this if E contains actual dates, not just a year like 1994.

How to sanity‑check:

-   Type 1994 in E12, 1/1/2016 in G12 → H12 should show 22 (2016-1994).

-   Delete G12 → H12 should go blank.

### 12.2 Age Band

Paste into I12 (then fill down the column):

=IF(H12="","",IF(H12<18,"Juvenile (< 18)",IF(H12<=26,"Emerging Adult (18--26)","Adult (> 26)")))

What this does:

-   If AgeAtCrime is blank, it stays blank.

-   Otherwise, it assigns one of three labels:

-   Juvenile (< 18)

-   Emerging Adult (18--26) (inclusive of 18 and 26)

-   Adult (> 26)

Why we need it:

-   Most disparity questions are analyzed by groups, not raw ages. AgeBand gives you a standard, reproducible grouping that matches how you'll discuss results with lawyers/journalists and in RJA‑focused work.

Customize the thresholds (if your study differs):

-   If your "emerging adult" study window should end at 24 instead of 26, change <=26 to <=24.

-   If you later use the precise age formula in 12.1‑B, you don't need to change this banding formula; it still reads the number in H.

### 12.3 (optional) Age at Filing

If you also want to compare the age at filing (sometimes relevant in policy discussions), add a column (e.g., J) and use:

=IF(OR(ISBLANK(E12),ISBLANK(F12)),"", YEAR(F12)-E12)

Where F contains DateFiled (a date). Use the DATEDIF variant if you later store full DOB.

### 12.4 Common mistakes & quick fixes

-   DOB stored as text ("1994 " with spaces) → Excel won't treat it as a number. Fix by trimming spaces or re‑typing just 1994.

-   CrimeDate pasted as text (e.g., "2016-12-24") → Format the cell as Date so YEAR(G12) works.

-   Didn't fill down → Select the formula cell's lower‑right fill handle and drag down to cover all rows.

-   Wrong columns → If your sheet uses different columns, substitute the letters consistently (e.g., if CrimeDate is H, change YEAR(G12) to YEAR(H12)).

* * * * *

13\. Data model (columns & meanings)
------------------------------------

|

Column

 |

Description

 |

Source

 |
|

CaseNumber

 |

Court case identifier

 |

Input file

 |
|

DataStatus

 |

Status flag for Step 1 extraction

 |

Step 1

 |
|

DefendantName

 |

Full name from court records (updated for casing if needed)

 |

Step 1 / Step 2

 |
|

DOB

 |

Birth year (YYYY)

 |

Step 1

 |
|

DateFiled

 |

Filing date

 |

Step 1

 |
|

CaseLocation

 |

North County / San Diego / East / South

 |

Step 1

 |
|

CrimeDate

 |

Date the offense occurred

 |

Step 2

 |
|

AgeAtCrime

 |

Calculated numeric age (formula preferred; JSON value optional)

 |

Formula / Step 2

 |
|

AgeAtFiling

 |

Age on the filing date (optional)

 |

Formula

 |
|

AgeBand

 |

Juvenile / Emerging Adult / Adult

 |

Formula

 |
|

Sentence

 |

Specific sentence imposed

 |

Step 2

 |
|

ChargesConvicted

 |

e.g., First‑degree murder

 |

Step 2

 |
|

CrimeType

 |

e.g., Robbery; Assault; Homicide (shooting)

 |

Step 2

 |
|

JuvenileOrAdultCourt

 |

Whether the case was in juvenile or adult court

 |

Step 2

 |
|

PleaOrTrial

 |

Plea vs. trial outcome

 |

Step 2

 |
|

SpecialCircumstance

 |

Overall status code from §190.2 (SC_*)

 |

Step 2

 |
|

Confidence

 |

GPT's confidence label for the row

 |

Step 2

 |
|

CaseSummary

 |

1--3 sentence summary of the case

 |

Step 2

 |
|

DefendantRace

 |

Only if explicitly stated in reliable sources

 |

Step 2

 |
|

DAEra

 |

A DA tenure label if you're studying a period

 |

Step 1/Constant

 |
|

Source_DocketURL

 |

Court record link (court index page)

 |

Step 1

 |
|

Source_ArticleURL

 |

Primary news/opinion/official link

 |

Step 2

 |
|

Notes

 |

QC flags, assumptions, and any extra source links

 |

All steps

 |

* * * * *

14\. Quality control & manual review
------------------------------------

-   Distinguish crime date from filing/sentencing dates

-   Add confidence notes (e.g., low = one minor source; high = appellate opinion + docket)

-   For no‑info rows, leave fields blank or write NO INFO in Notes and revisit

-   Double‑check co‑defendant attributions and name variants

* * * * *

15\. Expected success rates
---------------------------

-   Court data extraction: 95--98% rows populated

-   GPT‑assisted research: 75--90% (case‑coverage dependent)

-   Fully complete records: 70--85%

-   Manual follow‑up required: 15--30%

* * * * *

16\. Troubleshooting
--------------------

Session test failed

-   Refresh JSESSIONID (start a new search on the portal) and rerun.

GPT finds nothing

-   Remove middle names/suffixes; try nickname variations; verify DateFiled.

Rate limiting / site blocks

-   Pause 10--15 minutes. Run batches of 50--100 cases.

Excel won't open / partial writes

-   Use the auto‑generated backups in output/backups/.

* * * * *

17\. Time & cost expectations
-----------------------------

-   Setup: 2--3 hours

-   Step 1: 4--8 hours for ~1,300 cases (can run unattended)

-   Step 2: 8--15 hours with human input

-   Manual QC: 10--20 hours (data‑quality dependent)

-   ChatGPT usage: Free tier is limited; Plus may help for uninterrupted runs.

* * * * *

18\. Roadmap --- Ways to evolve this project
------------------------------------------

Automation & Data Quality

-   Automate Step 2 with targeted search APIs; add source‑ranking by reliability

-   Add name‑disambiguation and co‑defendant resolution heuristics

-   Integrate appellate opinion scraping with parsers for fact sections

-   Implement retry/backoff & proxy rotation for portal stability

-   Add deduplication and near‑duplicate article detection

Engineering & Ops

-   Package as a CLI (pipx), add pyproject.toml & entry points

-   Provide a Dockerfile for reproducible runs

-   CI for lint/tests; structured logs & metrics

-   Switch spreadsheet output to CSV/Parquet and ship to a lightweight DB

-   Orchestrate with Prefect/Airflow; add caching

Research Extensions

-   Generalize to other counties/states via config

-   Add bias‑analysis notebooks (chi‑square, logistic regression) with example charts

-   Publish an interactive dashboard (Streamlit) for filtering and exports

-   Add anonymization/redaction modes for public sharing

* * * * *

19\. FAQ
--------

Is this legal advice? No. This is a research utility and does not replace counsel.\
Does this scrape paywalled content? No. Use only public pages or sources you have rights to access.\
Why not fully automate Step 2? Jurisdictional variation, paywalls, and name collisions make human judgment valuable.\
Can I use another LLM? Yes. The prompt design is model‑agnostic; accuracy depends on source selection and verification.

* * * * *

20\. License & disclaimer
-------------------------

Released under the MIT License. Use at your own risk. Respect website terms of service and privacy laws. This repository is for research and journalism support, not legal advice.

* * * * *

21\. Acknowledgments
--------------------

-   Pillars of the Community --- for getting this project started and helping define what was required to initiate the work.

-   Thanks to the volunteers and contributors who helped build a transparent, reproducible workflow for public‑interest analysis.
