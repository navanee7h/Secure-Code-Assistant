# Project Report: Secure Code & OWASP Assistant
**Role:** AI Developer / AI Security Engineer
**Core Technologies:** Python, LangChain, FAISS, Streamlit, HuggingFace, Groq (Llama-3), FAISS Vector Database

## 1. Executive Summary
The **Secure Code & OWASP Assistant** is a Retrieval-Augmented Generation (RAG) agent designed to act as a specialized AI Security Engineer. It solves a critical problem in the DevSecOps lifecycle: helping developers identify and patch security vulnerabilities (specifically OWASP Top 10) in their code *before* it gets deployed. 

Instead of relying on a generalized AI (which often hallucinates security advice), this tool grounds its answers in a dedicated Knowledge Base of exact OWASP standards, ensuring precise, auditable, and mathematically sound security remediations.

## 2. The Architecture (How it Works)
The project utilizes a standard RAG pipeline, which is broken down into two main phases: **Data Ingestion (Building the Brain)** and **Generation (Answering the User)**.

### Phase 1: Data Ingestion (create_db.py)
This phase runs once to build our secure knowledge base.
1. **The Knowledge Base:** We start with markdown documents containing the OWASP Top 10 standards (`data/owasp_top_10.md`).
2. **Data Loading:** `LangChain`'s `TextLoader` reads these documents into memory.
3. **Chunking/Splitting:** Instead of feeding massive documents into the AI, `RecursiveCharacterTextSplitter` breaks the text into 500-character blocks (chunks) with a 50-character overlap. This ensures that a security rule and its code example stay together in one chunk without being cut in half.
4. **Embedding (HuggingFace):** We convert the English text chunks into high-dimensional vectors (arrays of floating-point numbers) using `all-MiniLM-L6-v2`. We use a local HuggingFace model instead of a cloud API to guarantee zero data leakage of the security rules.
5. **Vector Database (FAISS):** These vectors are inserted into a FAISS (Facebook AI Similarity Search) database and saved locally to the disk (`faiss_index/`). FAISS acts as ultra-fast mathematical storage.

### Phase 2: Retrieval & Generation (app.py)
This is what happens when a user pastes vulnerable Python code into the Streamlit UI and clicks "Analyze".
1. **User Input:** The user provides a vulnerable script (e.g., featuring SQL Injection string concatenation).
2. **Query Embedding:** The user's prompt is embedded using the exact same HuggingFace model into a query vector.
3. **Semantic Search:** FAISS takes the query vector and does a rapid mathematical similarity search (Cosine Similarity or L2 distance) against all vectors in our database. It retrieves the top 2 closest chunks (e.g., the exact chunk explaining OWASP A03:2021 Injection).
4. **Prompt Construction:** We construct a prompt taking the form of:
   * **System Instruction:** "You are an AppSec Engineer. Only use the retrieved context."
   * **Context:** [The matched FAISS text chunks]
   * **User Input:** [The vulnerable Python code]
5. **LLM Generation (Llama 3):** This massive prompt is sent to `llama-3.1-8b-instant` via the high-speed Groq API using LangChain Expression Language (LCEL). By forcing Llama-3 to rely solely on the provided context, we mathematically eliminate hallucinations. 
6. **UI Output:** Streamlit renders the LLM's patched code *and* provides the exact OWASP citations it retrieved in an expandable menu for security transparency.

## 3. Tool Stack Breakdown (Why we chose them)
*   **LangChain (LCEL):** The glue holding the API calls and database connections together. We use LCEL (`RunnableParallel`, `RunnablePassthrough`) because it natively handles asynchronous API calling and makes reading RAG pipelines declarative and clean.
*   **FAISS:** Selected because it is an in-memory database that doesn't require setting up Docker containers (unlike Milvus or Qdrant), making it perfectly lightweight for a local developer tool.
*   **HuggingFace Embeddings:** Utilizing `all-MiniLM-L6-v2` because it's locally executable and extremely performant for semantic clustering. Crucial for enterprise security compliance where proprietary code cannot leave the local machine.
*   **Groq API (Llama-3):** Groq relies on LPUs (Language Processing Units) rather than GPUs, operating at 500+ tokens a second. Llama-3 was selected because it's an open-weights model heavily trained on coding and logic tasks.
*   **Streamlit:** Allows rapid prototyping of beautiful frontend applications entirely in Python, abstracting away React/CSS requirements.

