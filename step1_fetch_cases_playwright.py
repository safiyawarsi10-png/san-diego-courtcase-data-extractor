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
    • Columns: CaseNumber, DefendantName, DOB, DateFiled, CaseLocation, DefendantRole, 
               TotalDefendants, DefendantIndex, AKA, plus placeholders for Steps 2-4
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

import sys
import os
import signal
import argparse
from datetime import datetime
from playwright.sync_api import sync_playwright
import pandas as pd
import openpyxl

# Parse command line arguments
parser = argparse.ArgumentParser(description='Enhanced Court Scraper - Step 1 of Juvenile/Emerging-Adult Bias Analysis')
parser.add_argument('session_id', help='JSESSIONID for court website authentication')
parser.add_argument('cases_file', help='Text file with case numbers (one per line) or dummy filename when using --testcase')
parser.add_argument('--testcase', help='Test single case ID instead of processing file', metavar='CASE_ID')

args = parser.parse_args()

session_id = args.session_id
cases_file = args.cases_file
test_case = args.testcase

# Handle test case mode
if test_case:
    print(f"🧪 TEST MODE: Running single case {test_case}")
    CASES = [test_case]
    # Generate output filename for test case
    out_xlsx = f"testcase_{test_case}_dob_extracted.xlsx"
    base_name = f"testcase_{test_case}"
else:
    # Generate output Excel filename from input file
    base_name = os.path.splitext(cases_file)[0]  # Remove .txt extension
    out_xlsx = f"{base_name}_dob_extracted.xlsx"

# Global variables for interrupt handling
all_data = []
columns = [
    "CaseNumber", "DefendantName", "DOB", "DateFiled", "CaseLocation", 
    "CrimeDate", "AgeAtCrime", "AgeBand", "Sentence", "DefendantRace", 
    "DAEra", "DefendantRole", "TotalDefendants", "DefendantIndex", "AKA",
    "Source_DocketURL", "Source_ArticleURL", "Notes"
]

def save_progress_and_exit(signum=None, frame=None):
    """Save collected data when interrupted with Ctrl-C"""
    print(f"\n\n⚠️  INTERRUPTED: Saving {len(all_data)} records collected so far...")
    
    if all_data:
        try:
            # Create DataFrame and export to Excel
            df = pd.DataFrame(all_data, columns=columns)
            
            # Add timestamp to filename to avoid overwriting complete runs
            timestamp = datetime.now().strftime("%H%M%S")
            interrupted_filename = f"{base_name}_dob_extracted_PARTIAL_{timestamp}.xlsx"
            
            # Create Excel file with formatting
            with pd.ExcelWriter(interrupted_filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Court_Data_Partial', index=False)
                
                # Get the workbook and worksheet for formatting
                workbook = writer.book
                worksheet = writer.sheets['Court_Data_Partial']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"💾 PARTIAL DATA SAVED: {interrupted_filename}")
            print(f"📊 Records preserved: {len(all_data)}")
            print(f"🔄 To continue: Remove completed cases from input file and re-run")
            
        except Exception as e:
            print(f"❌ Error saving partial data: {e}")
            # Fallback: save as CSV if Excel fails
            try:
                csv_filename = f"{base_name}_dob_extracted_PARTIAL_{timestamp}.csv"
                df.to_csv(csv_filename, index=False)
                print(f"💾 FALLBACK: Saved as CSV: {csv_filename}")
            except Exception as csv_error:
                print(f"❌ Failed to save even as CSV: {csv_error}")
    else:
        print("💭 No data collected yet - nothing to save")
    
    print("👋 Exiting gracefully...")
    sys.exit(0)

# Set up signal handler for Ctrl-C
signal.signal(signal.SIGINT, save_progress_and_exit)

# Read cases from file (skip if in test mode)
if not test_case:
    try:
        with open(cases_file, 'r') as f:
            CASES = [line.strip() for line in f if line.strip()]
        print(f"📂 Loaded {len(CASES)} cases from {cases_file}")
    except FileNotFoundError:
        print(f"❌ Error: Could not find cases file '{cases_file}'")
        print("Create a text file with one case number per line, example:")
        print("CN367913")
        print("CN367895") 
        print("CD270095")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading cases file: {e}")
        sys.exit(1)
