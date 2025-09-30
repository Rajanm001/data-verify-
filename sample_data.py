"""
Sample data for GetGSA testing
Contains the sample inputs from the specification plus additional edge cases
"""

SAMPLE_COMPANY_PROFILE_A = """Company Profile (A):
Acme Robotics LLC
UEI: ABC123DEF456
DUNS: 123456789
NAICS: 541511, 541512
POC: Jane Smith, jane@acme.co, (415) 555-0100
Address: 444 West Lake Street, Suite 1700, Chicago, IL 60606
SAM.gov: registered"""

SAMPLE_COMPANY_PROFILE_INCOMPLETE = """Company Profile (B):
Beta Systems Inc.
DUNS: 987654321
NAICS: 541611
POC: Bob Wilson, bob@beta.com, (312) 555-0200
Address: 100 North Michigan Avenue, Chicago, IL 60601
SAM.gov: registered"""

SAMPLE_PAST_PERFORMANCE_1 = """Past Performance (PP-1):
Customer: City of Palo Verde
Contract: Website modernization
Value: $18,000
Period: 07/2023 - 03/2024
Contact: John Roe, cio@pverde.gov"""

SAMPLE_PAST_PERFORMANCE_2 = """Past Performance (PP-2):
Customer: State of Fremont
Contract: Data migration & support
Value: $82,500
Period: 10/2022 - 02/2024
Contact: sarah.lee@fremont.gov"""

SAMPLE_PRICING_SHEET = """Pricing Sheet (text; simplified):
Labor Category, Rate, Unit
Senior Developer, 185, Hour
Project Manager, 165, Hour"""

SAMPLE_PRICING_INCOMPLETE = """Pricing Sheet (incomplete):
Labor Category, Rate
Senior Developer, 185
Project Manager, 165
Business Analyst"""

# Edge cases for testing robustness
EDGE_CASE_INVALID_EMAIL = """Company Profile (C):
Gamma Corp
UEI: GAMMA1234567
DUNS: 111222333
POC: Invalid Contact, not-an-email, (555) 555-5555
SAM.gov: pending"""

EDGE_CASE_MISSING_DUNS = """Company Profile (D):
Delta Services
UEI: DELTA1234567
NAICS: 518210
POC: Delta Admin, admin@delta.org, 555-123-4567
SAM.gov: registered"""

EDGE_CASE_LOW_VALUE_PP = """Past Performance (PP-3):
Customer: Small Town Municipality
Contract: Basic IT support
Value: $5,000
Period: 01/2024 - 03/2024
Contact: mayor@smalltown.gov"""

EDGE_CASE_HIGH_VALUE_PP = """Past Performance (PP-4):
Customer: Federal Agency XYZ
Contract: Enterprise system overhaul
Value: $2,500,000
Period: 01/2020 - 12/2023
Contact: contracting.officer@agency.gov"""

ALL_SAMPLE_DOCUMENTS = [
    {"name": "Company Profile A", "text": SAMPLE_COMPANY_PROFILE_A, "type_hint": "company_profile"},
    {"name": "Company Profile B (Incomplete)", "text": SAMPLE_COMPANY_PROFILE_INCOMPLETE, "type_hint": "company_profile"},
    {"name": "Past Performance PP-1", "text": SAMPLE_PAST_PERFORMANCE_1, "type_hint": "past_performance"},
    {"name": "Past Performance PP-2", "text": SAMPLE_PAST_PERFORMANCE_2, "type_hint": "past_performance"},
    {"name": "Pricing Sheet", "text": SAMPLE_PRICING_SHEET, "type_hint": "pricing"},
    {"name": "Pricing Sheet (Incomplete)", "text": SAMPLE_PRICING_INCOMPLETE, "type_hint": "pricing"},
]

EDGE_CASE_DOCUMENTS = [
    {"name": "Invalid Email", "text": EDGE_CASE_INVALID_EMAIL, "type_hint": "company_profile"},
    {"name": "Missing DUNS", "text": EDGE_CASE_MISSING_DUNS, "type_hint": "company_profile"},
    {"name": "Low Value PP", "text": EDGE_CASE_LOW_VALUE_PP, "type_hint": "past_performance"},
    {"name": "High Value PP", "text": EDGE_CASE_HIGH_VALUE_PP, "type_hint": "past_performance"},
]