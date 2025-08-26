"""Simple Q&A that actually works."""

import os
from dotenv import load_dotenv
load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

print("Loading system...")

# Load vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(
    persist_directory="./data/chroma_db",
    embedding_function=embeddings,
    collection_name="singapore_tax_docs"
)

# Create simple QA chain
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

print("Ready! Ask your questions:\n")

while True:
    question = input("Question: ").strip()
    if question.lower() in ['exit', 'quit', 'q']:
        break
    
    print("\nSearching...")
    result = qa_chain.invoke({"query": question})
    print(f"\nAnswer: {result['result']}\n")
    print("-" * 60)