"""Enhanced RAG Engine with Advanced PDF Processing."""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import logging

from .advanced_pdf_parser import IRASPDFParser, ParsedSection

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedRAGEngine:
    """Enhanced RAG engine with advanced document processing capabilities."""
    
    def __init__(self):
        """Initialize the enhanced RAG engine."""
        # Disable telemetry
        os.environ['ANONYMIZED_TELEMETRY'] = 'False'
        
        # Initialize OpenAI
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
        )
        
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize ChromaDB with settings
        import chromadb
        from chromadb.config import Settings
        
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
        
        # Create client with telemetry disabled
        client_settings = Settings(
            anonymized_telemetry=False,
            persist_directory=persist_dir
        )
        
        self.vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings,
            collection_name=os.getenv("CHROMA_COLLECTION_NAME", "singapore_tax_docs"),
            client_settings=client_settings
        )
        
        # Initialize PDF parser
        self.pdf_parser = IRASPDFParser()
        
        # Smart text splitter for different content types
        self.text_splitters = {
            'default': RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", "! ", "? ", ", ", " ", ""]
            ),
            'table': RecursiveCharacterTextSplitter(
                chunk_size=2000,  # Larger chunks for tables
                chunk_overlap=100,
                separators=["\n\n", "\n", "|", " "]
            ),
            'list': RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=200,
                separators=["\n\n", "\n", "•", "-", "*", " "]
            )
        }
        
        # Create enhanced QA chain
        self.qa_chain = self._create_enhanced_qa_chain()
    
    def _create_enhanced_qa_chain(self):
        """Create an enhanced QA chain with better prompting."""
        prompt_template = """You are a Singapore tax assistant. Answer ONLY using the information in the context below. Do NOT use any external knowledge.
        
        Context from Singapore tax documents:
        {context}
        
        Question: {question}
        
        Important: Base your answer ONLY on the context above. If the information is in the context, provide it. If it's not clearly stated in the context, say "Based on the documents provided, I cannot find specific information about [topic]."
        
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "question"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 5, "fetch_k": 10}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
    
    def process_pdf(self, file_path: str) -> List[Document]:
        """Process a PDF file using the advanced parser."""
        logger.info(f"Processing PDF: {file_path}")
        
        # Parse PDF into sections
        sections = self.pdf_parser.parse_pdf(file_path)
        
        # Convert sections to documents
        documents = self.pdf_parser.sections_to_documents(sections)
        
        # Apply smart chunking based on content type
        chunked_documents = []
        for doc in documents:
            # Select appropriate splitter based on section type
            section_type = doc.metadata.get('section_type', 'default')
            if section_type in ['table', 'tax_rate_table']:
                splitter = self.text_splitters['table']
            elif section_type == 'list':
                splitter = self.text_splitters['list']
            else:
                splitter = self.text_splitters['default']
            
            # Split if content is too long
            if len(doc.page_content) > 1500:
                chunks = splitter.split_documents([doc])
                # Preserve metadata in all chunks
                for chunk in chunks:
                    chunk.metadata.update(doc.metadata)
                chunked_documents.extend(chunks)
            else:
                chunked_documents.append(doc)
        
        logger.info(f"Processed {len(sections)} sections into {len(chunked_documents)} chunks")
        return chunked_documents
    
    def add_pdf_document(self, file_path: str):
        """Add a PDF document to the vector store."""
        documents = self.process_pdf(file_path)
        self.vectorstore.add_documents(documents)
        # Force persist
        self.vectorstore.persist()
        logger.info(f"Added {len(documents)} chunks from {file_path}")
        return len(documents)
    
    def query_with_metadata(self, question: str) -> Dict[str, Any]:
        """Query with enhanced metadata in response."""
        # Check if this is a calculation query
        from .calculation_handler import CalculationHandler
        calc_handler = CalculationHandler()
        
        is_calculation, calc_response = calc_handler.handle_calculation_query(question)
        
        if is_calculation and calc_response:
            # Return calculation response
            return {
                "answer": calc_response,
                "citations": [],
                "metadata": {
                    "response_type": "calculation",
                    "used_calculator": True
                }
            }
        
        # Regular RAG query
        result = self.qa_chain.invoke({"query": question})
        
        # Enhanced citation formatting
        citations = []
        seen_sources = set()
        
        for doc in result.get("source_documents", []):
            source_key = f"{doc.metadata.get('source', 'Unknown')}-{doc.metadata.get('section_number', '')}"
            
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                
                citation = {
                    "content": doc.page_content[:300] + "...",
                    "source": doc.metadata.get('source', 'Unknown'),
                    "section": doc.metadata.get('section_title', ''),
                    "section_number": doc.metadata.get('section_number', ''),
                    "pages": doc.metadata.get('pages', []),
                    "type": doc.metadata.get('section_type', 'content'),
                    "year_assessment": doc.metadata.get('year_assessment', ''),
                    "last_updated": doc.metadata.get('last_updated', '')
                }
                citations.append(citation)
        
        return {
            "answer": result["result"],
            "citations": citations,
            "metadata": {
                "num_sources": len(citations),
                "doc_types": list(set(c.get('type', '') for c in citations))
            }
        }
    
    def process_directory(self, directory_path: str, file_pattern: str = "*.pdf") -> int:
        """Process all PDFs in a directory."""
        directory = Path(directory_path)
        pdf_files = list(directory.glob(file_pattern))
        
        total_chunks = 0
        for pdf_file in pdf_files:
            try:
                chunks = self.add_pdf_document(str(pdf_file))
                total_chunks += chunks
            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {e}")
                continue
        
        logger.info(f"Processed {len(pdf_files)} PDFs, total {total_chunks} chunks added")
        return total_chunks