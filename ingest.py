import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

def build_vector_db():
    if not os.path.exists("scraped_docs.txt"):
        print("Creating sample scraped_docs.txt...")
        with open("scraped_docs.txt", "w", encoding="utf-8") as f:
            f.write("IBM Quantum provides access to real quantum hardware and software tools like Qiskit.")

    with open("scraped_docs.txt", "r", encoding="utf-8") as f:
        data = f.read()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.create_documents([data])

    # Local open-source embedding model (runs completely offline without API 404 errors)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print("SUCCESS: Vector DB created successfully!")

if __name__ == "__main__":
    build_vector_db()