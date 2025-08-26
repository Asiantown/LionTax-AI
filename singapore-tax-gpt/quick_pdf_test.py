"""Quick test to check PDF content extraction."""

import pdfplumber
from pathlib import Path


def quick_pdf_check(pdf_path):
    """Quick check of PDF content."""
    print(f"\n🔍 Quick PDF Analysis: {Path(pdf_path).name}")
    print("="*60)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 Pages: {len(pdf.pages)}")
            
            # Check first few pages
            for i, page in enumerate(pdf.pages[:3], 1):
                text = page.extract_text()
                if text:
                    print(f"\n📖 Page {i} Preview:")
                    print("-"*40)
                    # Show first 300 characters
                    preview = text[:300].replace('\n', ' ')
                    print(preview + "...")
                    
                    # Check for tables
                    tables = page.extract_tables()
                    if tables:
                        print(f"  📊 Found {len(tables)} table(s) on this page")
                
            # Check page 10 if it exists (usually has more content)
            if len(pdf.pages) > 10:
                page10 = pdf.pages[10]
                text = page10.extract_text()
                if text:
                    print(f"\n📖 Page 11 Preview:")
                    print("-"*40)
                    preview = text[:300].replace('\n', ' ')
                    print(preview + "...")
                    
                    # Look for key tax terms
                    keywords = ['rate', 'deduction', 'income', 'tax', 'assessment', 'relief']
                    found_keywords = [kw for kw in keywords if kw in text.lower()]
                    if found_keywords:
                        print(f"  🔑 Keywords found: {', '.join(found_keywords)}")
            
            print(f"\n✅ PDF is readable and contains text content")
            
    except Exception as e:
        print(f"❌ Error: {e}")


# Test both PDFs
pdfs = [
    "./data/iras_docs/Income Tax (Exemption of Foreign Income) Order 201.pdf",
    "./data/iras_docs/Income Tax Act 1947.pdf"
]

for pdf_path in pdfs:
    if Path(pdf_path).exists():
        quick_pdf_check(pdf_path)