else:
    print(f"🧪 Testing single case: {test_case}")

def search_case_with_form(page, case_number, try_with_s_prefix=False):
    """Use JavaScript form submission to search for cases (maintains session)"""
    
    search_case = case_number
    if try_with_s_prefix and not case_number.startswith("S"):
        search_case = "S" + case_number
    
    try:
        print(f"      Submitting form search for: {search_case}")
        
        # Navigate to search page first to get proper session context
        page.goto("https://courtindex.sdcourt.ca.gov/CISPublic/casesearch", 
                 wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(1000)
        
        # Submit the search via JavaScript to maintain session
        search_script = f"""
        // Create and submit form programmatically
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/CISPublic/viewcase';
        
        // Add form fields
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
        
        // Add to page and submit
        document.body.appendChild(form);
        form.submit();
        """
        
        page.evaluate(search_script)
        
        # Wait for navigation to results page
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
        
        # Check if this is a multiple matches page
        if "View Case Number Matches" in page_text and "Select the Case Number below" in page_text:
            # Check for explicit no results first
            if "No selections matching your search criteria were found" in page_text:
                print(f"      ❌ Explicit 'no results' message found")
                return None
                
            print(f"      ✅ Multi-location page detected, parsing results...")
            
            # Extract all case location links
            matches = []
            
            # Debug: Print page content to understand structure
            print(f"      🔍 Scanning page for case links...")
            
            # Look for links that contain case details
            all_links = page.locator("a")
            for i in range(all_links.count()):
                link = all_links.nth(i)
                href = link.get_attribute("href")
                link_text = link.text_content().strip()
                
                # Look for case detail links
                if href and "casedetailr" in href and "casenum=" in href:
                    print(f"      → Found case link: {link_text} → {href}")
                    
                    # Extract case number and site from URL
                    try:
                        # Parse URL parameters
                        import urllib.parse
                        parsed_url = urllib.parse.urlparse(href)
                        params = urllib.parse.parse_qs(parsed_url.query)
                        
                        case_num = params.get('casenum', [''])[0]
                        site_code = params.get('casesite', [''])[0]
                        
                        # Map site codes to readable names
                        site_map = {
                            'NC': 'North County',
                            'SD': 'San Diego', 
                            'EC': 'East County',
                            'SC': 'South County',
                            'SB': 'South Bay'  # Sometimes used instead of SC
                        }
                        
                        location_name = site_map.get(site_code, site_code)
                        
                        # Get the parent row to extract other details
                        parent_row = link.locator("xpath=ancestor::tr[1]")
                        if parent_row.count() > 0:
                            cells = parent_row.locator("td")
                            
                            # Extract data from table cells
                            case_type = ""
                            date_filed = ""
                            plaintiff = ""
                            defendant = ""
                            
                            if cells.count() >= 6:
                                case_type = cells.nth(2).text_content().strip()
                                date_filed = cells.nth(3).text_content().strip()
                                plaintiff = cells.nth(4).text_content().strip()
                                defendant = cells.nth(5).text_content().strip()
                            
                            # Convert relative URL to absolute
                            if href.startswith("/"):
                                href = f"https://courtindex.sdcourt.ca.gov{href}"
                            
                            match_info = {
                                "location": location_name,
                                "url": href,
                                "case_type": case_type,
                                "date_filed": date_filed,
                                "defendant": defendant
                            }
                            
                            matches.append(match_info)
                            print(f"         ✅ Parsed: {location_name} - {defendant}")
                        
                    except Exception as parse_error:
                        print(f"         ⚠️  Error parsing link {href}: {parse_error}")
                        continue
            
            if matches:
                print(f"      🎯 Successfully parsed {len(matches)} location(s)")
                return matches
            else:
                print(f"      ❌ No valid case links found on multi-location page")
                
                # Debug: Show what we found instead
                print(f"      🔍 Debug - All links on page:")
                for i in range(min(all_links.count(), 10)):  # Show first 10 links
                    link = all_links.nth(i)
                    href = link.get_attribute("href") or "no-href"
                    text = link.text_content().strip()[:50]
                    print(f"         Link {i}: '{text}' → {href}")
                
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
    """Extract defendants from current page - separated for reuse"""
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
                        
                        # Skip headers
                        if first_cell in ["Last Name", "Defendant"] or "Name" in first_cell:
                            continue
                        
                        # Extract data row
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
        # Award points for having birth year data
        if defendant.get('BirthYear') and defendant['BirthYear'].isdigit():
            score += 10
        
        # Award points for complete names
        if defendant.get('FirstName') and defendant.get('LastName'):
            score += 5
        
        # Award points for having DA numbers
        if defendant.get('DANumber'):
            score += 2
        
        # Deduct points for missing critical data
        if not defendant.get('BirthYear'):
            score -= 5
    
    return score

def extract_defendants_from_multi_location_case(page, case_number, attempted_urls):
    """Handle cases that exist in multiple court locations"""
    
    print(f"   🔍 Found multi-location case - checking all locations...")
    
    # Check for multiple location matches
    location_matches = check_for_multiple_locations(page)
    
    if not location_matches:
        print(f"   ❌ Could not parse multiple locations")
        return [], {}, None
    
    print(f"   📍 Found {len(location_matches)} locations: {[m['location'] for m in location_matches]}")
    
    all_location_data = []
    best_location_data = None
    best_location_score = 0
    
    # Try each location and score the data quality
    for idx, location_match in enumerate(location_matches, 1):
        location = location_match["location"]
        location_url = location_match["url"]
        
        print(f"      → Checking location {idx}/{len(location_matches)}: {location}")
        attempted_urls.append(location_url)
        
        try:
            page.goto(location_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            
            # Extract defendants from this location
            location_defendants = extract_defendants_from_page(page)
            
            if location_defendants:
                # Score this location's data quality
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
                
                # Track the best quality location
                if score > best_location_score:
                    best_location_score = score
                    best_location_data = location_data
            else:
                print(f"         ❌ No defendants found at {location}")
                
        except Exception as e:
            print(f"         ❌ Error accessing {location}: {e}")
    
    # Use the highest quality location data
    if best_location_data:
        print(f"   🏆 Using best quality data from: {best_location_data['location']} (score: {best_location_score})")
        
        # Add notes about multiple locations
        for defendant in best_location_data['defendants']:
            if 'notes' not in defendant:
                defendant['notes'] = []
            defendant['notes'].append(f"Multi-location case: found in {len(all_location_data)} locations")
            defendant['notes'].append(f"Using data from {best_location_data['location']} (highest quality)")
            
            # Add info about other locations
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
        
        # Check for the specific "no matches" message FIRST
        if "No selections matching your search criteria were found" in page_text:
            print(f"      ❌ No results found")
            return False
        
        # Check for multiple location matches (this is actually a SUCCESS case)
        if "View Case Number Matches" in page_text and "Select the Case Number below" in page_text:
            # Double check that we actually have results, not just the page structure
            if "No selections matching your search criteria were found" in page_text:
                print(f"      ❌ Multi-location page but no results")
                return False
            
            # Look for actual case links to confirm results exist
            case_links = page.locator("a[href*='casedetailr']")
            if case_links.count() > 0:
                print(f"      ✅ Multi-location page with {case_links.count()} result(s)")
                return "multiple_locations"
            else:
                print(f"      ❌ Multi-location page but no case links found")
                return False
            
        # Check for other error indicators
        if "Error" in title:
            return False
            
        # Check for positive indicators (direct case detail page)
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
        return birth_year  # Just return YYYY, not YYYY-01-01
    return ""

def format_date_filed(date_str):
    """Standardize date format"""
    if not date_str:
        return ""
    
    try:
        # Convert MM/DD/YYYY to YYYY-MM-DD
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
        
        # Exact match
        if current_key == seen_key:
            return True
            
        # Same person with different name variations
        if (current_key[2] == seen_key[2] and  # Same birth year
            current_key[0] == seen_key[0]):    # Same last name
            # Check if first names are variations (e.g., "DANIELLE N" vs "DANIELLE NADINE")
            current_first = current_key[1].replace(" ", "")
            seen_first = seen_key[1].replace(" ", "")
            if current_first in seen_first or seen_first in current_first:
                return True
    
    return False

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
    if test_case:
        print(f"🧪 TEST MODE: Single case {test_case}")
        print(f"📄 Output: {out_xlsx}")
    else:
        print(f"📄 Output: {out_xlsx}")
        print("⚠️  Press Ctrl-C anytime to save partial progress and exit gracefully")
    print("🔄 NEW: Automatic fallback between original and S-prefixed case formats")
    print("🎯 NEW: Multi-location case handling with data quality scoring")
    print("="*60)
    
    # Test session
    print("Testing session...")
    try:
        page.goto("https://courtindex.sdcourt.ca.gov/CISPublic/", timeout=15000)
        print(f"✅ Session active - {page.title()}")
    except Exception as e:
        print(f"⚠️  Session test failed: {e}")

    # Use global all_data for interrupt handling
    for idx, raw in enumerate(CASES, 1):
        print(f"\n→ [{idx}/{len(CASES)}] Fetching {raw}")
        
        case_found = False
        successful_case = None
        attempted_urls = []
        
        try:
            # First attempt: try original format
            print(f"   Trying original format: {raw}")
            if search_case_with_form(page, raw, try_with_s_prefix=False):
                attempted_urls.append(f"Form search: {raw}")
                case_status = check_if_case_found(page)
                
                if case_status == True:
                    print(f"   ✅ Found with original format (direct match)")
                    case_found = True
                    successful_case = raw
                elif case_status == "multiple_locations":
                    print(f"   🔍 Found with original format (multiple locations)")
                    case_found = "multiple_locations"
                    successful_case = raw
                else:
                    print(f"   ❌ Not found with original format, trying S-prefix...")
                    
                    # Second attempt: try with S prefix
                    s_prefixed_case = "S" + raw if not raw.startswith("S") else raw
                    print(f"   Trying S-prefixed format: {s_prefixed_case}")
                    
                    if search_case_with_form(page, raw, try_with_s_prefix=True):
                        attempted_urls.append(f"Form search: {s_prefixed_case}")
                        case_status_s = check_if_case_found(page)
                        
                        if case_status_s == True:
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
                    raw, "", "", "", "", "", "", "", "", "", "Bonnie Dumanis",
                    "", "", "", "", " | ".join(attempted_urls), 
                    "", "Case not found in court system (tried both formats)"
                ])
                continue
            
            # Handle multi-location cases
            if case_found == "multiple_locations":
                defendants_data, page_content, final_url = extract_defendants_from_multi_location_case(
                    page, successful_case, attempted_urls
                )
                
                if defendants_data:
                    # Use the multi-location extracted data
                    case_title = page_content.get("case_title", "")
                    case_location = page_content.get("case_location", "")
                    case_type = page_content.get("case_type", "")
                    date_filed = page_content.get("date_filed", "")
                    successful_url = final_url
                    
                    # Convert to expected format
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
                        successful_case, "", "", "", "", "", "", "", "", "", "Bonnie Dumanis",
                        "", "", "", "", " | ".join(attempted_urls), "", "Multi-location case but no defendants found"
                    ])
                    continue
            else:
                # Handle direct case match (existing logic)
                case_title = ""
                case_location = ""
                case_type = ""
                date_filed = ""
                successful_url = page.url  # Current page URL
                
                # Parse page text for key-value pairs
                all_text = page.locator("body").text_content()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                for i, line in enumerate(lines):
                    if "Case Title:" in line and i + 1 < len(lines):
                        case_title = lines[i + 1] if "DEFENDANT" in lines[i + 1] else case_title
                    elif "Case Location:" in line and i + 1 < len(lines):
                        case_location = lines[i + 1]
                    elif "Case Type:" in line and i + 1 < len(lines):
                        case_type = lines[i + 1]
                    elif "Date Filed:" in line and i + 1 < len(lines):
                        date_filed = lines[i + 1]
                
                # Extract ALL defendants from table (existing logic)
                all_defendants = extract_defendants_from_page(page)
                
                # Remove duplicates while preserving order
                unique_defendants = []
                for defendant in all_defendants:
                    if not is_duplicate_defendant(defendant, unique_defendants):
                        unique_defendants.append(defendant)
            
            # Format shared case data
            formatted_date_filed = format_date_filed(date_filed)
            total_defendants = len(unique_defendants)
            
            print(f"   📋 Found {total_defendants} unique defendant(s)")
            
            # Create one row per defendant
            if unique_defendants:
                for def_idx, defendant_data in enumerate(unique_defendants, 1):
                    # Build defendant name
                    full_name = f"{defendant_data['FirstName']} {defendant_data['LastName']}".strip()
                    
                    # Format DOB
                    formatted_dob = format_dob(defendant_data["BirthYear"])
                    
                    # Determine defendant role
                    defendant_role = "Primary" if def_idx == 1 else "Co-defendant"
                    
                    # Create notes for missing data and data quality flags
                    notes = []
                    if total_defendants > 1:
                        notes.append(f"Multi-defendant case ({total_defendants} total)")
                    if defendant_data["AKA"] == "Y":
                        notes.append("Has AKA/alias names")
                    if not defendant_data["BirthYear"]:
                        notes.append("DOB missing from docket; need article age")
                    elif defendant_data["BirthYear"]:
                        notes.append("DOB=birth year only (court data)")
                    if not date_filed:
                        notes.append("DateFiled missing")
                    
                    # Add format used note
                    format_used = "S-prefixed" if successful_case.startswith("S") and not raw.startswith("S") else "original"
                    notes.append(f"Found using {format_used} format via form search")
                    
                    # Add multi-location notes if present
                    if hasattr(defendant_data, 'additional_notes') and defendant_data.get('additional_notes'):
                        notes.extend(defendant_data['additional_notes'])
                    
                    # Compile row data
                    row_data = [
                        successful_case,         # CaseNumber (use the format that worked)
                        full_name,              # DefendantName  
                        formatted_dob,          # DOB
                        formatted_date_filed,   # DateFiled
                        case_location,          # CaseLocation
                        "",                     # CrimeDate (Step 2)
                        "",                     # AgeAtCrime (Step 3)
                        "",                     # AgeBand (Step 3)
                        "",                     # Sentence (Step 2)
                        "",                     # DefendantRace (Step 2)
                        "Bonnie Dumanis",       # DAEra
                        defendant_role,         # DefendantRole
                        total_defendants,       # TotalDefendants
                        def_idx,                # DefendantIndex
                        defendant_data["AKA"],  # AKA
                        successful_url,         # Source_DocketURL
                        "",                     # Source_ArticleURL (Step 2)
                        "; ".join(notes)        # Notes
                    ]
                    
                    print(f"      #{def_idx}: {full_name} (Born: {defendant_data['BirthYear'] or 'Unknown'})")
                    all_data.append(row_data)
                    
            else:
                # No defendants found - create error row
                print(f"   ⚠️  No defendants extracted")
                all_data.append([
                    successful_case, "", "", formatted_date_filed, case_location, "", "", "", "", "",
                    "Bonnie Dumanis", "", "", "", "", successful_url, "", "No defendants found in docket"
                ])
            
            print(f"      Filed: {date_filed or 'Unknown'} | Location: {case_location or 'Unknown'}")
            
        except Exception as e:
            print(f"   ❌ Error processing {raw}: {e}")
            all_data.append([
                raw, "", "", "", "", "", "", "", "", "", "Bonnie Dumanis",
                "", "", "", "", " | ".join(attempted_urls) if attempted_urls else "Form submission failed", 
                "", f"Scraping error: {str(e)}"
            ])

    browser.close()

    # Create DataFrame and export to Excel
    print(f"\n📊 Creating Excel file with {len(all_data)} rows...")
    
    try:
        df = pd.DataFrame(all_data, columns=columns)
        
        # Create Excel file with formatting
        with pd.ExcelWriter(out_xlsx, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Court_Data', index=False)
            
            # Get the workbook and worksheet for formatting
            workbook = writer.book
            worksheet = writer.sheets['Court_Data']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
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
        # Try to save progress with the interrupt handler
        save_progress_and_exit()
