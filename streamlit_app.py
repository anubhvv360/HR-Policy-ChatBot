import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import GooglePalmEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
import os

# --- Streamlit App ---
st.set_page_config(page_title="HR Policy Bot", layout="wide")

# Utility: Initialize session state for vector store and chain
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'qa_chain' not in st.session_state:
    st.session_state.qa_chain = None

# Sidebar: Instructions
with st.sidebar:
    st.header("HR Policy Bot")
    st.write("Upload your HR policy PDFs or use the sample text to get started.")

# Main: File upload and text input
st.subheader("1. Provide HR Policies")
uploaded_files = st.file_uploader("Upload PDF files", type=['pdf'], accept_multiple_files=True)

# Pre-filled sample HR policy text
default_policy = '''
Company XYZ HR Policy

1. Recruitment and Selection
- Purpose: Ensure fair hiring practices.
- Scope: All permanent and contract employees.

2. Leave Policy
- Annual Leave: 24 days per year.
- Sick Leave: 10 days per year with medical certificate.

3. Code of Conduct
- Workplace Behavior: Respect, integrity, and professionalism.
- Anti-Harassment: Zero tolerance for harassment.

... (add more sections as needed)
'''
policy_text = st.text_area("Or paste your HR policy text here", value=default_policy, height=300)

# Button: Load policies into vector store
if st.button("Load Policies"):
    docs = []
    # Load PDFs if any
    for file in uploaded_files:
        loader = PyPDFLoader(file)
        loaded = loader.load()
        docs.extend(loaded)

    # Include free-text policy
    docs.append({ 'page_content': policy_text }) if policy_text else None

    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_documents(docs)

    # Create embeddings and vector store
    embeddings = GooglePalmEmbeddings()
    vectorstore = Chroma.from_documents(texts, embeddings, persist_directory="hr_policy_db")
    st.session_state.vectorstore = vectorstore

    # Build QA chain
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    st.session_state.qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4})
    )
    st.success("HR policies loaded successfully!")

# Q&A Interface
if st.session_state.qa_chain:
    st.subheader("2. Ask a question about your HR policies")
    query = st.text_input("Enter your question here")
    if query:
        with st.spinner("Thinking..."):
            answer = st.session_state.qa_chain.run(query)
        st.markdown("**Answer:**")
        st.write(answer)
else:
    st.info("Please load policies to enable Q&A.")

# Footer
st.markdown("---")
st.write("Built with Streamlit ❤ and Gemini LLM")
