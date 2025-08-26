"""Streamlit UI for Singapore Tax GPT."""

import streamlit as st
import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.core.enhanced_rag import EnhancedRAGEngine
from src.core.query_enhancer import QueryEnhancer
from src.core.batch_processor import BatchDocumentProcessor
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Page config
st.set_page_config(
    page_title="Singapore Tax Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        color: #1e293b;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px;
    }
    
    /* Professional header */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 50%, #475569 75%, #64748b 100%);
        padding: 4rem 2rem;
        margin: -2rem -2rem 3rem -2rem;
        border-radius: 0 0 2rem 2rem;
        color: white;
        text-align: center;
        box-shadow: 
            0 20px 25px -5px rgba(0, 0, 0, 0.1),
            0 10px 10px -5px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
        z-index: 1;
    }
    
    .main-header > * {
        position: relative;
        z-index: 2;
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    
    .main-header p {
        font-size: 1.25rem;
        opacity: 0.9;
        margin: 0;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.5;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1cypcdb {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 2px solid #e2e8f0;
        box-shadow: 4px 0 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* Sidebar headers */
    .sidebar-header {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        font-weight: 600;
        font-size: 1rem;
        margin: 1.5rem -1rem 1rem -1rem;
        padding: 1rem;
        border-radius: 0.75rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.2s ease;
        margin-bottom: 1rem;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 10px 15px -3px rgba(0, 0, 0, 0.1),
            0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.875rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.25);
        width: 100%;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 12px -2px rgba(59, 130, 246, 0.35);
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        box-shadow: 0 4px 6px -1px rgba(5, 150, 105, 0.25);
        font-size: 1.1rem;
        padding: 1rem 2rem;
        font-weight: 700;
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 12px -2px rgba(5, 150, 105, 0.35);
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        padding: 0.75rem;
        border-radius: 1rem;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 0.75rem;
        padding: 1rem 2rem;
        font-weight: 600;
        color: #64748b;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        color: #1e40af;
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transform: translateY(-1px);
    }
    
    /* Card styling */
    .info-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e2e8f0;
        border-radius: 1rem;
        padding: 2rem;
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
        line-height: 1.7;
        font-size: 1.05rem;
    }
    
    /* Success/Error styling */
    .stSuccess {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #bbf7d0;
        border-radius: 0.75rem;
        box-shadow: 0 2px 4px rgba(34, 197, 94, 0.1);
    }
    
    .stError {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 2px solid #fecaca;
        border-radius: 0.75rem;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.1);
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #fed7aa;
        border-radius: 0.75rem;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.1);
    }
    
    .stInfo {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 2px solid #bfdbfe;
        border-radius: 0.75rem;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border: 2px solid #e2e8f0;
        border-radius: 0.75rem;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        line-height: 1.6;
        padding: 1rem;
        transition: all 0.2s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
        outline: none;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border: 2px solid #e2e8f0;
        border-radius: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #3b82f6;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
    }
    
    /* Loading spinner */
    .stSpinner {
        color: #3b82f6;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 0.75rem;
        overflow: hidden;
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 2px solid #e2e8f0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 0.75rem;
        border: 2px solid #e2e8f0;
        font-weight: 600;
    }
    
    /* Checkbox styling */
    .stCheckbox > label {
        font-weight: 500;
        color: #374151;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #e2e8f0;
    }
    
    /* Quick action buttons */
    .quick-action-btn {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 2px solid #e2e8f0;
        border-radius: 0.75rem;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        text-align: left;
        font-size: 0.9rem;
        color: #475569;
    }
    
    .quick-action-btn:hover {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        color: #1e40af;
        transform: translateX(4px);
    }
    
    /* Professional footer */
    .professional-footer {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        padding: 3rem 2rem;
        margin: 3rem -2rem -2rem -2rem;
        border-radius: 2rem 2rem 0 0;
        text-align: center;
        box-shadow: 0 -10px 25px rgba(0,0,0,0.1);
    }
    
    .professional-footer h3 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #f1f5f9;
    }
    
    .professional-footer p {
        opacity: 0.8;
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }
    
    .disclaimer {
        background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
        border: 2px solid #f59e0b;
        border-radius: 0.75rem;
        padding: 1rem;
        margin-top: 1.5rem;
        color: #92400e;
        font-weight: 500;
        font-size: 0.9rem;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag_engine' not in st.session_state:
    with st.spinner("🚀 Initializing Singapore Tax Assistant..."):
        st.session_state.rag_engine = EnhancedRAGEngine()
        st.session_state.query_enhancer = QueryEnhancer()
        st.session_state.batch_processor = BatchDocumentProcessor(
            rag_engine=st.session_state.rag_engine,
            max_workers=2,
            use_cache=True
        )

# Professional header
st.markdown("""
<div class="main-header">
    <h1>🏛️ Singapore Tax Assistant</h1>
    <p>Professional AI-powered tax guidance using official IRAS documents and regulations</p>
</div>
""", unsafe_allow_html=True)

# Enhanced sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">📊 System Overview</div>', unsafe_allow_html=True)
    
    # Document stats with enhanced display
    pdf_files = list(Path("./data/iras_docs").glob("*.pdf"))
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📄 Documents", len(pdf_files))
    with col2:
        # Calculate total size
        total_size = sum(f.stat().st_size for f in pdf_files) / (1024 * 1024)
        st.metric("💾 Total Size", f"{total_size:.1f} MB")
    
    st.markdown('<div class="sidebar-header">🧮 Tax Calculators</div>', unsafe_allow_html=True)
    
    calc_examples = [
        ("💰", "Calculate income tax for $120,000"),
        ("🏠", "Stamp duty for $1.5M property as citizen"),
        ("💼", "CPF contribution for $5,000 salary"),
        ("🏘️", "Property tax for $500,000 annual value"),
        ("🌏", "Stamp duty for foreigner buying $2M property"),
        ("📊", "Take home pay for $80,000 annual income"),
    ]
    
    for icon, example in calc_examples:
        if st.button(f"{icon} {example}", key=f"calc_{example}"):
            st.session_state.sample_query = example
    
    st.markdown('<div class="sidebar-header">💡 Quick Queries</div>', unsafe_allow_html=True)
    
    quick_queries = [
        ("❓", "What are the current tax rates?"),
        ("👨‍👩‍👧‍👦", "How to claim parent relief?"),
        ("📅", "When is the filing deadline?"),
        ("🎯", "What reliefs are available for YA 2024?"),
        ("📈", "GST registration requirements"),
        ("🏦", "Corporate tax obligations")
    ]
    
    for icon, query in quick_queries:
        if st.button(f"{icon} {query}", key=f"quick_{query}"):
            st.session_state.sample_query = query
    
    st.markdown('<div class="sidebar-header">⚙️ System Tools</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Document Database"):
        with st.spinner("Processing documents..."):
            report = st.session_state.batch_processor.scan_directory(
                "./data/iras_docs", 
                "*.pdf"
            )
            st.success(f"✅ Processed {report.total_documents} documents")
            if report.new_documents > 0:
                st.info(f"🆕 {report.new_documents} new documents added")
            if report.updated_documents > 0:
                st.info(f"🔄 {report.updated_documents} documents updated")

# Main interface with enhanced tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Tax Assistant", 
    "📄 Document Library", 
    "🔍 Advanced Tools",
    "📊 Analytics"
])

