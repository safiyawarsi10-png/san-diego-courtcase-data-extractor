# Data Collection & Research
## San Diego Criminal Cases


Content

[**Purpose**](#purpose)

[**Background**](#background)

[**The Manual Research Challenge**](#the-manual-research-challenge)

[Automation With Hybrid Approach
](#automation-with-hybrid-approach)

> [What Still Requires Human Oversight
> ](#what-still-requires-human-oversight)

[**What You Need Before Starting**](#what-you-need-before-starting)

[**Running the Analysis**](#running-the-analysis)

> [Step 1: Extract Court Data](#step-1-extract-court-data)
>
> [Step 2: Finding Crime Dates & Sentences Using GPT
> ](#step-2-finding-crime-dates-sentences-using-gpt)
>
> [Step 3: Manual Review & Completion
> ](#step-3-manual-review-completion)
>
> [Getting Help](#getting-help)
>
> [Final Tips for Success](#final-tips-for-success)
>
> [Why This Step Matters](#why-this-step-matters)

[**Appendix**](#appendix)

> [A. GPT Extractor Prompt - Technical Implementation
> ](#a.-gpt-extractor-prompt---technical-implementation)

#  

# Purpose

This document outlines the research process and tools used by our team
and volunteers to build a transparent dataset for bias analysis.

We\'re building a structured, auditable dataset of San Diego homicide
cases so we can ask one simple, powerful question: Is the DA\'s office
more (or less) harsh on juvenile and emerging-adult defendants than
you\'d expect?

Concretely, we\'re:

1.  **Assembling core facts** (defendant name, birth-year, filing date)
    > straight from the Superior Court\'s public \"Case Detail\" pages.

2.  **Pulling in crime dates and sentencing outcomes** from reputable
    > local news or appellate opinions using a custom GPT tool.

3.  **Computing each defendant\'s exact age at the time of the crime**,
    > then bucketing them as:

    -   Juvenile (\< 18)

    -   Emerging Adult (18--26)

    -   Adult (\> 26)

4.  **Flagging any gaps** or estimates in our data (e.g. \"DOB≈1993
    > inferred from press release\") so nothing is hidden.

Why? Once every record has:

-   a verified crime date,

-   a birth-year (or exact DOB),

-   the resulting sentence length/type,

-   and a note of the source URLs,

We can pivot across race and age-bands and run straightforward
statistics (chi-square, regression, etc.) to see if juveniles or
18--26-year-olds were treated more harshly---or more leniently---than
older adults.

That transparent, repeatable pipeline---court lookup → GPT-assisted news
research → derived fields → QC flags---lets anyone audit every cell,
reproduce our steps, and trust whatever bias-analysis we publish.

# Background

This toolkit supports research into potential racial bias in criminal
sentencing, specifically examining how age intersects with race in
homicide case outcomes. The research focuses on:

**Research Question**: Does sentencing vary by race for defendants who
were juveniles (under 18) or emerging adults (18-26) when they committed
serious crimes in San Diego?

**Data Scope**: Approximately 1,300 case numbers covering San Diego
criminal cases prosecuted during a District Attorney tenure, or any
other set, visible at [[court
website]{.underline}](https://courtindex.sdcourt.ca.gov/CISPublic/casesearch).

**Key Variables to Collect**:

-   **Defendant Demographics**: Name, birth year, race (when available)

-   **Crime Details**: Exact date crime was committed

-   **Case Outcomes**: Specific sentence received

-   **Age Analysis**: Defendant\'s age when crime occurred

-   **Court Information**: Case filing dates, locations

# The Manual Research Challenge

**What This Research Involves Without Automation**

If you were to do this research entirely by hand, here\'s what would be
required for **each of the 1,300+ cases**:

### Step 1: Court Record Lookup (2-3 minutes per case)

1.  **Navigate to San Diego Superior Court website**

    -   Go to: https://courtindex.sdcourt.ca.gov/CISPublic/

    -   Determine correct court location (North County, San Diego, East
        > County, South County)

    -   Enter case number and search

2.  **Extract Court Information**

    -   Find defendant\'s full name

    -   Record birth year (if available)

    -   Note case filing date

    -   Document case location and type

    -   Handle multi-defendant cases (create separate records)

3.  **Navigate Authentication Issues**

    -   Court website requires active session

    -   Sessions expire frequently

    -   Need to restart searches when blocked

### Step 2: Manual Outcome Research (10-15 minutes per case)

**Note**: This step has been replaced by GPT-assisted research described
in the automation section below.

1.  **Search Multiple News Sources**

    -   San Diego Union-Tribune archives

    -   Times of San Diego

    -   NBC San Diego, CBS 8, Fox 5, ABC 10

    -   Local patch sites and community papers

2.  **Search Strategy for Each Case**

    -   Try defendant name + \"San Diego crime\"

    -   Try defendant name + \"convicted\" + \"sentenced\"

    -   Try case number + court terms

    -   Search different name variations and nicknames

3.  **Extract Key Information from Articles**

    -   **Crime Date**: When the actual crime occurred (not trial date)

    -   **Sentence Details**: Exact punishment received

    -   **Defendant Race**: Only if explicitly mentioned

    -   **Age Information**: Sometimes stated directly

    -   **Case Context**: Juvenile vs adult court, plea vs trial

4.  **Verify Information Accuracy**

    -   Cross-check dates between multiple sources

    -   Ensure sentence information matches defendant

    -   Distinguish between co-defendants in multi-person cases

### Step 3: Manual Calculations & Validation (5-10 minutes per case)

1.  **Calculate Age at Crime**

    -   Formula: Crime Year - Birth Year = Age at Crime

    -   Handle incomplete birth dates (year only)

    -   Account for crime date vs case filing date differences

2.  **Assign Age Categories**

    -   Juvenile: Under 18 years old

    -   Emerging Adult: 18-26 years old

    -   Adult: Over 26 years old

3.  **Data Quality Review**

    -   Flag missing information

    -   Note confidence levels

    -   Document sources for verification

### Total Time Investment

-   **Per Case**: 17-28 minutes of focused research

-   **Full Dataset**: 1,300+ cases × 22 minutes = **480+ hours**

-   **Timeline**: 3-4 months of full-time work for one researcher

### Common Manual Research Challenges

-   **Court Website Issues**: Frequent timeouts, session expiration,
    > inconsistent interface

-   **News Archive Limitations**: Paywalls, broken links, incomplete
    > digitization

-   **Name Variations**: Defendants may be referred to differently
    > across sources

-   **Multi-Defendant Confusion**: Ensuring correct sentence attribution

-   **Date Ambiguity**: Distinguishing crime date from
    > arrest/trial/sentencing dates

-   **Missing Information**: Some cases have limited public coverage

-   **Data Entry Errors**: Manual transcription mistakes in large
    > datasets

#  

# Automation With Hybrid Approach

This toolkit **automates 85-90% of the manual research work**,
transforming months of research into days using a combination of
automated court data extraction and AI-assisted news research:

**Script 1: step1_fetch_cases_playwright.py - Court Data Extraction**

**What it replaces**: Hours of manual court website navigation

**What it does automatically**:

-   Handles court website authentication and sessions

-   Searches all four San Diego court locations automatically

-   Extracts defendant names, birth years, filing dates

-   Manages multi-defendant cases (creates separate rows)

-   Handles website errors and timeouts gracefully

-   Creates properly formatted Excel output

-   Saves progress if interrupted

**Time savings**: 2-3 minutes per case → 30 seconds per case

**Step 2: GPT-Assisted News Research & Analysis**

Volunteers copy the defendant\'s name and filing date from the Excel
sheet, paste them into our custom GPT interface, and receive structured
case facts including the crime date, sentence, and sources. This
replaces hours of manual news searching and article reading per case.

**What it does**:

-   Uses a specialized GPT tool for intelligent news research

-   Searches multiple San Diego news sites with optimized strategies

-   Extracts key information (crime dates, sentences, demographics)
    > accurately

-   Provides reliable source URLs for verification

-   Handles multi-defendant cases intelligently

-   Allows manual quality control at each step

**Time savings**: 10-15 minutes per case → 2-3 minutes per case

## What Still Requires Human Oversight

**Critical Manual Steps (Step 3)**:

-   Age calculations and category assignment

-   Quality review of GPT findings

-   Research for cases where no articles were found

-   Final data validation before statistical analysis

**Why Human Review Matters**: While automation handles the bulk
research, human oversight ensures accuracy, catches edge cases, and
maintains the audit trail essential for credible academic research.

**Overall Impact**

-   **Time Reduction**: 480+ hours → 40-60 hours total

-   **Accuracy Improvement**: AI-assisted extraction reduces errors

-   **Consistency**: Standardized data extraction and formatting

-   **Audit Trail**: Every piece of data includes source URLs

-   **Quality Control**: Human oversight ensures accuracy

#  

# What You Need Before Starting

**1. Computer Requirements**

-   **Operating System**: Windows, Mac, or Linux

-   **Internet Connection**: Stable broadband

-   **Storage Space**: \~500MB for software + \~50MB for your data

-   **Time Availability**: 2-3 hours for setup, then can run scripts
    > overnight

**2. Required Accounts & Access**

-   **ChatGPT Account** (for the Criminal Case Extractor GPT)

    -   Go to: https://chat.openai.com/

    -   Create account (free tier works, but paid tier recommended for
        > heavy usage)

    -   Access to custom GPT: [[Criminal Case
        > Extractor]{.underline}](https://chatgpt.com/g/g-68807caf03048191a1dfe9e2dfdb1502-criminal-case-extractor)

-   **San Diego Court Access**

    -   No special account needed

    -   You\'ll get session ID from browser (we\'ll show you how)

**3. Input Data File**

-   **Format**: Text file with one case number per line

> **Example content**:\
> CN367913
>
> CN367895
>
> CD270095
>
> CE366120
>
> CS290571

-   **Your file**: Should contain all \~1,300 case numbers you want to
    > research

#  

### Install Required Software

**Step 1: If not installed already, fresh Python Installation**

1.  **Download Python**: Go to https://python.org/downloads

2.  **Install Python**: Choose \"Add to PATH\" during installation

3.  **Open Terminal/Command Prompt**

##### **Install packages**:

##### \> pip install playwright pandas openpyxl requests

##### \> playwright install chromium

**Step 2: Set Up ChatGPT Access**

1.  **Sign up at ChatGPT**: https://chat.openai.com/

2.  **Test the GPT tool**: Visit [[Criminal Case Extractor
    > GPT]{.underline}](https://chatgpt.com/g/g-68807caf03048191a1dfe9e2dfdb1502-criminal-case-extractor)

3.  **Verify access**: You should see the custom interface

**Step 3: Get Court Session ID**

1.  **Open your web browser**

2.  **Go to**: https://courtindex.sdcourt.ca.gov/CISPublic/

3.  **Do any case search** (just to establish a session)

4.  **Open Developer Tools**: Press F12

5.  **Go to Application tab** → Storage → Cookies

6.  **Find courtindex.sdcourt.ca.gov**

7.  **Copy JSESSIONID value** (looks like: A1B2C3D4E5F6.worker1)

**Step 4: Prepare Your Files**

1.  **Create a folder** for your project (e.g., bias_analysis)

2.  **Put these files in the folder**:

    -   step1_fetch_cases_playwright.py

    -   your_cases.txt (your list of case numbers)

#  

# Running the Analysis

## Step 1: Extract Court Data 

**Run this command** (replace SESSION_ID and cases.txt with your
values):

##### python3 step1_fetch_cases_playwright.py SESSION_ID cases.txt

**Example**:

##### python3 step1_fetch_cases_playwright.py A1B2C3D4E5F6 san_diego_cases.txt

**What happens**:

-   Script opens browser windows automatically

-   Visits court website for each case number

-   Extracts defendant information

-   Creates Excel file: san_diego_cases_dob_extracted.xlsx

**Expected time**: \~5 seconds per case (\~100 minutes for 1200 cases)

**You can safely interrupt** (Ctrl-C) and it will save partial progress

## Step 2: Finding Crime Dates & Sentences Using GPT

**Goal:\
**For each defendant in our Excel sheet, we need to find:

1.  **Date when the crime occurred**

2.  **Sentence the defendant received**

3.  **Links to reliable sources confirming this information**

This data helps us analyze whether younger defendants (under 26) receive
harsher treatment in the justice system.

### What You\'ll Be Doing

You\'ll use a specialized AI tool on ChatGPT that automatically searches
for and extracts legal case information using a custom-designed prompt.

👉 **Access the tool here:\
**🔗 [[Criminal Case Extractor
GPT]{.underline}](https://chatgpt.com/g/g-68807caf03048191a1dfe9e2dfdb1502-criminal-case-extractor)

### Step-by-Step Process

**Step 1: Access the GPT Tool**

-   Click the link above

-   Make sure you\'re logged into ChatGPT

-   You should see the **\"Criminal Case Extractor\"** interface

**Step 2: Get Information from Court Records**

Each Excel row contains a court record link in the **\"Court Record\"**
or **\"Docket URL\"** column.

**To extract the needed information:**

-   Click the court record link (opens San Diego Superior Court case
    > page)

-   Copy the pieces of information:

> ![](media/image1.png){width="2.8802088801399823in"
> height="2.367918853893263in"}

**Paste into the GPT:**

##### Case Title: DEFENDANT JAVIER ALFONSO SEDA

##### Case Number: SCN359605 Case Location: North County 

##### Case Type: Criminal Date Filed: 07/14/2016

**Step 3: Review the GPT Response**

The GPT will return structured data in a JSON format:

##### {

#####  \"crime_date\": \"2009-12-20\",

#####  \"sentence\": \"25 years to life\",

#####  \"sources\": \[

#####  \"https://example-news-source.com/article1\",

#####  \"https://court-documents.com/case2\"

#####  \]

##### }

**Step 4: Transfer Data to Excel**

Copy the relevant information into your Excel columns:

  ------------------------------------------------------------------------
  **Crime Date**   **Sentence**        **Article URL**
  ---------------- ------------------- -----------------------------------
  2009-12-20       25 years to life    https://example-source.com/\...

  ------------------------------------------------------------------------

**Step 5: Handle Cases with No Information**

If the GPT returns \"confidence_level\": \"none\" or indicates no
information was found:

-   Leave those Excel cells blank, OR

-   Write **\"NO INFO\"** in the Notes column

-   Consider highlighting the row for later manual research

**Step 6: Continue Through Your Cases**

You can process multiple cases in the same GPT session - it handles each
query separately.

### Tips for Best Results

**For accuracy:**

-   Double-check that the **Date Filed** matches exactly what\'s in the
    > court record

-   If GPT doesn\'t find the case, try removing middle names or suffixes
    > (Jr., III, etc.)

-   Don\'t edit the JSON response - just copy the fields you need

**Source priority:**

-   Prefer legal sources (court documents, appellate decisions)

-   News articles from major outlets are also good

-   Avoid blog posts or unofficial sources

## Step 3: Manual Review & Completion

After completing the GPT-assisted research, you\'ll need to manually:

1.  **Calculate age bands** using the provided crime dates and birth
    > years

2.  **Review flagged cases** where automated research found no articles

3.  **Validate questionable data** marked as \"low confidence\"

4.  **Fill any remaining gaps** through targeted manual research

### Understanding Your Results

**Excel File Structure**

Your final Excel file will have these columns:

  ------------------------------------------------------------------------
  **Column**              **Description**                    **Source**
  ----------------------- ---------------------------------- -------------
  **CaseNumber**          Court case identifier              Input file

  **DefendantName**       Full name from court records       Script 1

  **DOB**                 Birth year (YYYY format)           Script 1

  **DateFiled**           When case was filed in court       Script 1

  **CaseLocation**        North County, San Diego, etc.      Script 1

  **CrimeDate**           When the actual crime occurred     Step 2 GPT

  **AgeAtCrime**          Calculated age (manual step)       Step 3

  **AgeBand**             Juvenile/Emerging Adult/Adult      Step 3

  **Sentence**            Specific punishment received       Step 2 GPT

  **DefendantRace**       Only if explicitly stated in       Step 2 GPT
                          articles                           

  **DAEra**               \"Bonnie Dumanis\" (constant)      Script 1

  **Source_DocketURL**    Court record link for verification Script 1

  **Source_ArticleURL**   News article link for verification Step 2 GPT

  **Notes**               Data quality flags and comments    All steps
  ------------------------------------------------------------------------

### Data Quality Indicators

**High Quality Records**:

-   Have both court data AND news article data

-   Crime date found and confirmed

-   Sentence information extracted

-   Birth year available for age calculation

**Needs Manual Review**:

-   Notes contain \"low confidence\"

-   Missing crime date or sentence

-   No articles found during GPT research

-   Birth year missing from court records

**Success Metrics to Expect**

**Typical Success Rates**:

-   **Court Data Extraction**: 95-98% (most cases have basic court
    > records)

-   **GPT News Research**: 75-90% (varies by case prominence and time
    > period)

-   **Complete Information**: 70-85% of cases will have all needed data

-   **Manual Research Needed**: 15-30% of cases require some additional
    > work

### Troubleshooting

**Common Issues & Solutions**

**\"Session test failed\" Error**

**Problem**: Court website session expired or invalid\
**Solution**:

1.  Get fresh JSESSIONID from browser (see setup instructions)

2.  Make sure you\'ve done a recent search on the court website

3.  Try a different browser if sessions keep expiring

**GPT Not Finding Cases**

**Problem**: GPT returns no information for known cases\
**Solutions**:

1.  Check if defendant names are formatted correctly

2.  Try removing middle names or suffixes (Jr., III, etc.)

3.  Verify the Date Filed is accurate

4.  Some older cases may have limited digital news coverage

**ChatGPT Rate Limiting**

**Problem**: \"Too many requests\" error from ChatGPT\
**Solutions**:

1.  Wait 1-2 hours before continuing

2.  Consider upgrading to ChatGPT Plus for higher limits

3.  Process cases in smaller batches throughout the day

**Script Crashes or Freezes**

**Problem**: Network issues or website blocking\
**Solutions**:

1.  Check internet connection

2.  Wait 10-15 minutes before retrying (rate limiting)

3.  Restart scripts - they resume from where they stopped

4.  Run smaller batches (50-100 cases at a time)

**Excel File Won\'t Open**

**Problem**: File corruption during saving\
**Solutions**:

1.  Scripts create backup files automatically

2.  Look for files ending in \_BACKUP_HHMMSS.xlsx

3.  Restart script - it will create new output file

## Getting Help

**Before Asking for Help**

1.  **Check the error message carefully** - often it tells you exactly
    > what\'s wrong

2.  **Try with a few test cases first** - validates your setup

3.  **Check your internet connection** - both scripts and GPT require
    > stable connectivity

4.  **Verify your ChatGPT access** - make sure you can access the custom
    > GPT

**What Information to Include When Asking for Help**

1.  **Exact error message** (copy and paste)

2.  **Which step failed** (Step 1 court data, Step 2 GPT research, etc.)

3.  **Your operating system** (Windows, Mac, Linux)

4.  **How many cases you\'re processing**

5.  **Whether the GPT tool works for test cases**

**Understanding Costs**

**ChatGPT Usage**:

-   Free tier: Limited daily usage

-   ChatGPT Plus (\$20/month): Much higher limits, recommended for large
    > datasets

-   Full 1,300 case dataset: May require ChatGPT Plus for uninterrupted
    > processing

**Time Investment**:

-   Setup: 2-3 hours

-   Script 1 (court data): 4-8 hours for full dataset

-   Step 2 (GPT research): 8-15 hours for full dataset (with human
    > input)

-   Manual review: 10-20 hours depending on data quality

## Final Tips for Success

**Start Small**

-   Test with 10-20 cases first

-   Validate the full pipeline works before processing 1,300 cases

-   Practice with the GPT tool on a few known cases

**Monitor Progress**

-   Script 1 prints progress updates constantly

-   Excel files update after each successful case

-   Keep track of which cases you\'ve processed with the GPT

**Backup Your Work**

-   Scripts create automatic backups

-   Keep copies of your input files

-   Save your Excel file frequently during GPT research

**Plan for Manual Work**

-   15-30% of cases will need some manual research

-   Budget time for Step 3 (manual calculations and review)

-   The automation handles the bulk work, but human oversight ensures
    > quality

**Use the Audit Trail**

-   Every data point includes source URLs

-   You can verify any automated finding

-   Essential for academic credibility and peer review

## Why This Step Matters

This information is **essential** for calculating each defendant\'s age
when they committed their crime. This age data allows us to analyze
whether the justice system treats younger defendants differently than
older ones - the core question of our research.

Your careful work ensures our findings are accurate and credible. Thank
you for contributing to this important analysis!

# Appendix

## A. GPT Extractor Prompt - Technical Implementation

For researchers interested in setting up their own custom
[[GPT]{.underline}](https://chatgpt.com/) or adapting this prompt for
use with [[Claude]{.underline}](https://claude.ai/chat/) or other AI
systems, below is the complete prompt that powers our Criminal Case
Extractor GPT tool.

### Understanding the Prompt Structure:

This prompt follows best practices for legal information extraction:

-   **Multi-phase search strategy** prioritizing legal sources over news
    > articles

-   **Systematic verification** requirements to prevent AI
    > hallucinations

-   **Structured JSON output** for consistent data processing

-   **Source prioritization** emphasizing appellate decisions and court
    > records

-   **Failure recovery protocols** for difficult-to-find cases

The prompt is designed to be methodical, transparent, and reproducible -
essential qualities for academic research.

### Complete GPT Extractor Prompt:

GPT link : 🔗 [[Criminal Case Extractor
GPT]{.underline}](https://chatgpt.com/g/g-68807caf03048191a1dfe9e2dfdb1502-criminal-case-extractor)

Recommended model (this was built for): **GPT-5**

\*\*ROLE:\*\* You are a specialized legal information extraction agent
focused on San Diego County criminal cases.

\*\*TASK:\*\* When provided with a defendant\'s full name and filing
date, independently research and produce the specified structured data
following the verified process below. Respond only with the final JSON
object---no commentary or context.

\*\*REQUIREMENTS & METHOD:\*\*

1\. Focus solely on the specified defendant (ignore co-defendants and
unrelated individuals)

2\. Confirm crimes occurred before or around the provided filing date.
Cases may occur months/years before filing, with appellate decisions
containing detailed facts years later

3\. \*\*You are an autonomous research agent:\*\* Complete the entire
research process without requesting user confirmation. If you encounter
uncertainty about search strategies or source reliability, make the most
reasonable decision and explicitly document your process in search tool
preambles

4\. Always begin with highest quality primary legal sources and apply
rigorous search, verification, and extraction as outlined below

\## Systematic Search Protocol

\*\*(Execute searches in this exact order - do not skip phases)\*\*

\### PHASE 1: Legal Database Priority (START HERE - MOST CRITICAL)

Execute these search templates first, in order:

• \"People v. \[Last Name\]\" + San Diego

• \"\[Full Name\]\" + \"convicted\" + San Diego + \[filing year\]

• \"\[Last Name\]\" + \"California Court of Appeals\" + San Diego

• \"\[Last Name\]\" + \"Superior Court\" + San Diego + criminal

• \"\[Full Name\]\" + \"sentenced\" + San Diego

\*\*Tool Call Requirements:\*\* After each search, use thorough
preambles explaining your search strategy and findings. Use web_fetch to
resolve and verify URLs.

\### PHASE 2: Official Records

\- San Diego County District Attorney press releases

\- Superior Court of California, San Diego records

\- California appellate court decisions

\- Federal court records (if applicable)

\### PHASE 3: Name Variations

Search all forms including: provided full name, first and last only,
\"Last, First\" order, alternative spellings.

\### PHASE 4: Temporal Context Expansion

Search 6 months before filing to 5 years after. Query examples:

• \"\[Location\] murder \[year range around filing\]\"

• \"convicted \[location\] \[filing year and following years\]\"

• Appellate decisions 2-7 years post-filing

\### PHASE 5: Traditional Media

Search local newspapers, alternative weeklies, and TV news archives.

\## Verification & Source Reliability

\*\*Prioritize sources in this exact order:\*\*

1\. Appellate court decisions (highest reliability)

2\. Trial court records and official documents

3\. District Attorney press releases and law enforcement communications

4\. Major newspaper legal coverage

5\. Local alternative media

6\. General news sources

\*\*Verification Requirements:\*\*

\- Always verify that crime date aligns with filing date timeline

\- Cross-reference defendant name spelling across sources

\- Confirm jurisdiction matches

\- For critical facts, require at least two independent sources (legal
sources weighted most heavily)

\- Use web_fetch tool to open each candidate link and verify it contains
substantive information

\## JSON Output Format

\*\*Required Structure:\*\*

\`\`\`json

{

\"defendant_name\": \"\",

\"crime_date\": \"YYYY-MM-DD or Month YYYY\",

\"defendant_age_at_crime\": \"\",

\"sentence\": \"\",

\"charges_convicted\": \"\",

\"crime_type\": \"\",

\"defendant_race\": \"\",

\"juvenile_adult_court\": \"\",

\"plea_or_trial\": \"\",

\"confidence_level\": \"\",

\"case_summary\": \"\",

\"sources\": \[\]

}

\`\`\`

\*\*Confidence Level Criteria:\*\*

\- \*\*high\*\*: Key facts corroborated (appellate or multiple strong
sources)

\- \*\*medium\*\*: Some facts corroborated or one strong source

\- \*\*low\*\*: Few details or only less reliable sources

\- \*\*none\*\*: No reliable information found with systematic search

\*\*Critical Rule:\*\* If details cannot be verified from reliable
sources, leave JSON fields blank. Never guess or infer missing
information.

\## Search Failure Recovery Protocol

If no results after 8 legal database searches, try:

• \"\[Last Name\] v. State\" or \"State v. \[Last Name\]\"

• \"\[Last Name\] + San Diego + prison\" or \"+ sentenced\"

• Remove middle names/prefixes completely

• Broaden date range (1-24 months pre-filing)

• Alternative name spellings

• \"\[Defendant last name\] San Diego criminal \[year range\]\"

\## Agent Behavior Requirements

\*\*You are an autonomous agent:\*\* Continue research through all
phases until reliable case information is found or all steps are
exhausted. Do not stop when encountering uncertainty---make reasonable
decisions and continue. Always document your search and decision process
in tool preambles.

\*\*Only terminate when:\*\* You have completed all search phases OR
found sufficient information from reliable sources to populate the JSON
structure with high confidence.

\## Final Output Instructions

\*\*OUTPUT ONLY\*\* the JSON object with no additional commentary.
Include up to 3 most authoritative source URLs in the sources array,
prioritizing legal sources.

\*\*Copyright Compliance:\*\* Use only very short quotes (\<15 words)
when necessary, always in quotation marks with proper citations. Never
reproduce large content chunks.

\-\--

\*\*Dynamic Variables:\*\*

\- Defendant Name: \[TO BE PROVIDED\]

\- Case Number: \[TO BE PROVIDED\]

\- Filing Date: \[TO BE PROVIDED\]

### Key Prompt Design Principles:

**1. Source Hierarchy**: The prompt explicitly prioritizes legal sources
(appellate decisions, court records) over news articles, ensuring higher
accuracy and reliability.

**2. Systematic Search Strategy**: Rather than random searches, the
prompt follows a structured five-phase approach, from legal databases to
traditional media.

**3. Verification Requirements**: Multiple checkpoints prevent AI
hallucination by requiring source verification and cross-referencing.

**4. Structured Output**: JSON format ensures consistent data extraction
that can be easily processed and validated.

**5. Transparency**: The prompt documents search methodology even for
cases where no information is found, maintaining research integrity.

**6. Copyright Compliance**: Built-in restrictions prevent reproduction
of copyrighted content while allowing proper citation.

This prompt can be adapted for other jurisdictions by changing
location-specific terms (San Diego → your jurisdiction) and adjusting
local news sources and court systems. The core methodology remains
applicable across different legal research contexts.

### Understanding Effective AI Prompt Engineering

**Good prompts are built, not born.** Like debugging code, creating an
effective AI prompt requires multiple iterations of testing, identifying
failures, and systematic refinement. This legal extraction prompt went
through dozens of versions after we discovered the AI was:

-   Hallucinating case details when no sources existed

-   Prioritizing flashy news articles over authoritative court records

-   Missing appellate decisions that contained the most detailed facts

-   Failing to try alternative name spellings for difficult-to-find
    > cases

-   Producing inconsistent JSON output formats

Each failure became a new instruction. When the AI invented a fake
sentencing date, we added verification requirements. When it missed
obvious legal sources, we restructured the search phases to prioritize
legal databases first.

**The iterative process**: Test with known cases → identify what went
wrong → add specific instructions → test again. Modern AI tools can even
help you improve prompts - you can show Claude or GPT examples of bad
outputs and ask it to suggest prompt improvements. It\'s like having a
coding partner who helps debug your instructions.

This legal research prompt represents hours of iterative refinement,
turning a basic \"find information about this defendant\" request into a
systematic, reliable research methodology. The specificity isn\'t
accidental - it\'s the result of learning from every mistake the AI made
along the way.
