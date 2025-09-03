# Non-Resident Tax Rate Correction

## ❌ The Problem
The system was returning: "The tax rate for non-residents is a flat 22% on employment income"

This was **INCORRECT**.

## 🔍 Root Cause Analysis
1. The `singapore_tax_facts.json` file contained outdated information
2. It had a single field: `"non_resident_rate": 22`
3. This 22% rate was the OLD rate (pre-YA 2024) for director's fees/other income
4. It didn't distinguish between employment income and other types of income

## ✅ The Correct Rates (YA 2024/2025)

According to official IRAS sources:

### Employment Income
- **15% flat rate** (or progressive resident rates if higher)
- Special concession applies only to employment income
- Exempt if working ≤60 days (except directors, entertainers, professionals)

### Director's Fees and Other Income
- **24% flat rate** (increased from 22% in YA 2024)
- Applies to director's fees, consultant fees, all other income

### Important Notes
- Non-residents are NOT entitled to personal reliefs
- The 15% employment income rate is a concession (vs. the standard 24%)

## 🔧 What Was Fixed

1. **Updated `singapore_tax_facts.json`:**
   ```json
   "non_resident_rates": {
     "employment_income": 15,
     "other_income": 24,
     "note": "Employment income taxed at 15% or progressive rates..."
   }
   ```

2. **Updated `qa_working.py` response:**
   ```
   Tax rates for non-residents:
   
   Employment income: 15% flat rate (or progressive resident rates if higher)
   Director's fees and other income: 24% flat rate
   
   Note: Non-residents are not entitled to personal reliefs
   ```

## 📚 Sources
- IRAS official website: Individual Income Tax rates
- Web search confirmed YA 2024 rates (24% for other income, up from 22%)
- Employment income concession remains at 15%

## ⚠️ Lesson Learned
Tax rates change over time. The system was using outdated 2023 data.
Always verify tax information against current official sources.