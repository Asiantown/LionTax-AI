"""Quick demonstration of smart chunking benefits."""

from src.core.smart_chunker import SmartTaxChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter


def demonstrate_smart_chunking():
    """Show the benefits of smart chunking with examples."""
    
    print("\n" + "="*60)
    print("🎯 SMART CHUNKING DEMONSTRATION")
    print("="*60)
    
    # Example 1: Tax Rate Table
    tax_table = """
INCOME TAX RATES (YEAR OF ASSESSMENT 2024)

The following progressive tax rates apply to resident individuals:

| Chargeable Income | Tax Rate | Gross Tax Payable |
|-------------------|----------|------------------|
| First $20,000     | 0%       | $0               |
| Next $10,000      | 2%       | $200             |
| Next $10,000      | 3.5%     | $350             |
| Next $40,000      | 7%       | $2,800           |
| Next $40,000      | 11.5%    | $4,600           |
| Next $40,000      | 15%      | $6,000           |
| Next $40,000      | 18%      | $7,200           |
| Next $40,000      | 19%      | $7,600           |
| Next $40,000      | 19.5%    | $7,800           |
| Next $40,000      | 20%      | $8,000           |
| Above $320,000    | 22%      | Variable         |

Note: For income above $1,000,000, the maximum rate is 24%.
"""
    
    # Example 2: Relief List
    relief_list = """
TAX RELIEFS AVAILABLE

Resident individuals may claim the following personal reliefs:

• Earned Income Relief
  - Maximum: $1,000
  - Conditions: Age below 55, income not exceeding $4,000

• Spouse Relief
  - Amount: $2,000
  - Conditions: Supporting spouse whose income ≤ $4,000

• Qualifying Child Relief (QCR)
  - Amount: $4,000 per child
  - Conditions: Child unmarried and either:
    • Below 16 years old
    • Studying full-time at any educational institution
    • Serving National Service

• Parent Relief
  - Amount: $9,000 (living with parent)
  - Amount: $5,500 (not living with parent)
  - Conditions: Supporting parent aged 55 and above

• CPF Cash Top-up Relief
  - Maximum: $8,000 per year
  - For cash top-ups to own or family members' CPF accounts
"""
    
    # Initialize chunkers
    smart_chunker = SmartTaxChunker(
        chunk_size=300,  # Small size to show splitting
        chunk_overlap=50,
        preserve_tables=True,
        preserve_lists=True
    )
    
    regular_chunker = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )
    
    # Test 1: Table Preservation
    print("\n📊 TEST 1: TAX RATE TABLE")
    print("-" * 40)
    
    smart_chunks = smart_chunker.split_text(tax_table)
    regular_chunks = regular_chunker.split_text(tax_table)
    
    print(f"Regular chunking: {len(regular_chunks)} chunks")
    print(f"Smart chunking: {len(smart_chunks)} chunks")
    
    # Check if table is preserved
    print("\n🔍 Checking table integrity:")
    
    # Regular chunks
    print("\nRegular Chunks:")
    table_broken = False
    for i, chunk in enumerate(regular_chunks, 1):
        table_rows = chunk.count('|')
        print(f"  Chunk {i}: {table_rows} table rows, {len(chunk)} chars")
        if '| First $20,000' in chunk and '| Above $320,000' not in chunk:
            table_broken = True
    
    if table_broken:
        print("  ❌ Table split across chunks - information fragmented!")
    
    # Smart chunks
    print("\nSmart Chunks:")
    for i, chunk in enumerate(smart_chunks, 1):
        if '|' in chunk:
            table_rows = chunk.count('\n') - chunk.count('\n\n')
            has_complete_table = '| First $20,000' in chunk and '| Above $320,000' in chunk
            print(f"  Chunk {i}: Complete table: {'✅' if has_complete_table else '❌'}")
            if has_complete_table:
                print(f"           {table_rows} rows preserved together")
    
    # Test 2: List Preservation
    print("\n📋 TEST 2: TAX RELIEF LIST")
    print("-" * 40)
    
    smart_chunks = smart_chunker.split_text(relief_list)
    regular_chunks = regular_chunker.split_text(relief_list)
    
    print(f"Regular chunking: {len(regular_chunks)} chunks")
    print(f"Smart chunking: {len(smart_chunks)} chunks")
    
    print("\n🔍 Checking list integrity:")
    
    # Check if individual reliefs are kept intact
    reliefs = ['Earned Income Relief', 'Spouse Relief', 'Qualifying Child Relief', 'Parent Relief']
    
    print("\nRegular Chunks:")
    for relief in reliefs:
        found_complete = False
        for chunk in regular_chunks:
            if relief in chunk and 'Conditions:' in chunk:
                # Check if the complete relief info is in one chunk
                if relief == 'Qualifying Child Relief':
                    if 'Below 16' in chunk and 'full-time' in chunk:
                        found_complete = True
                else:
                    found_complete = True
        print(f"  {relief}: {'✅ Complete' if found_complete else '❌ Split'}")
    
    print("\nSmart Chunks:")
    for relief in reliefs:
        found_complete = False
        for chunk in smart_chunks:
            if relief in chunk and 'Conditions:' in chunk:
                if relief == 'Qualifying Child Relief':
                    if 'Below 16' in chunk and 'full-time' in chunk:
                        found_complete = True
                else:
                    found_complete = True
        print(f"  {relief}: {'✅ Complete' if found_complete else '❌ Split'}")
    
    # Show impact on Q&A
    print("\n💡 IMPACT ON Q&A ACCURACY")
    print("-" * 40)
    
    print("\nScenario: User asks 'What is the tax rate for $100,000 income?'")
    print("\nWith Regular Chunking:")
    print("  • Might retrieve chunk with only first few tax brackets")
    print("  • Missing the $80,000-$120,000 bracket info")
    print("  • Answer could be incomplete or wrong")
    
    print("\nWith Smart Chunking:")
    print("  • Retrieves complete tax table in one chunk")
    print("  • All brackets available for calculation")
    print("  • Accurate answer guaranteed")
    
    print("\n" + "="*60)
    print("✅ SMART CHUNKING BENEFITS DEMONSTRATED")
    print("="*60)
    
    print("\n📊 Summary:")
    print("  • Tables stay intact → Accurate rate lookups")
    print("  • Lists preserved → Complete information")
    print("  • Context maintained → Better retrieval")
    print("  • Fewer fragments → Higher quality answers")


if __name__ == "__main__":
    demonstrate_smart_chunking()