# Step 2 — GPT-Assisted Research

This folder documents the semi-automated process of augmenting the Step 1 spreadsheet
with **crime dates, sentences, and other fields** by using a GPT-based extractor.

---

## 1. GPT-assisted research for crime dates, sentences & special circumstances

This semi-automated phase uses a specialized GPT workflow and keeps **you** in control of verification.

**Preferred workflow:**
1. From your Step 1 spreadsheet, open the **Source_DocketURL** (the court index link). For example: https://courtindex.sdcourt.ca.gov/CISPublic/casedetailr?casenum=SCN367895&casesite=NC&applcode=R 
2. Copy the visible case fields as shown in Figure 1(Case Title, Case Number, Case Location, Case Type, Date Filed).

![View Case Detail](https://github.com/user-attachments/assets/a8f890b8-88d6-45e4-a787-bf73d72ae834)
Figure 1

4. Provide those details to the GPT assistant along with supporting PDFs or articles.
   GPT assistant: https://chatgpt.com/g/g-68992f4b52a4819197a6166755b35d4b-criminal-case-extractor-san-diego
5. Paste the JSON returned into your spreadsheet.

### What you’ll copy from the court page
From the court index page for the case, copy the visible text for: Case Title, Case Number, Case Location, Case Type, Date Filed.

**Example:**
```
Case Title:   DEFENDANT KEVIN PHAN
Case Number:  SCN367895
Case Location: North County
Case Type:    Criminal
Date Filed:   12/29/2016
```

### Attaching evidence (PDFs & articles)
- **Court documents:** appellate opinions, minute orders  
- **Articles:** relevant news stories or saved PDFs  
- The GPT will consider everything and include helpful links in its JSON output.

---

## 2. Example JSON returned by the GPT

```json
{
  "defendant_name": "This text includes the name of the defendant",
  "crime_date": "This includes the date in the format YYYY-MM-DD",
  "defendant_age_at_crime": "This text includes the age in numbers of the defendant",
  "sentence": "This text includes the eventual sentence the defendant received",
  "charges_convicted": "This text includes the charges pressed",
  "crime_type": "This text includes the type of alleged offense",
  "defendant_race": "This text includes the race of the defendant",
  "juvenile_adult_court": "This text includes either 'Adult' or 'Juvenile' depending on the court the defendant was sent to",
  "plea_or_trial": "This text will include whether or not the defendant made a plea",
  "confidence_level": "This text includes how reliable the sources are for the provided information, whether it's high, medium, or low. It's a good idea to manually double check if the confidence level comes out as low.",
  "case_summary": "This text summarizes the incident and provides an explanation why special circumstance under the penal code 190.2 applies or doesn't apply if it's specifically a homicide case",
  "special_circumstance_overall_status": "This includes a shorthand code of conveying whether the incident was special circumstance or not, wnad whether it was applied",
  "sources": [
    This provides sources of where the information for the json was pulled. For example:
    "https://codes.findlaw.com/ca/penal-code/pen-sect-190-2/"
  ]
}
```

---

## 3. Mapping JSON → Spreadsheet columns

- `defendant_name` → DefendantName  
- `crime_date` → CrimeDate  
- `defendant_age_at_crime` → AgeAtCrime (optional; formula preferred)  
- `sentence` → Sentence  
- `charges_convicted` → ChargesConvicted  
- `crime_type` → CrimeType  
- `defendant_race` → DefendantRace  
- `juvenile_adult_court` → JuvenileOrAdultCourt  
- `plea_or_trial` → PleaOrTrial  
- `confidence_level` → Confidence  
- `case_summary` → CaseSummary  
- `special_circumstance_overall_status` → SpecialCircumstance  
- `sources` → Source_ArticleURL + Notes  

---

## 4. Prompt transparency

The exact system/user prompt used for this step is stored in:

```
prompts/extractor_prompt.md
```

Maintaining this file ensures **transparency** and lets contributors update the workflow
as new models evolve.

---

## 5. Quality hints for Step 2

- Prefer appellate opinions and official documents.  
- Be careful with **crime date vs. filing/sentencing dates**.  
- Cross-check when names collide using docket details.  
- If GPT returns nothing: try removing middle names/suffixes, include nickname variations, reattach PDFs and article links.  
- For rows with no info, leave blank or add a note in **Notes** (e.g., `NO INFO`).  

---

## 6. Spreadsheet formulas (Age at Crime & Age Band)

Step 2 relies on the same formulas from Step 1 to compute ages and assign age bands.  
See Step 1 README for the detailed formulas.

---

## 7. Data model (columns & meanings)

| Column              | Description                                               | Source             |
|---------------------|-----------------------------------------------------------|--------------------|
| CaseNumber          | Court case identifier                                     | Input file         |
| DataStatus          | Status flag for Step 1 extraction                         | Step 1             |
| DefendantName       | Full name from court records                              | Step 1 / Step 2    |
| DOB                 | Birth year (YYYY)                                         | Step 1             |
| DateFiled           | Filing date                                               | Step 1             |
| CaseLocation        | North County / San Diego / East / South                   | Step 1             |
| CrimeDate           | Date the offense occurred                                 | Step 2             |
| AgeAtCrime          | Calculated numeric age                                    | Formula / Step 2   |
| AgeAtFiling         | Age on the filing date (optional)                         | Formula            |
| AgeBand             | Juvenile / Emerging Adult / Adult                         | Formula            |
| Sentence            | Specific sentence imposed                                 | Step 2             |
| ChargesConvicted    | e.g., First-degree murder                                 | Step 2             |
| CrimeType           | e.g., Robbery; Assault; Homicide (shooting)               | Step 2             |
| JuvenileOrAdultCourt| Whether the case was in juvenile or adult court           | Step 2             |
| PleaOrTrial         | Plea vs. trial outcome                                    | Step 2             |
| SpecialCircumstance | Overall status code from §190.2 (SC_*)                    | Step 2             |
| Confidence          | GPT’s confidence label                                    | Step 2             |
| CaseSummary         | 1–3 sentence summary of the case                          | Step 2             |
| DefendantRace       | Only if explicitly stated in reliable sources             | Step 2             |
| DAEra               | A DA tenure label if you’re studying a period             | Step 1 / Constant  |
| Source_DocketURL    | Court record link (court index page)                      | Step 1             |
| Source_ArticleURL   | Primary news/opinion/official link                        | Step 2             |
| Notes               | QC flags, assumptions, and any extra source links         | All steps          |

---

## 8. Quality control & manual review

- Distinguish **crime date** from **filing/sentencing** dates.  
- Add confidence notes (`high`, `low`).  
- For rows with no info, mark `NO INFO` in Notes.  
- Double-check co-defendant attributions and name variants.  
