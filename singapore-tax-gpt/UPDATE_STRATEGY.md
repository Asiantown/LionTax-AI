# Strategy for Handling Outdated Tax Documents

## 🚨 The Problem
- The PDF files are Singapore Tax Acts (laws) from various years
- Tax RATES change yearly, but the Acts are the underlying legislation
- We discovered the non-resident rate was wrong (22% vs correct 15%/24%)
- There may be other outdated rates throughout the system

## 📊 Current Document Analysis
```
Income Tax Act 1947.pdf      - Base legislation (updated periodically)
GST Act 1993.pdf            - GST legislation 
Property Tax Act 1960.pdf   - Property tax legislation
Stamp Duties Act 1929.pdf   - Stamp duty legislation
Estate Duty Act 1929.pdf    - Estate duty (abolished in 2008)
```

These are ACTS (laws), not rate sheets. The Acts don't change often, but the RATES change annually.

## ✅ Recommended Solution

### 1. **Immediate Actions**
- [x] Fix non-resident rates (15%/24% vs 22%)
- [ ] Audit all rates in singapore_tax_facts.json against IRAS 2024
- [ ] Add a "last_updated" field to track data currency
- [ ] Add disclaimer about data currency in the UI

### 2. **Two-Tier Information System**
```
Tier 1: Structured Facts (singapore_tax_facts.json)
- All current rates, thresholds, reliefs for 2024/2025
- Manually updated from IRAS website
- Primary source for factual questions

Tier 2: Legislative Documents (PDFs)
- Tax Acts for understanding rules and regulations
- Good for conceptual questions
- Not for current rates
```

### 3. **Enhanced Q&A Logic**
```python
def answer_question(question):
    # 1. Check if asking for rates/numbers
    if is_factual_question(question):
        # Use singapore_tax_facts.json (current data)
        return get_from_structured_facts()
    
    # 2. For rules/regulations/concepts
    else:
        # Use PDF documents (legislation)
        return search_documents()
    
    # 3. Add web search fallback for current info
    if needs_current_data and not_in_facts:
        return web_search_current_rates()
```

### 4. **Data Updates Needed**

#### Critical Rate Updates for singapore_tax_facts.json:
- [x] Non-resident rates: 15% employment, 24% other
- [ ] GST rate: Verify current is 9% (was 8% in 2023)
- [ ] Corporate tax rate: Verify 17%
- [ ] Property tax rates: Check for 2024 changes
- [ ] CPF contribution rates: Update for 2024
- [ ] SRS contribution limits: Check for changes

#### Add New Fields:
```json
{
  "metadata": {
    "last_updated": "2024-12-19",
    "tax_year": "2024",
    "year_of_assessment": "2025",
    "data_source": "IRAS official website"
  },
  "income_tax": {
    "effective_from": "YA 2025",
    ...
  }
}
```

### 5. **Permanent Solution Options**

#### Option A: Manual Updates
- Create a quarterly update schedule
- Download IRAS rate cards/circulars
- Update singapore_tax_facts.json
- Pros: Accurate, controlled
- Cons: Manual effort required

#### Option B: Web Scraping
- Build IRAS website scraper
- Auto-update rates monthly
- Pros: Always current
- Cons: Website changes break scraper

#### Option C: Hybrid Approach (Recommended)
- Use structured facts for known rates
- Fall back to web search for unknown/recent changes
- Alert when discrepancies found
- Manual review and update quarterly

## 🎯 Priority Actions

1. **TODAY**: Update all 2024 tax rates in singapore_tax_facts.json
2. **THIS WEEK**: Add web search fallback for rate questions
3. **ONGOING**: Quarterly manual updates from IRAS

## ⚠️ Risk Mitigation

Add disclaimer to app:
```
"Tax rates and regulations are subject to change. 
This system uses data current as of December 2024.
Please verify critical information with IRAS directly."
```

## 📝 Notes
- The Income Tax Act PDF is legislation, not a rate sheet
- IRAS publishes annual rate cards separately from Acts
- We need to distinguish between RULES (from Acts) and RATES (from IRAS updates)