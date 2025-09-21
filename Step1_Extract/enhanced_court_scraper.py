#!/usr/bin/env python3
"""
enhanced_court_scraper.py - Step 1 of Juvenile/Emerging-Adult Bias Analysis

PURPOSE:
    Extracts defendant information from San Diego Superior Court records for bias analysis.
    This script implements Step 1 of a research workflow designed to identify potential 
    racial bias or improper sentencing disparities for juvenile (<18) and emerging adult 
    (18-26) defendants in homicide cases during Bonnie Dumanis's tenure as DA.

WHAT IT DOES:
    • Scrapes court docket data from San Diego Superior Court "Case Detail" pages
    • Extracts ALL defendants from multi-defendant cases (creates separate rows)
    • Handles multi-location cases (same case number in different court locations)
    • Captures: defendant names, birth years, filing dates, case locations, AKA flags
    • Outputs structured Excel file ready for Steps 2-4 (news matching, age analysis, bias detection)
    • Handles multiple court locations: North County, San Diego, East County, South County

HOW IT WORKS:
    1. Reads case numbers from input text file (one per line)
    2. Builds proper URLs for each court location (NC, SD, EC, SC)
    3. Uses authenticated session to access court records
    4. Handles both direct case matches and multi-location scenarios
    5. Parses HTML tables to extract defendant information
    6. Removes duplicate defendants (same person with name variations)
    7. Creates Excel output with auto-formatted columns

ARGUMENTS:
    python3 enhanced_court_scraper.py <JSESSIONID> <cases_file.txt>
    python3 enhanced_court_scraper.py <JSESSIONID> dummy.txt --testcase <CASE_ID>

    JSESSIONID: Authentication session ID for court website access
        • REQUIRED: San Diego Superior Court requires valid session for case detail access
        • HOW TO GET: 
            1. Open browser, go to https://courtindex.sdcourt.ca.gov/CISPublic/
            2. Perform any case search to establish session
            3. Open Developer Tools (F12) → Application/Storage → Cookies
            4. Find "JSESSIONID" cookie for courtindex.sdcourt.ca.gov domain
            5. Copy the Value (e.g., "A1B2C3D4E5F6G7H8I9J0.worker1")
        • WHY NEEDED: Court system blocks automated access without valid session
        • EXPIRES: Sessions timeout after ~30 minutes of inactivity
        • TIP: Get fresh JSESSIONID right before running large batches

    cases_file.txt: Text file containing case numbers (one per line)
        • FORMAT: Case numbers without "S" prefix (script tries both formats)
        • EXAMPLES: CN367913, CD270095, CE366120, CS290571
        • LOCATION CODES: CN/SCN=North County, CD/SCD=San Diego, CE/SCE=East County, CS/SCS=South County
        • NOTE: When using --testcase, this argument is ignored (can use any dummy filename)

    --testcase CASE_ID: Test mode - process only a single case
        • EXAMPLE: --testcase SCS179252
        • OUTPUT: testcase_<CASE_ID>_dob_extracted.xlsx
        • USE: Perfect for testing/debugging specific cases before batch processing

OUTPUT:
    <input_filename>_dob_extracted.xlsx
    • Excel file with one row per defendant (multi-defendant cases = multiple rows)
    • Columns: CaseNumber, DefendantName, DOB, DateFiled, CaseLocation,
               CrimeDate, AgeAtCrime, AgeBand, Sentence, DefendantRace,
               DefendantRole, TotalDefendants, DefendantIndex, AKA,
               Source_DocketURL, Source_ArticleURL, Notes, Special Circumstance?
    • Auto-formatted columns with source URLs for audit trail

DEPENDENCIES:
    pip install playwright pandas openpyxl
    playwright install chromium

EXAMPLE USAGE:
    # Process batch of cases from file
    python3 enhanced_court_scraper.py A1B2C3.worker1 san_diego_murders_batch1.txt
    → Creates: san_diego_murders_batch1_dob_extracted.xlsx
    
    # Test single case
    python3 enhanced_court_scraper.py A1B2C3.worker1 dummy.txt --testcase SCS179252
    → Creates: testcase_SCS179252_dob_extracted.xlsx

TROUBLESHOOTING:
    • "Session test failed" → Get fresh JSESSIONID from browser
    • "Case not found" → Verify case number format and court location
    • "Scraping error" → Court website may be down or blocking requests
    • Multiple defendants found → Normal, creates separate rows as designed

NEXT STEPS:
    After completion, proceed to Step 2: News article matching for crime dates and sentences
"""