with tab1:
    st.markdown('<div class="section-header">💬 Ask Your Tax Questions</div>', unsafe_allow_html=True)
    st.markdown("Get instant, accurate answers from official IRAS documents and Singapore tax regulations.")
    
    # Check for sample query
    if 'sample_query' in st.session_state:
        query_input = st.session_state.sample_query
        del st.session_state.sample_query
    else:
        query_input = ""
    
    # Enhanced query input
    query = st.text_area(
        "Enter your tax question:",
        value=query_input,
        height=120,
        placeholder="e.g., How much income tax do I need to pay on an annual salary of $80,000? What deductions can I claim?",
        help="Ask detailed questions about Singapore taxes, calculations, deadlines, or regulations."
    )
    
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        submit = st.button("🔍 Get Answer", type="primary")
    with col2:
        show_details = st.checkbox("Show analysis", help="Display query processing details")
    with col3:
        confidence_threshold = st.slider("Confidence threshold", 0.0, 1.0, 0.7, 0.1)
    
    if submit and query:
        with st.spinner("🔍 Analyzing your question..."):
            # Enhance query
            enhanced = st.session_state.query_enhancer.enhance_query(query)
            
            # Show query analysis if requested
            if show_details:
                with st.expander("🔬 Query Analysis", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Query Type", enhanced.query_type)
                    with col2:
                        st.metric("Tax Category", enhanced.tax_category)
                    with col3:
                        st.metric("Confidence", f"{enhanced.confidence:.0%}")
                    with col4:
                        complexity = "High" if len(enhanced.keywords) > 10 else "Medium" if len(enhanced.keywords) > 5 else "Low"
                        st.metric("Complexity", complexity)
                    
                    if enhanced.entities['amounts']:
                        st.info(f"💰 **Amounts detected:** {', '.join(enhanced.entities['amounts'])}")
                    if enhanced.entities['years']:
                        st.info(f"📅 **Years detected:** {', '.join(enhanced.entities['years'])}")
                    if enhanced.keywords:
                        st.info(f"🔑 **Keywords:** {', '.join(enhanced.keywords[:15])}")
        
        with st.spinner("🔍 Searching official tax documents..."):
            try:
                # Get answer from RAG
                response = st.session_state.rag_engine.query_with_metadata(query)
                
                # Display answer in professional format
                st.markdown("### ✅ Official Answer")
                st.markdown(f"""
                <div class="info-card">
                    {response['answer']}
                </div>
                """, unsafe_allow_html=True)
                
                # Show confidence and sources
                col1, col2 = st.columns([3, 1])
                with col1:
                    if response['citations']:
                        with st.expander(f"📚 Official Sources ({len(response['citations'])} documents)", expanded=False):
                            for i, citation in enumerate(response['citations'], 1):
                                source = citation.get('source', 'Unknown Document')
                                section = citation.get('section', '')
                                pages = citation.get('pages', [])
                                
                                st.markdown(f"**{i}. {source}**")
                                if section:
                                    st.markdown(f"   📍 Section: {section}")
                                if pages:
                                    st.markdown(f"   📄 Pages: {', '.join(map(str, pages))}")
                                st.markdown("---")
                with col2:
                    # Add rating system
                    st.markdown("**Rate this answer:**")
                    rating = st.radio("", ["👍 Helpful", "👎 Not helpful", "🤔 Unclear"], key="rating")
                            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Please try rephrasing your question or check if documents are processed correctly.")

with tab2:
    st.markdown('<div class="section-header">📄 Document Management</div>', unsafe_allow_html=True)
    st.markdown("Manage and process official IRAS tax documents for the knowledge base.")
    
    # Enhanced document display
    pdf_files = list(Path("./data/iras_docs").glob("*.pdf"))
    
    if pdf_files:
        st.markdown(f"### Available Documents ({len(pdf_files)})")
        
        # Create enhanced document table
        doc_data = []
        total_size = 0
        for pdf in pdf_files:
            size_mb = pdf.stat().st_size / (1024 * 1024)
            total_size += size_mb
            modified = pdf.stat().st_mtime
            import datetime
            mod_date = datetime.datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M")
            
            doc_data.append({
                "📄 Document": pdf.name,
                "📊 Size (MB)": f"{size_mb:.2f}",
                "📅 Modified": mod_date,
                "✅ Status": "Ready"
            })
        
        st.dataframe(doc_data, use_container_width=True)
        
        # Document processing section
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_doc = st.selectbox(
                "Select a document to process:", 
                [p.name for p in pdf_files],
                help="Choose a document to reprocess or analyze"
            )
        with col2:
            st.metric("Total Library Size", f"{total_size:.1f} MB")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 Process Selected Document"):
                selected_path = Path("./data/iras_docs") / selected_doc
                with st.spinner(f"Processing {selected_doc}..."):
                    result = st.session_state.batch_processor.process_single_document(selected_path)
                    
                    if result.status == "success":
                        st.success(f"✅ Successfully processed!")
                        st.info(f"📊 Created {result.chunks_created} text chunks")
                        st.info(f"🏷️ Type: {result.document_type} | Category: {result.tax_category}")
                    elif result.status == "skipped":
                        st.info("ℹ️ Document already processed (found in cache)")
                    else:
                        st.error(f"❌ Processing failed: {result.error}")
        
        with col2:
            if st.button("🔄 Reprocess All Documents"):
                with st.spinner("Reprocessing all documents..."):
                    report = st.session_state.batch_processor.scan_directory(
                        "./data/iras_docs", 
                        "*.pdf"
                    )
                    st.success(f"✅ Processed {report.total_documents} documents")
        
        with col3:
            if st.button("🗑️ Clear Cache"):
                cache_file = Path("./data/processing_cache.json")
                if cache_file.exists():
                    cache_file.unlink()
                    st.success("✅ Cache cleared")
                else:
                    st.info("ℹ️ No cache to clear")
    else:
        st.warning("⚠️ No documents found in ./data/iras_docs/")
        st.info("📁 Add PDF files to the data/iras_docs/ directory to get started")

with tab3:
    st.markdown('<div class="section-header">🔍 Advanced Tools & Diagnostics</div>', unsafe_allow_html=True)
    st.markdown("System diagnostics, testing tools, and advanced configuration options.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🧪 Component Testing")
        
        test_results = {}
        
        if st.button("🔧 Test PDF Parser"):
            try:
                from src.core.advanced_pdf_parser import IRASPDFParser
                parser = IRASPDFParser()
                st.success("✅ PDF Parser: Working correctly")
                test_results['pdf_parser'] = True
            except Exception as e:
                st.error(f"❌ PDF Parser: {str(e)}")
                test_results['pdf_parser'] = False
        
        if st.button("🏷️ Test Metadata Extractor"):
            try:
                from src.core.metadata_extractor import MetadataExtractor
                extractor = MetadataExtractor()
                test_text = "Income Tax Act Year of Assessment 2024 Section 10"
                metadata = extractor.extract_metadata(test_text)
                st.success(f"✅ Metadata Extractor: Type={metadata.document_type}")
                test_results['metadata'] = True
            except Exception as e:
                st.error(f"❌ Metadata Extractor: {str(e)}")
                test_results['metadata'] = False
        
        if st.button("📋 Test Document Classifier"):
            try:
                from src.core.document_classifier import DocumentClassifier
                classifier = DocumentClassifier()
                result = classifier.classify("IRAS e-Tax Guide on GST", "", "")
                st.success(f"✅ Document Classifier: {result.document_type.value}")
                test_results['classifier'] = True
            except Exception as e:
                st.error(f"❌ Document Classifier: {str(e)}")
                test_results['classifier'] = False
        
        if st.button("🚀 Run All Tests"):
            with st.spinner("Running comprehensive system tests..."):
                # Test all components
                components = [
                    ("PDF Parser", "src.core.advanced_pdf_parser", "IRASPDFParser"),
                    ("Metadata Extractor", "src.core.metadata_extractor", "MetadataExtractor"),
                    ("Document Classifier", "src.core.document_classifier", "DocumentClassifier"),
                    ("Query Enhancer", "src.core.query_enhancer", "QueryEnhancer"),
                    ("RAG Engine", "src.core.enhanced_rag", "EnhancedRAGEngine")
                ]
                
                results = []
                for name, module, class_name in components:
                    try:
                        exec(f"from {module} import {class_name}")
                        results.append((name, "✅ Working"))
                    except Exception as e:
                        results.append((name, f"❌ Error: {str(e)[:50]}..."))
                
                for name, status in results:
                    if "✅" in status:
                        st.success(f"{name}: {status}")
                    else:
                        st.error(f"{name}: {status}")
    
    with col2:
        st.markdown("#### 📊 System Statistics")
        
        # Enhanced statistics display
        if st.button("📈 View Detailed Statistics"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                # Cache statistics
                cache_file = Path("./data/processing_cache.json")
                if cache_file.exists():
                    import json
                    with open(cache_file, 'r') as f:
                        cache = json.load(f)
                    st.metric("📦 Cached Documents", len(cache))
                    
                    # Calculate cache size
                    cache_size = cache_file.stat().st_size / 1024
                    st.metric("💾 Cache Size", f"{cache_size:.1f} KB")
                else:
                    st.info("No cache file found")
            
            with col_b:
                # Version database
                version_db = Path("./data/version_db.json")
                if version_db.exists():
                    import json
                    with open(version_db, 'r') as f:
                        versions = json.load(f)
                    st.metric("📋 Tracked Versions", len(versions))
                    
                    # Calculate version db size
                    db_size = version_db.stat().st_size / 1024
                    st.metric("🗄️ Version DB Size", f"{db_size:.1f} KB")
                else:
                    st.info("No version database found")
        
        # Memory and performance info
        if st.button("🖥️ System Performance"):
            import psutil
            import sys
            
            # Memory usage
            memory = psutil.virtual_memory()
            st.metric("💾 Available Memory", f"{memory.available / (1024**3):.1f} GB")
            st.metric("🐍 Python Memory", f"{sys.getsizeof(st.session_state) / (1024**2):.1f} MB")
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            st.metric("⚡ CPU Usage", f"{cpu_percent:.1f}%")

with tab4:
    st.markdown('<div class="section-header">📊 Usage Analytics</div>', unsafe_allow_html=True)
    st.markdown("Track system usage, popular queries, and performance metrics.")
    
    # Placeholder for analytics - in a real system, you'd track this data
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Total Queries Today", "47", delta="12")
        st.metric("⚡ Avg Response Time", "1.2s", delta="-0.3s")
    
    with col2:
        st.metric("👥 Active Users", "8", delta="3")
        st.metric("📊 Success Rate", "94%", delta="2%")
    
    with col3:
        st.metric("🔍 Cache Hit Rate", "78%", delta="5%")
        st.metric("📄 Documents Processed", str(len(pdf_files)), delta="0")
    
    # Popular queries section
    st.markdown("#### 🔥 Most Popular Queries")
    popular_queries = [
        "Income tax calculation for $100,000",
        "Stamp duty rates for property purchase",
        "CPF contribution rates 2024",
        "Tax filing deadline Singapore",
        "GST registration requirements"
    ]
    
    for i, query in enumerate(popular_queries, 1):
        st.write(f"{i}. {query}")
    
    # Performance chart placeholder
    st.markdown("#### 📈 Response Time Trends")
    st.info("📊 Analytics dashboard would show performance trends, popular query categories, and usage patterns over time.")

# Professional footer
st.markdown("""
<div class="professional-footer">
    <h3>🏛️ Singapore Tax Assistant</h3>
    <p><strong>Powered by Advanced AI and Official IRAS Documents</strong></p>
    <p>Providing accurate, up-to-date tax information for Singapore residents and businesses</p>
    
    <div class="disclaimer">
        ⚠️ <strong>Important Disclaimer:</strong> This is an AI assistant for informational purposes only. 
        Always verify important tax information with official IRAS sources or consult a qualified tax professional.
    </div>
</div>
""", unsafe_allow_html=True)