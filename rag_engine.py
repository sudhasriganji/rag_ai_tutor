import os
from pathlib import Path

from dotenv import load_dotenv


from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from ingest import build_vector_db


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    try:
        import streamlit as st
        API_KEY = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        API_KEY = None

if not API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY is missing.\n"
        "Please add your Gemini API key to the .env file:\n\n"
        "GOOGLE_API_KEY=your_api_key_here"
    )


# =========================================================
# ANSWER QUESTION USING HYBRID RAG + LLM
# =========================================================

def answer_question(query: str) -> str:

    # -----------------------------------------------------
    # 1. Load embedding model
    # -----------------------------------------------------

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )


    # -----------------------------------------------------
    # 2. Load Chroma vector database
    # -----------------------------------------------------

    if not os.path.exists("./chroma_db"):
        build_vector_db()

    vector_store = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )


    # -----------------------------------------------------
    # 3. Retrieve relevant documents
    # -----------------------------------------------------

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 4}
    )

    docs = retriever.invoke(query)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )


    # -----------------------------------------------------
    # 4. Create a flexible AI tutor prompt
    # -----------------------------------------------------

    system_prompt = """
You are an intelligent and helpful AI tutor specializing in
Quantum Computing, Qiskit, programming, mathematics, and
general knowledge.

You have access to retrieved study material below.

IMPORTANT RULES:

1. Use the retrieved study material when it is relevant to
   the user's question.

2. If the retrieved material does NOT contain the answer,
   DO NOT say:
   "The information is not available in the study material."

3. Instead, answer the question using your own general
   knowledge.

4. If the retrieved material is only partially relevant,
   combine the useful information from the material with
   your own knowledge.

5. Never force irrelevant retrieved information into an answer.

6. Answer naturally and conversationally, like a modern AI
   assistant.

7. Explain difficult concepts clearly and provide examples
   when useful.

8. If the user asks a normal non-quantum question, you can
   answer it normally using your general knowledge.

9. Do not pretend that information came from the study
   material when it did not.

10. If the question requires current or real-time information
    that you do not have access to, clearly say that.

Retrieved study material:
-------------------------
{context}
-------------------------
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}")
        ]
    )


    # -----------------------------------------------------
    # 5. Initialize Gemini
    # -----------------------------------------------------

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0.4,
        google_api_key=API_KEY
    )


    # -----------------------------------------------------
    # 6. Build hybrid RAG chain
    # -----------------------------------------------------

    rag_chain = (
        {
            "context": lambda _: context,
            "input": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )


    # -----------------------------------------------------
    # 7. Generate answer
    # -----------------------------------------------------

    return rag_chain.invoke(query)