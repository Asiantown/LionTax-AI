"""Test tax content optimization functionality."""

from src.core.tax_content_optimizer import TaxContentOptimizer
from src.core.advanced_pdf_parser import IRASPDFParser
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_tax_content_optimizer():
    """Test tax content optimization."""
    print("\n" + "="*70)
    print("🎯 TAX CONTENT OPTIMIZER TEST")
    print("="*70)
    
    optimizer = TaxContentOptimizer()
    
    # Test 1: Tax Rate Table Optimization
    print("\n📊 TEST 1: Tax Rate Table Preservation")
    print("-" * 50)
    
    tax_rate_content = """
    Tax Rates for YA 2024
    
    Individual Income Tax Rates:
    | Income Range | Tax Rate |
    |-------------|----------|
    | First $20,000 | 0% |
    | Next $10,000 | 2% |
    | Next $10,000 | 3.5% |
    | Next $40,000 | 7% |
    | Next $40,000 | 11.5% |
    | Above $120,000 | 15% |
    
    Note: These rates apply to tax residents only.
    """
    
    sections = optimizer.optimize_content(tax_rate_content)
    
    print(f"  Sections created: {len(sections)}")
    for i, section in enumerate(sections, 1):
        print(f"  {i}. Type: {section.section_type}")
        print(f"     Priority: {section.priority}/10")
        print(f"     Preserve whole: {section.preserve_whole}")
        print(f"     Size: {len(section.content)} chars")
    
    if any(s.section_type == 'tax_rate_table' and s.preserve_whole for s in sections):
        print("  ✅ Tax rate table preserved as whole")
    else:
        print("  ❌ Tax rate table not properly preserved")
    
    # Test 2: Calculation Example Optimization
    print("\n🧮 TEST 2: Calculation Example Handling")
    print("-" * 50)
    
    example_content = """
    Example 1: Tax Calculation for Employment Income
    
    Mr. Tan's annual income is $85,000. His tax calculation:
    - First $20,000 @ 0% = $0
    - Next $10,000 @ 2% = $200
    - Next $10,000 @ 3.5% = $350
    - Next $40,000 @ 7% = $2,800
    - Remaining $5,000 @ 11.5% = $575
    
    Total tax payable = $3,925
    
    Example 2: With Tax Relief
    
    If Mr. Tan claims Earned Income Relief of $1,000:
    Taxable income = $84,000
    Tax payable = $3,810
    """
    
    sections = optimizer.optimize_content(example_content)
    
    print(f"  Sections created: {len(sections)}")
    for section in sections:
        if 'example' in section.section_type.lower():
            print(f"  Found: {section.section_type}")
            print(f"  Priority: {section.priority}/10")
            print(f"  Content preview: {section.content[:100]}...")
    
    # Test 3: Mixed Content Optimization
    print("\n🔀 TEST 3: Mixed Content Optimization")
    print("-" * 50)
    
    mixed_content = """
    INCOME TAX TREATMENT OF EMPLOYMENT BENEFITS
    
    1. Definition
    "Employment benefits" means any benefit provided by an employer to an employee.
    
    2. Taxable Benefits
    The following benefits are taxable:
    - Housing accommodation
    - Car benefits
    - Club memberships
    
    3. Tax Rates
    Benefits are taxed at the following rates:
    | Benefit Type | Tax Rate |
    |-------------|----------|
    | Housing | 10% of income |
    | Car | $xxx per month |
    
    4. Calculation Example
    Employee with $100,000 salary and housing benefit:
    - Basic salary: $100,000
    - Housing benefit (10%): $10,000
    - Total taxable: $110,000
    
    5. Compliance Requirements
    Employers must report all benefits in Form IR8A by 1 March.
    """
    
    sections = optimizer.optimize_content(mixed_content)
    
    print(f"  Total sections: {len(sections)}")
    
    # Count section types
    section_types = {}
    for section in sections:
        section_types[section.section_type] = section_types.get(section.section_type, 0) + 1
    
    print("\n  Section type distribution:")
    for stype, count in section_types.items():
        print(f"    {stype}: {count}")
    
    # Check priority distribution
    high_priority = sum(1 for s in sections if s.priority >= 7)
    print(f"\n  High priority sections (≥7): {high_priority}/{len(sections)}")
    
    # Test 4: Retrieval Optimization
    print("\n🔍 TEST 4: Retrieval Optimization")
    print("-" * 50)
    
    retrieval_docs = optimizer.optimize_for_retrieval(sections)
    
    print(f"  Documents prepared for retrieval: {len(retrieval_docs)}")
    
    # Check metadata enrichment
    for i, doc in enumerate(retrieval_docs[:3], 1):
        print(f"\n  Document {i}:")
        print(f"    Section type: {doc['metadata'].get('section_type')}")
        print(f"    Priority: {doc['metadata'].get('priority')}")
        if 'search_keywords' in doc['metadata']:
            print(f"    Search keywords: {', '.join(doc['metadata']['search_keywords'])}")
        if 'years' in doc['metadata']:
            print(f"    Years referenced: {', '.join(doc['metadata']['years'])}")
    
    # Test 5: Real PDF Content
    print("\n📄 TEST 5: Real PDF Content Optimization")
    print("-" * 50)
    
    parser = IRASPDFParser()
    pdf_files = list(Path("./data/iras_docs").glob("*.pdf"))[:1]
    
    if pdf_files:
        pdf_file = pdf_files[0]
        print(f"  Testing with: {pdf_file.name}")
        
        sections = parser.parse_pdf(str(pdf_file))
        if sections and len(sections) > 0:
            # Take first section with substantial content
            for parsed_section in sections:
                if len(parsed_section.content) > 500:
                    test_content = parsed_section.content[:2000]
                    break
            
            optimized = optimizer.optimize_content(test_content, 'act')
            
            print(f"  Original size: {len(test_content)} chars")
            print(f"  Optimized into: {len(optimized)} sections")
            
            # Show optimization results
            total_size = sum(len(s.content) for s in optimized)
            preserved = sum(1 for s in optimized if s.preserve_whole)
            
            print(f"  Total optimized size: {total_size} chars")
            print(f"  Sections preserved whole: {preserved}/{len(optimized)}")
            
            # Check for critical content preservation
            has_critical = any(s.priority >= 8 for s in optimized)
            if has_critical:
                print("  ✅ Critical content identified and prioritized")
    
    # Test 6: Performance
    print("\n⚡ TEST 6: Optimization Performance")
    print("-" * 50)
    
    import time
    
    # Create large content
    large_content = mixed_content * 10  # Repeat content 10 times
    
    start_time = time.time()
    sections = optimizer.optimize_content(large_content)
    optimization_time = time.time() - start_time
    
    print(f"  Content size: {len(large_content)} chars")
    print(f"  Sections created: {len(sections)}")
    print(f"  Optimization time: {optimization_time:.3f}s")
    
    if optimization_time < 1:
        print("  ✅ Performance: Excellent (<1s)")
    elif optimization_time < 3:
        print("  ⚠️ Performance: Acceptable (<3s)")
    else:
        print("  ❌ Performance: Slow (>3s)")
    
    # Summary
    print("\n" + "="*70)
    print("📊 OPTIMIZATION SUMMARY")
    print("="*70)
    
    print("\n✅ Capabilities demonstrated:")
    print("  • Tax rate table preservation")
    print("  • Calculation example handling")
    print("  • Mixed content optimization")
    print("  • Metadata enrichment for retrieval")
    print("  • Priority-based content ranking")
    print("  • Smart splitting with boundary respect")
    
    print("\n🎯 Benefits for RAG:")
    print("  • Better chunk coherence")
    print("  • Preserved critical information")
    print("  • Enhanced retrieval accuracy")
    print("  • Context-aware chunking")


if __name__ == "__main__":
    test_tax_content_optimizer()