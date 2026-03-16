import streamlit as st
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Secure Code Assistant", page_icon="🛡️")

st.title("Secure Code & OWASP Assistant")
st.markdown("I am an AI Security Agent. Paste your code or ask a question about vulnerabilities, and I will analyze it against OWASP Top 10 standards.")

DB_DIR = "faiss_index"

@st.cache_resource
def load_vector_store():
    if not os.path.exists(DB_DIR):
        return None
    # Use the same embedding model we used to create the DB
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # allow_dangerous_deserialization is needed for loading local FAISS in new LangChain versions
    db = FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)
    return db

db = load_vector_store()

if not db:
    st.error("Vector database not found! Please run the creation script first.")
else:
    # We use Groq API for Llama-3 because it runs incredibly fast and is free.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.warning("To power the AI, we need a Groq API Key (it's free!).")
        api_key = st.text_input("Enter your GROQ_API_KEY:", type="password")
    
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
        # Initialize Llama-3.1 via Groq for high-speed inference
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

        # The RAG Prompt: Telling the AI to ONLY use our OWASP data
        system_prompt = (
            "You are an expert Application Security Engineer and Secure Code Reviewer. "
            "Use the following pieces of retrieved OWASP documentation to analyze the user's input. "
            "If the provided context does not contain the answer, say you do not know. Do not hallucinate. "
            "Always identify the exact vulnerability name, explain the risk, and provide a secure code fix.\n\n"
            "Context (OWASP Guidelines):\n{context}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        # LCEL for Retrieval Augmented Generation
        retriever = db.as_retriever(search_kwargs={"k": 2})
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
            | prompt
            | llm
            | StrOutputParser()
        )

        rag_chain = RunnableParallel(
            {"context": retriever, "input": RunnablePassthrough()}
        ).assign(answer=rag_chain_from_docs)

        # Chat interface
        user_input = st.text_area("Enter Python/JS code or a security question here:", height=150)
        
        if st.button("Analyze Security", type="primary"):
            if user_input:
                with st.spinner("Analyzing against OWASP guidelines..."):
                    try:
                        response = rag_chain.invoke(user_input)
                        
                        st.markdown("### 🔍 Analysis & Fixes")
                        st.write(response["answer"])
                        
                        # Transparency feature: Displaying the RAG citation
                        with st.expander("📚 View Retrieved OWASP Sources"):
                            st.info("The AI generated the answer above using these exact documents from our Knowledge Base:")
                            for i, doc in enumerate(response["context"]):
                                st.markdown(f"**Source {i+1}:**")
                                st.code(doc.page_content, language='markdown')
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
            else:
                st.warning("Please enter some code or a question.")
