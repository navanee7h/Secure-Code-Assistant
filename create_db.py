import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_PATH = "data/owasp_top_10.md"
DB_DIR = "faiss_index"

def create_vector_db():
    print(f"Loading data from {DATA_PATH}...")
    loader = TextLoader(DATA_PATH, encoding='utf-8')
    documents = loader.load()

    print("Splitting text into chunks...")
    # Chunking logic ensuring we don't break code blocks unnecessarily
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    print("Generating embeddings and building FAISS vector store...")
    # Local open-source embedding model - perfect for offline security
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    db = FAISS.from_documents(chunks, embeddings)
    
    print(f"Saving vector database to {DB_DIR}...")
    db.save_local(DB_DIR)
    print("Database created and saved successfully!")

if __name__ == "__main__":
    if not os.path.exists("data"):
        print("Data directory not found. Please ensure data/owasp_top_10.md exists.")
    else:
        create_vector_db()
