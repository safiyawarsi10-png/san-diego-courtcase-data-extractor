# Using the Claude Research Tool — Step 2 Guide

This guide explains how to use the specialized Claude project to research and fill out your Step 1 spreadsheet at scale. No coding required.

---

## Overview

After Step 1 generates your spreadsheet of case numbers and defendant names, Step 2 is where the real research happens — finding incident dates, sentences, charges, and sources for each case. This guide walks you through doing that efficiently using Claude's Projects feature, which lets you load a specialized legal research prompt once and reuse it across many sessions.

This tool replaces the previous GPT-based research method. Claude handles large-scale legal datasets more accurately, produces more consistent §190.2 classifications, and provides better source attribution — making it the strongly recommended choice for this workflow.

The core workflow is:

1. Set up a Claude Project with the specialized prompt
2. Split your spreadsheet into batches of 10 cases
3. Open 2–3 parallel Claude tabs and feed one batch per tab
4. Collect the filled-out results
5. Compile everything back into one master spreadsheet
6. Follow up on gaps in person at the courthouse

---

## Step 1 — Create a Claude Project

Claude Projects let you save a persistent system prompt so you don't have to re-paste the instructions every session. This is essential for processing hundreds of cases consistently.

1. Go to [claude.ai](https://claude.ai) and sign in. A **Claude Pro** account is strongly recommended — free accounts have message limits that will interrupt large batch runs.
2. In the left sidebar, click **"New Project"**.
3. Give your project a name, e.g.: `SD Court Case Researcher`.
4. You'll see a **"Project Instructions"** field (also called the system prompt area). This is where the specialized prompt lives — paste the full contents of `Step2_Extract/CLAUDE_MASTER_PROMPT.md` into this field.
5. Click **Save**.

That's it. Every conversation you start inside this project will automatically use the specialized legal research prompt, with full knowledge of the §190.2 classification system, the 4 SC codes, the sentencing rules, and the San Diego news sources — without you having to paste anything again.

> **Tip:** Double-check that the prompt saved correctly by opening a new chat inside the project and asking: *"What are the 4 SC codes?"* Claude should recite them back immediately.

---

## Step 2 — Split Your Spreadsheet Into Batches of 10

Your Step 1 output is likely hundreds of rows. Claude works best when given focused, manageable batches — 10 cases at a time is the recommended size for reliable, thorough results.

1. Open your Step 1 Excel file.
2. Copy rows 1–10 (plus the header row) into a new sheet or a new file. Save it as `batch_001.xlsx`.
3. Repeat for rows 11–20 (`batch_002.xlsx`), 21–30 (`batch_003.xlsx`), and so on until all cases are covered.
4. For ~1,300 cases, this will produce ~130 batch files. You can name them however you like — just keep them organized in a folder, e.g. `batches/`.

> **Shortcut:** You can also just copy and paste 10 rows of data directly into the chat as plain text rather than uploading a file. Either approach works.

---

## Step 3 — Open 2–3 Parallel Tabs and Run Batches

To speed things up, you can run multiple batches simultaneously by opening several Claude tabs at once, each working on a different batch.

1. Open your `SD Court Case Researcher` project in Claude.
2. Start a **new conversation** inside the project.
3. Upload or paste your first batch (10 cases) and send this message:

```
Fill this out. Find as much information as possible on each person — 
incident date, sentence, charges, victim info, age at crime, 
special circumstance classification, and sources.
```

4. Open a **second browser tab**, go back to your project, start another new conversation, and do the same with your second batch.
5. Optionally open a **third tab** for a third batch.

Running 2–3 tabs in parallel means you can cut your total research time roughly in half or better, since each session runs independently.

> **Important:** Keep each batch in its own conversation. Don't mix batches in the same chat — it increases the risk of Claude confusing cases across rows.

> **Note on rate limits:** If Claude starts responding slowly or says it's reached a limit, pause for 10–15 minutes before continuing. Claude Pro handles large runs better than free accounts but may still throttle during very long sessions.

---

## Step 4 — Collect Your Filled-Out Results

For each batch, Claude will return the completed data — either as a structured table, JSON, or both depending on how it formats the output.

1. Copy Claude's output for each batch into a new sheet in Excel, or save it as its own file (e.g. `batch_001_filled.xlsx`).
2. Do this for every batch until all ~130 batches are processed.
3. Keep the filled batches in a separate folder, e.g. `batches_filled/`.

---

## Step 5 — Compile Everything Into One Master Spreadsheet

Once all batches are filled out, ask Claude to help you compile them.

1. Open a **new conversation** in your Claude project (or in a regular Claude chat — you don't need the specialized prompt for this step).
2. Upload all your filled batch files, or paste their contents, and send:

```
Compile all of these into one master spreadsheet.
Remove any columns that are consistently empty or unfilled across all cases.
Keep all columns that have data in at least some rows.
```

3. Claude will return a single consolidated dataset. Save this as your master output file, e.g. `SD_Cases_Master.xlsx`.

> **Tip:** After compiling, do a quick scan of the data. Look for columns that are mostly empty — these are good candidates to drop before analysis. Also look for rows where confidence is marked `low` — these are your priority follow-up cases.

---

## Step 6 — Follow Up on Missing Information In Person

Even with thorough AI research, some cases will have gaps. The most common missing fields are:

- **Sentence** — not always reported in news; may only exist in court records
- **Exact incident date** — sometimes only a year or month is reported
- **Defendant race** — rarely in news articles, may require court documents
- **Charges convicted of** — plea deals and lesser charges often go unreported

For these cases, the next step is to visit the courthouse directly.

### San Diego Superior Court Locations

| Court | Address | Cases |
|-------|---------|-------|
| Central (San Diego) | 1100 Union St, San Diego, CA 92101 | SCD prefix cases |
| North County (Vista) | 325 S Melrose Dr, Vista, CA 92081 | SCN prefix cases |
| East County (El Cajon) | 250 E Main St, El Cajon, CA 92020 | SCE prefix cases |
| South County (Chula Vista) | 500 3rd Ave, Chula Vista, CA 91910 | SCS prefix cases |

### What to Do at the Courthouse

1. Bring your list of case numbers with missing data (filter your master sheet for `confidence = low` or blank fields).
2. Go to the **Civil/Criminal Records window** and request the case file or minute orders for each case number.
3. Minute orders (the official record of each court hearing) will have exact sentencing language, charges, and dates.
4. Some courthouses offer a public access terminal where you can look up cases yourself — ask the clerk.
5. Bring a laptop or phone to update your spreadsheet on the spot, or photograph documents to fill in later.

### Tips for Court Visits

- **Arrive early.** Records windows often have queues and may close for lunch.
- **Bring photo ID.**
- **Some records may be sealed** — particularly juvenile cases. You won't be able to access these without a court order.
- **Appellate opinions** are publicly available online via the California Courts website and can sometimes fill in gaps without a courthouse visit.

---

## Quick Reference — The Full Workflow

```
Step 1 Output (large spreadsheet)
         │
         ▼
Split into batches of 10 cases
         │
         ▼
Open 2–3 Claude tabs (SD Court Case Researcher project)
Feed one batch per tab → "Fill this out. Find as much info as possible."
         │
         ▼
Collect filled batches (save each output)
         │
         ▼
Compile into one master spreadsheet
Remove consistently empty columns
         │
         ▼
Review low-confidence rows
         │
         ▼
Court visit for remaining gaps
         │
         ▼
Final auditable dataset — ready for analysis
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Claude doesn't seem to know the SC codes | Check that the master prompt is saved in Project Instructions — start a fresh chat inside the project |
| Output format is inconsistent across batches | Ask Claude at the end of each session: *"Return this as a table with the same columns as the input"* |
| Claude mixes up defendants across rows | Keep batches to 10 or fewer; start a new conversation for each batch |
| Rate limit hit mid-batch | Wait 10–15 minutes, then continue in a new conversation — paste the remaining cases |
| Compiled spreadsheet has duplicate columns | Ask Claude: *"Deduplicate columns and keep the one with more data filled in"* |
| Case number returns no results anywhere | Flag as `confidence = low`, add to courthouse visit list |
