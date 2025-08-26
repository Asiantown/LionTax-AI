# 🧪 Testing Singapore Tax GPT

## Quick Start Testing

### 1. Quick System Test
```bash
# Verify all components are working
uv run python test_complete_system.py quick
```

### 2. Complete System Test
```bash
# Test document processing and queries
uv run python test_complete_system.py
```

### 3. Interactive Command Line Test
```bash
# Interactive Q&A mode
uv run python test_complete_system.py interactive
```

### 4. Web Interface (Streamlit)
```bash
# Launch the web UI
uv run streamlit run app.py
```
Then open http://localhost:8501 in your browser

## Component Tests

### Test Individual Components
```bash
# Test PDF Parser
uv run python test_advanced_parser.py

# Test Smart Chunking
uv run python test_smart_chunking.py

# Test Metadata Extraction
uv run python comprehensive_metadata_test.py

# Test Document Classifier
uv run python test_document_classifier.py

# Test Batch Processing
uv run python test_batch_processing.py

# Test Query Enhancement
uv run python test_query_enhancement.py

# Test Update Detection
uv run python test_update_detection.py

# Test Tax Content Optimizer
uv run python test_tax_optimizer.py
```

## Sample Test Queries

Try these queries in any of the testing interfaces:

### Income Tax Queries
- "What is the income tax rate for $100,000 salary?"
- "How do I calculate tax for YA 2024?"
- "What tax reliefs can I claim?"
- "Am I eligible for parent relief?"

### GST Queries
- "What is the current GST rate?"
- "When do I need to register for GST?"
- "What supplies are zero-rated?"

### Property Tax Queries
- "How is property tax calculated?"
- "What is the owner-occupier tax rate?"
- "What is annual value?"

### Procedural Queries
- "How to file income tax return?"
- "When is the tax filing deadline?"
- "How to submit Form IR8A?"

## Testing Workflow

### Step 1: Process Documents
```python
# In Python or via UI
from src.core.batch_processor import BatchDocumentProcessor

processor = BatchDocumentProcessor()
report = processor.process_directory("./data/iras_docs", "*.pdf")
print(f"Processed {report.successful} documents")
```

### Step 2: Test Queries
```python
from src.core.enhanced_rag import EnhancedRAGEngine

engine = EnhancedRAGEngine()
response = engine.query_with_metadata("What is the tax rate?")
print(response['answer'])
```

### Step 3: Check Results
- Verify answer accuracy
- Check source citations
- Review confidence scores

## Performance Benchmarks

Expected performance metrics:
- PDF parsing: ~40s for 1000 pages
- Query enhancement: <10ms
- RAG retrieval: 2-5 seconds
- Document classification: 100% accuracy on test set

## Troubleshooting

### If tests fail:

1. **Check API Key**
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

2. **Verify Dependencies**
   ```bash
   uv sync
   ```

3. **Check PDF Files**
   ```bash
   ls -la data/iras_docs/*.pdf
   ```

4. **Clear Cache** (if needed)
   ```bash
   rm -rf data/chroma_db/*
   rm data/processing_cache.json
   rm data/version_db.json
   ```

5. **View Logs**
   ```bash
   # Components log to console by default
   # Check for INFO/ERROR messages
   ```

## Expected Output

### Successful Test Output:
```
✅ PDF Parser working
✅ Metadata extraction working (Type: e-tax-guide)
✅ Query enhancement working (Type: factual)
✅ RAG Engine initialized
🎉 All components working!
```

### Query Response Example:
```
Query: What is the income tax rate?
Answer: For Singapore tax residents, the income tax rates 
        for YA 2024 range from 0% to 22%...
Sources: 
  - income_tax_guide_2024.pdf
  - Income Tax Act 1947.pdf
```

## Data Requirements

Ensure you have PDF files in `./data/iras_docs/`:
- Income Tax Act
- IRAS e-Tax Guides
- Tax circulars
- Tax forms

Current test files:
- Income Tax Act 1947.pdf (1059 pages)
- Income Tax (Exemption of Foreign Income) Order 201.pdf (2 pages)

## Next Steps

After successful testing:
1. Add more IRAS documents
2. Fine-tune chunk sizes if needed
3. Adjust retrieval parameters
4. Deploy to production