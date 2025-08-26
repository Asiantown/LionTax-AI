"""Basic RAG Engine for Singapore Tax GPT - MVP Implementation."""

import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BasicRAGEngine:
    """Minimal RAG engine for Day 1-2 MVP."""
    
    def __init__(self):
        """Initialize the basic RAG components."""
        # Initialize OpenAI
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
        )
        
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize ChromaDB
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
        self.vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings,
            collection_name=os.getenv("CHROMA_COLLECTION_NAME", "singapore_tax_docs")
        )
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Create QA chain
        self.qa_chain = self._create_qa_chain()
    
    def _create_qa_chain(self):
        """Create a simple QA chain."""
        prompt_template = """Use the following context to answer the question.
        
        Context: {context}
        
        Question: {question}
        
        Answer the question based on the context. If you cannot answer from the context, say so.
        Include the source document in your answer.
        
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "question"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load and process a single document."""
        # Determine loader based on file extension
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.txt'):
            loader = TextLoader(file_path)
        else:
            print(f"Unsupported file type: {file_path}")
            return []
        
        # Load and split
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata['source'] = os.path.basename(file_path)
        
        return chunks
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store."""
        self.vectorstore.add_documents(documents)
        print(f"Added {len(documents)} document chunks to vector store")
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG system."""
        result = self.qa_chain.invoke({"query": question})
        
        # Format response
        response = {
            "answer": result["result"],
            "sources": []
        }
        
        # Add source documents
        for doc in result.get("source_documents", []):
            response["sources"].append({
                "content": doc.page_content[:200] + "...",
                "source": doc.metadata.get("source", "Unknown")
            })
        
        return response


def test_basic_rag():
    """Test the basic RAG engine with sample content."""
    print("Testing Basic RAG Engine...")
    
    # Initialize engine
    engine = BasicRAGEngine()
    
    # Create a test document
    test_content = """
    Singapore Income Tax Rates for Year of Assessment 2024:
    
    For resident individuals, the tax rates are progressive:
    - First $20,000: 0%
    - Next $10,000: 2%
    - Next $10,000: 3.5%
    - Next $40,000: 7%
    - Next $40,000: 11.5%
    - Next $40,000: 15%
    
    Non-residents pay a flat rate of 15% or progressive rates, whichever is higher.
    
    The tax filing deadline for paper filing is 15 April, and for e-filing is 18 April.
    """
    
    # Save test content to file
    test_file = "./data/test_tax_info.txt"
    os.makedirs("./data", exist_ok=True)
    with open(test_file, "w") as f:
        f.write(test_content)
    
    # Load and add document
    documents = engine.load_document(test_file)
    engine.add_documents(documents)
    
    # Test queries
    test_queries = [
        "What is the tax rate for the first $20,000?",
        "When is the e-filing deadline?",
        "How are non-residents taxed?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = engine.query(query)
        print(f"Answer: {response['answer']}")
        print(f"Sources: {[s['source'] for s in response['sources']]}")


if __name__ == "__main__":
    test_basic_rag()