# enhanced_court_scraper.py - Step 1 of Juvenile/Emerging-Adult Bias Analysis
# MODIFIED: Extracts ALL defendants as separate rows, outputs to Excel
# UPDATED: Added fallback logic for case number formats (original vs S-prefixed)
# UPDATED: Added multi-location case handling with data quality scoring
# UPDATED: Removed DAEra column and added final column "Special Circumstance?"

import sys
import os
import signal
import argparse
from datetime import datetime
from playwright.sync_api import sync_playwright
import pandas as pd
import openpyxl

# --- Globals used by the SIGINT handler; set properly inside main() ---
base_name: str = "output"
all_data: list = []
columns: list = []

def save_progress_and_exit(signum=None, frame=None):
    """Save collected data when interrupted with Ctrl-C"""
    print(f"\n\n  INTERRUPTED: Saving {len(all_data)} records collected so far...")
    if all_data:
        try:
            df = pd.DataFrame(all_data, columns=columns)
            timestamp = datetime.now().strftime("%H%M%S")
            interrupted_filename = f"{base_name}_dob_extracted_PARTIAL_{timestamp}.xlsx"
            with pd.ExcelWriter(interrupted_filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Court_Data_Partial', index=False)
                worksheet = writer.sheets['Court_Data_Partial']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            print(f"💾 PARTIAL DATA SAVED: {interrupted_filename}")
            print(f"📊 Records preserved: {len(all_data)}")
            print(f"🔄 To continue: Remove completed cases from input file and re-run")
        except Exception as e:
            print(f"❌ Error saving partial data: {e}")
            try:
                timestamp = datetime.now().strftime("%H%M%S")
                csv_filename = f"{base_name}_dob_extracted_PARTIAL_{timestamp}.csv"
                df.to_csv(csv_filename, index=False)
                print(f"💾 FALLBACK: Saved as CSV: {csv_filename}")
            except Exception as csv_error:
                print(f"❌ Failed to save even as CSV: {csv_error}")
    else:
        print("💭 No data collected yet - nothing to save")
    print("👋 Exiting gracefully...")
    sys.exit(0)

def search_case_with_form(page, case_number, try_with_s_prefix=False):
    """Use JavaScript form submission to search for cases (maintains session)"""
    search_case = case_number
    if try_with_s_prefix and not case_number.startswith("S"):
        search_case = "S" + case_number
    try:
        print(f"      Submitting form search for: {search_case}")
        page.goto("https://courtindex.sdcourt.ca.gov/CISPublic/casesearch",
                  wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(1000)
        search_script = f"""
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/CISPublic/viewcase';
        const fields = [
            ['caseType', 'A'],
            ['site', 'A'], 
            ['casenum', '{search_case}'],
            ['page', '1']
        ];
        fields.forEach(([name, value]) => {{
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = name;
            input.value = value;
            form.appendChild(input);
        }});
        document.body.appendChild(form);
        form.submit();
        """
        page.evaluate(search_script)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        return True
    except Exception as e:
        print(f"      ❌ Error in form submission: {e}")
        return False

def check_for_multiple_locations(page):
    """Check if we got a 'View Case Number Matches' page with multiple locations"""
    try:
        page_text = page.locator("body").text_content()
        if "View Case Number Matches" in page_text and "Select the Case Number below" in page_text:
            if "No selections matching your search criteria were found" in page_text:
                print(f"      ❌ Explicit 'no results' message found")
                return None
            print(f"      ✅ Multi-location page detected, parsing results...")
            matches = []
            all_links = page.locator("a")
            for i in range(all_links.count()):
                link = all_links.nth(i)
                href = link.get_attribute("href")
                if href and "casedetailr" in href and "casenum=" in href:
                    try:
                        import urllib.parse
                        parsed_url = urllib.parse.urlparse(href)
                        params = urllib.parse.parse_qs(parsed_url.query)
                        site_code = params.get('casesite', [''])[0]
                        site_map = {'NC': 'North County','SD': 'San Diego','EC': 'East County','SC': 'South County','SB': 'South Bay'}
                        location_name = site_map.get(site_code, site_code)
                        parent_row = link.locator("xpath=ancestor::tr[1]")
                        case_type = date_filed = plaintiff = defendant = ""
                        if parent_row.count() > 0:
                            cells = parent_row.locator("td")
                            if cells.count() >= 6:
                                case_type = cells.nth(2).text_content().strip()
                                date_filed = cells.nth(3).text_content().strip()
                                plaintiff = cells.nth(4).text_content().strip()
                                defendant = cells.nth(5).text_content().strip()
                        if href.startswith("/"):
                            href = f"https://courtindex.sdcourt.ca.gov{href}"
                        matches.append({
                            "location": location_name,
                            "url": href,
                            "case_type": case_type,
                            "date_filed": date_filed,
                            "defendant": defendant
                        })
                    except Exception as parse_error:
                        print(f"         ⚠️  Error parsing link {href}: {parse_error}")
                        continue
            if matches:
                print(f"      🎯 Successfully parsed {len(matches)} location(s)")
                return matches
            print(f"      ❌ No valid case links found on multi-location page")
            return None
        return None
    except Exception as e:
        print(f"   ⚠️  Error checking for multiple locations: {e}")
        return None

def extract_case_info(page, field_name):
    """Extract specific case information from the page"""
    try:
        all_text = page.locator("body").text_content()
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        for i, line in enumerate(lines):
            if field_name in line and i + 1 < len(lines):
                return lines[i + 1]
        return ""
    except:
        return ""

def extract_defendants_from_page(page):
    """Extract defendants from current page"""
    all_defendants = []
    try:
        tables = page.locator("table")
        for table_idx in range(tables.count()):
            table = tables.nth(table_idx)
            table_text = table.text_content()
            if "Defendant" in table_text and ("Last Name" in table_text or "First Name" in table_text):
                rows = table.locator("tr")
                for row_idx in range(rows.count()):
                    row = rows.nth(row_idx)
                    cells = row.locator("td")
                    if cells.count() >= 3:
                        first_cell = cells.nth(0).text_content().strip()
                        second_cell = cells.nth(1).text_content().strip()
                        third_cell = cells.nth(2).text_content().strip()
                        fourth_cell = cells.nth(3).text_content().strip() if cells.count() > 3 else ""
                        fifth_cell = cells.nth(4).text_content().strip() if cells.count() > 4 else ""
                        if first_cell in ["Last Name", "Defendant"] or "Name" in first_cell:
                            continue
                        if first_cell and first_cell.isupper() and len(first_cell) > 1:
                            defendant_info = {
                                "LastName": first_cell,
                                "FirstName": second_cell,
                                "BirthYear": third_cell if third_cell.isdigit() and len(third_cell) == 4 else "",
                                "AKA": fourth_cell if fourth_cell in ["Y", "N", "Yes", "No"] else "",
                                "DANumber": fifth_cell if cells.count() > 4 else ""
                            }
                            all_defendants.append(defendant_info)
                break
        return all_defendants
    except Exception as e:
        print(f"      ⚠️  Error extracting defendants: {e}")
        return []

def calculate_data_quality_score(defendants):
    """Score defendant data quality - higher is better"""
    if not defendants:
        return 0
    score = 0
    for defendant in defendants:
        if defendant.get('BirthYear') and defendant['BirthYear'].isdigit():
            score += 10
        if defendant.get('FirstName') and defendant.get('LastName'):
            score += 5
        if defendant.get('DANumber'):
            score += 2
        if not defendant.get('BirthYear'):
            score -= 5
    return score

def extract_defendants_from_multi_location_case(page, case_number, attempted_urls):
    """Handle cases that exist in multiple court locations"""
    print(f"   🔍 Found multi-location case - checking all locations...")
    location_matches = check_for_multiple_locations(page)
    if not location_matches:
        print(f"   ❌ Could not parse multiple locations")
        return [], {}, None
    print(f"   📍 Found {len(location_matches)} locations: {[m['location'] for m in location_matches]}")
    all_location_data = []
    best_location_data = None
    best_location_score = 0
    for idx, location_match in enumerate(location_matches, 1):
        location = location_match["location"]
        location_url = location_match["url"]
        print(f"      → Checking location {idx}/{len(location_matches)}: {location}")
        attempted_urls.append(location_url)
        try:
            page.goto(location_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            location_defendants = extract_defendants_from_page(page)
            if location_defendants:
                score = calculate_data_quality_score(location_defendants)
                location_data = {
                    "location": location,
                    "url": location_url,
                    "defendants": location_defendants,
                    "score": score,
                    "page_content": {
                        "case_title": extract_case_info(page, "Case Title:"),
                        "case_location": extract_case_info(page, "Case Location:"),
                        "date_filed": extract_case_info(page, "Date Filed:"),
                        "case_type": extract_case_info(page, "Case Type:")
                    }
                }
                all_location_data.append(location_data)
                print(f"         ✅ {len(location_defendants)} defendants found (quality score: {score})")
                if score > best_location_score:
                    best_location_score = score
                    best_location_data = location_data
            else:
                print(f"         ❌ No defendants found at {location}")
        except Exception as e:
            print(f"         ❌ Error accessing {location}: {e}")
    if best_location_data:
        print(f"   🏆 Using best quality data from: {best_location_data['location']} (score: {best_location_score})")
        for defendant in best_location_data['defendants']:
            if 'notes' not in defendant:
                defendant['notes'] = []
            defendant['notes'].append(f"Multi-location case: found in {len(all_location_data)} locations")
            defendant['notes'].append(f"Using data from {best_location_data['location']} (highest quality)")
            other_locations = [loc['location'] for loc in all_location_data if loc['location'] != best_location_data['location']]
            if other_locations:
                defendant['notes'].append(f"Also found in: {', '.join(other_locations)}")
        return best_location_data['defendants'], best_location_data['page_content'], best_location_data['url']
    else:
        print(f"   ❌ No usable defendant data found in any location")
        return [], {}, None

def check_if_case_found(page):
    """Check if the case was found - now handles multiple location scenarios"""
    try:
        title = page.title()
        page_text = page.locator("body").text_content()
        if "No selections matching your search criteria were found" in page_text:
            print(f"      ❌ No results found")
            return False
        if "View Case Number Matches" in page_text and "Select the Case Number below" in page_text:
            if "No selections matching your search criteria were found" in page_text:
                print(f"      ❌ Multi-location page but no results")
                return False
            case_links = page.locator("a[href*='casedetailr']")
            if case_links.count() > 0:
                print(f"      ✅ Multi-location page with {case_links.count()} result(s)")
                return "multiple_locations"
            else:
                print(f"      ❌ Multi-location page but no case links found")
                return False
        if "Error" in title:
            return False
        if "Case Title:" in page_text and "Defendant" in page_text:
            print(f"      ✅ Direct case detail page found")
            return True
        print(f"      ❌ Unknown page type")
        return False
    except Exception as e:
        print(f"      ⚠️  Error checking case status: {e}")
        return False

def format_dob(birth_year):
    """Keep birth year as-is - don't add fake precision"""
    if birth_year and birth_year.isdigit() and len(birth_year) == 4:
        return birth_year
    return ""

def format_date_filed(date_str):
    """Standardize date format"""
    if not date_str:
        return ""
    try:
        if "/" in date_str:
            month, day, year = date_str.split("/")
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    except:
        pass
    return date_str

def is_duplicate_defendant(defendant, seen_defendants):
    """Check if this defendant is a duplicate of one already processed"""
    current_key = (
        defendant['LastName'].upper(),
        defendant['FirstName'].upper(),
        defendant['BirthYear']
    )
    for seen in seen_defendants:
        seen_key = (
            seen['LastName'].upper(),
            seen['FirstName'].upper(),
            seen['BirthYear']
        )
        if current_key == seen_key:
            return True
        if (current_key[2] == seen_key[2] and current_key[0] == seen_key[0]):
            current_first = current_key[1].replace(" ", "")
            seen_first = seen_key[1].replace(" ", "")
            if current_first in seen_first or seen_first in current_first:
                return True
    return False

def main():
    global base_name, all_data, columns

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Enhanced Court Scraper - Step 1 of Juvenile/Emerging-Adult Bias Analysis')
    parser.add_argument('session_id', help='JSESSIONID for court website authentication')
    parser.add_argument('cases_file', help='Text file with case numbers (one per line) or dummy filename when using --testcase')
    parser.add_argument('--testcase', help='Test single case ID instead of processing file', metavar='CASE_ID')
    args = parser.parse_args()

    session_id = args.session_id
    cases_file = args.cases_file
    test_case = args.testcase

    # Output paths and mode
    if test_case:
        print(f"🧪 TEST MODE: Running single case {test_case}")
        CASES = [test_case]
        out_xlsx = f"testcase_{test_case}_dob_extracted.xlsx"
        base_name = f"testcase_{test_case}"
    else:
        base_name = os.path.splitext(cases_file)[0]
        out_xlsx = f"{base_name}_dob_extracted.xlsx"

    # Columns and data store
    all_data = []
    columns = [
        "CaseNumber", "DefendantName", "DOB", "DateFiled", "CaseLocation", 
        "CrimeDate", "AgeAtCrime", "AgeBand", "Sentence", "DefendantRace", 
        "DefendantRole", "TotalDefendants", "DefendantIndex", "AKA",
        "Source_DocketURL", "Source_ArticleURL", "Notes", "Special Circumstance?"
    ]

    # SIGINT handler
    signal.signal(signal.SIGINT, save_progress_and_exit)

    # Load cases if not in test mode
    if not test_case:
        try:
            with open(cases_file, 'r') as f:
                CASES = [line.strip() for line in f if line.strip()]
            print(f"📂 Loaded {len(CASES)} cases from {cases_file}")
        except FileNotFoundError:
            print(f"❌ Error: Could not find cases file '{cases_file}'")
            print("Create a text file with one case number per line, example:\nCN367913\nCN367895\nCD270095")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error reading cases file: {e}")
            sys.exit(1)
    else:
        print(f"🧪 Testing single case: {test_case}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_cookies([{
            "name": "JSESSIONID",
            "value": session_id,
            "domain": "courtindex.sdcourt.ca.gov",
            "path": "/"
        }])
        page = context.new_page()

        print("🏛️  San Diego Superior Court - Juvenile/Emerging-Adult Bias Analysis")
        print("📋 Step 1: Court Docket Data Collection (ALL DEFENDANTS)")
        print(f"📄 Output: {out_xlsx}")
        if not test_case:
            print("⚠️  Press Ctrl-C anytime to save partial progress and exit gracefully")
        print("🔄 NEW: Automatic fallback between original and S-prefixed case formats")
        print("🎯 NEW: Multi-location case handling with data quality scoring")
        print("="*60)

        print("Testing session...")
        try:
            page.goto("https://courtindex.sdcourt.ca.gov/CISPublic/", timeout=15000)
            print(f"✅ Session active - {page.title()}")
        except Exception as e:
            print(f"⚠️  Session test failed: {e}")

        for idx, raw in enumerate(CASES, 1):
            print(f"\n→ [{idx}/{len(CASES)}] Fetching {raw}")
            case_found = False
            successful_case = None
            attempted_urls = []

            try:
                print(f"   Trying original format: {raw}")
                if search_case_with_form(page, raw, try_with_s_prefix=False):
                    attempted_urls.append(f"Form search: {raw}")
                    case_status = check_if_case_found(page)
                    if case_status is True:
                        print(f"   ✅ Found with original format (direct match)")
                        case_found = True
                        successful_case = raw
                    elif case_status == "multiple_locations":
                        print(f"   🔍 Found with original format (multiple locations)")
                        case_found = "multiple_locations"
                        successful_case = raw
                    else:
                        print(f"   ❌ Not found with original format, trying S-prefix...")
                        s_prefixed_case = "S" + raw if not raw.startswith("S") else raw
                        print(f"   Trying S-prefixed format: {s_prefixed_case}")
                        if search_case_with_form(page, raw, try_with_s_prefix=True):
                            attempted_urls.append(f"Form search: {s_prefixed_case}")
                            case_status_s = check_if_case_found(page)
                            if case_status_s is True:
                                print(f"   ✅ Found with S-prefixed format (direct match)")
                                case_found = True
                                successful_case = s_prefixed_case
                            elif case_status_s == "multiple_locations":
                                print(f"   🔍 Found with S-prefixed format (multiple locations)")
                                case_found = "multiple_locations"
                                successful_case = s_prefixed_case
                            else:
                                print(f"   ❌ Not found with either format")
                else:
                    print(f"   ❌ Form submission failed")

                if not case_found:
                    print(f"   ❌ Case {raw} not found in either format")
                    all_data.append([
                        raw, "", "", "", "", "", "", "", "", "",
                        "", "", "", "", " | ".join(attempted_urls),
                        "", "Case not found in court system (tried both formats)", ""
                    ])
                    continue

                if case_found == "multiple_locations":
                    defendants_data, page_content, final_url = extract_defendants_from_multi_location_case(
                        page, successful_case, attempted_urls
                    )
                    if defendants_data:
                        case_location = page_content.get("case_location", "")
                        date_filed = page_content.get("date_filed", "")
                        successful_url = final_url
                        unique_defendants = []
                        for defendant in defendants_data:
                            defendant_info = {
                                "LastName": defendant["LastName"],
                                "FirstName": defendant["FirstName"],
                                "BirthYear": defendant["BirthYear"],
                                "AKA": defendant["AKA"],
                                "DANumber": defendant["DANumber"],
                                "additional_notes": defendant.get("notes", [])
                            }
                            unique_defendants.append(defendant_info)
                    else:
                        print(f"   ❌ No defendants found in any location")
                        all_data.append([
                            successful_case, "", "", "", "", "", "", "", "", "",
                            "", "", "", "", " | ".join(attempted_urls), "",
                            "Multi-location case but no defendants found", ""
                        ])
                        continue
                else:
                    case_location = ""
                    date_filed = ""
                    successful_url = page.url
                    all_text = page.locator("body").text_content()
                    lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                    for i, line in enumerate(lines):
                        if "Case Location:" in line and i + 1 < len(lines):
                            case_location = lines[i + 1]
                        elif "Date Filed:" in line and i + 1 < len(lines):
                            date_filed = lines[i + 1]
                    all_defendants = extract_defendants_from_page(page)
                    unique_defendants = []
                    for defendant in all_defendants:
                        if not is_duplicate_defendant(defendant, unique_defendants):
                            unique_defendants.append(defendant)

                formatted_date_filed = format_date_filed(date_filed)
                total_defendants = len(unique_defendants)
                print(f"   📋 Found {total_defendants} unique defendant(s)")

                if unique_defendants:
                    for def_idx, defendant_data in enumerate(unique_defendants, 1):
                        full_name = f"{defendant_data['FirstName']} {defendant_data['LastName']}".strip()
                        formatted_dob = format_dob(defendant_data["BirthYear"])
                        defendant_role = "Primary" if def_idx == 1 else "Co-defendant"

                        notes = []
                        if total_defendants > 1:
                            notes.append(f"Multi-defendant case ({total_defendants} total)")
                        if defendant_data["AKA"] == "Y":
                            notes.append("Has AKA/alias names")
                        if not defendant_data["BirthYear"]:
                            notes.append("DOB missing from docket; need article age")
                        else:
                            notes.append("DOB=birth year only (court data)")
                        if not date_filed:
                            notes.append("DateFiled missing")

                        format_used = "S-prefixed" if successful_case.startswith("S") and not raw.startswith("S") else "original"
                        notes.append(f"Found using {format_used} format via form search")

                        if hasattr(defendant_data, 'additional_notes') and defendant_data.get('additional_notes'):
                            notes.extend(defendant_data['additional_notes'])

                        row_data = [
                            successful_case,         # CaseNumber
                            full_name,               # DefendantName  
                            formatted_dob,           # DOB
                            formatted_date_filed,    # DateFiled
                            case_location,           # CaseLocation
                            "", "", "", "", "",      # CrimeDate, AgeAtCrime, AgeBand, Sentence, DefendantRace
                            defendant_role,          # DefendantRole
                            total_defendants,        # TotalDefendants
                            def_idx,                 # DefendantIndex
                            defendant_data["AKA"],   # AKA
                            successful_url,          # Source_DocketURL
                            "",                      # Source_ArticleURL
                            "; ".join(notes),        # Notes
                            ""                       # Special Circumstance?
                        ]
                        print(f"      #{def_idx}: {full_name} (Born: {defendant_data['BirthYear'] or 'Unknown'})")
                        all_data.append(row_data)
                else:
                    print(f"   ⚠️  No defendants extracted")
                    all_data.append([
                        successful_case, "", "", formatted_date_filed, case_location, "", "", "", "", "",
                        "", "", "", "", successful_url, "", "No defendants found in docket", ""
                    ])

                print(f"      Filed: {date_filed or 'Unknown'} | Location: {case_location or 'Unknown'}")

            except Exception as e:
                print(f"   ❌ Error processing {raw}: {e}")
                all_data.append([
                    raw, "", "", "", "", "", "", "", "", "",
                    "", "", "", "", " | ".join(attempted_urls) if attempted_urls else "Form submission failed",
                    "", f"Scraping error: {str(e)}", ""
                ])

        browser.close()

        print(f"\n📊 Creating Excel file with {len(all_data)} rows...")
        try:
            df = pd.DataFrame(all_data, columns=columns)
            with pd.ExcelWriter(out_xlsx, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Court_Data', index=False)
                worksheet = writer.sheets['Court_Data']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            print(f"🎯 Step 1 Complete!")
            print(f"📊 Data exported to: {out_xlsx}")
            if test_case:
                print(f"🧪 TEST COMPLETE: Single case {test_case} processed")
            else:
                print(f"🔢 Note: Multi-defendant cases create multiple rows (one per defendant)")
            print(f"🔄 NEW: Form-based search with automatic fallback handling")
            print(f"🎯 NEW: Multi-location cases automatically resolved with best data quality")
            if not test_case:
                print(f"🔜 Next: Run Steps 2-4 (news search, age calculation, bias analysis)")
            print("\nReady for your bias analysis pipeline! 🏛️⚖️")
        except Exception as e:
            print(f"❌ Error creating Excel file: {e}")
            save_progress_and_exit()

if __name__ == "__main__":
    main()
