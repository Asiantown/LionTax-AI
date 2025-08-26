"""Create a test PDF using reportlab for parser testing."""

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not installed. Install with: uv pip install reportlab")

import os
from pathlib import Path


def create_iras_style_pdf():
    """Create a PDF that mimics IRAS e-Tax Guide structure."""
    
    if not REPORTLAB_AVAILABLE:
        print("❌ ReportLab not available. Installing...")
        os.system("uv pip install reportlab")
        print("Please run the script again after installation.")
        return None
    
    # Create PDF
    pdf_path = "./data/iras_docs/test_iras_income_tax_guide.pdf"
    Path("./data/iras_docs").mkdir(parents=True, exist_ok=True)
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='IRASTitle',
        parent=styles['Title'],
        fontSize=16,
        textColor=colors.HexColor('#003366'),
        spaceAfter=30,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='IRASHeading',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#003366'),
        spaceAfter=12
    ))
    
    # Title
    elements.append(Paragraph("IRAS e-Tax Guide", styles['IRASTitle']))
    elements.append(Paragraph("INCOME TAX: INDIVIDUALS", styles['IRASTitle']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Last Updated: 1 January 2024", styles['Normal']))
    elements.append(Paragraph("Year of Assessment 2024", styles['Normal']))
    elements.append(Spacer(1, 0.5*inch))
    
    # Section 1
    elements.append(Paragraph("1. TAX RESIDENCY", styles['IRASHeading']))
    elements.append(Paragraph(
        """1.1 You are a tax resident for a Year of Assessment (YA) if you are a:
        <br/>• Singapore Citizen who normally resides in Singapore
        <br/>• Singapore Permanent Resident who has a permanent home in Singapore
        <br/>• Foreigner who stayed/worked in Singapore for 183 days or more""",
        styles['Normal']
    ))
    elements.append(Spacer(1, 12))
    
    # Table - Tax Rates
    elements.append(Paragraph("2. TAX RATES FOR RESIDENTS (YA 2024)", styles['IRASHeading']))
    elements.append(Spacer(1, 12))
    
    data = [
        ['Chargeable Income', 'Tax Rate', 'Tax Payable'],
        ['First $20,000', '0%', '$0'],
        ['Next $10,000', '2%', '$200'],
        ['Next $10,000', '3.5%', '$350'],
        ['Next $40,000', '7%', '$2,800'],
        ['Next $40,000', '11.5%', '$4,600'],
        ['Next $40,000', '15%', '$6,000'],
        ['Above $160,000', 'Up to 24%', '-']
    ]
    
    table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 12))
    
    # Section 3
    elements.append(PageBreak())
    elements.append(Paragraph("3. TAX RELIEFS", styles['IRASHeading']))
    elements.append(Paragraph(
        """3.1 Personal Reliefs Available:
        <br/>• Earned Income Relief: Up to $1,000
        <br/>• Spouse Relief: $2,000 (if spouse's income ≤ $4,000)
        <br/>• Qualifying Child Relief: $4,000 per child
        <br/>• Parent Relief: $9,000 (living with) or $5,500 (not living with)""",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(elements)
    print(f"✅ Created test PDF: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    pdf_path = create_iras_style_pdf()
    
    if pdf_path and Path(pdf_path).exists():
        print("\n📄 Test PDF created successfully!")
        print(f"Location: {pdf_path}")
        print("\nNow you can test the parser with:")
        print("  uv run python test_real_pdf.py")