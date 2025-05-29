import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import GooglePalmEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.llms import GoogleGemini
from langchain.chains import RetrievalQA
import os

# --- Streamlit App Configuration ---
st.set_page_config(page_title="HR Policy Bot", layout="wide")

# Fetch Gemini API key from Streamlit secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found in Streamlit secrets. Please add it under Settings → Secrets.")
    st.stop()

# Initialize session state for vector store and QA chain
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

# Sidebar UI
with st.sidebar:
    st.title("HR Policy Bot")
    st.write("Upload your HR policy PDFs or use the sample text below to get started.")

# Main UI: Document input
st.header("1. Provide HR Policies")
uploaded_files = st.file_uploader(
    "Upload PDF files", type=["pdf"], accept_multiple_files=True
)

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

4. Performance Management
- Annual reviews and goal-setting process.
- Feedback mechanism: Quarterly check-ins.

5. Compensation & Benefits
- Salary structure, pay grades, and bonus eligibility.
- Health insurance, retirement plans, and perks.

... (add more sections as needed)
'''
policy_text = st.text_area(
    "Or paste your HR policy text here", value=default_policy, height=300
)

# Load policies into the vector store
if st.button("Load Policies"):
    docs = []
    # Load PDF documents
    for pdf in uploaded_files:
        loader = PyPDFLoader(pdf)
        docs.extend(loader.load())

    # Include free-text policy as a Document
    if policy_text:
        docs.append(Document(page_content=policy_text, metadata={}))

    # Split docs into text chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    # Generate embeddings and build Chroma vector store
    embeddings = GooglePalmEmbeddings(api_key=GEMINI_API_KEY)
    vectorstore = Chroma.from_documents(
        chunks, embeddings, persist_directory="hr_policy_db"
    )
    vectorstore.persist()
    st.session_state.vectorstore = vectorstore

    # Prepare the RetrievalQA chain
    llm = GoogleGemini(
        model_name="gemini-2.0-flash", api_key=GEMINI_API_KEY, temperature=0
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4})
    )
    st.session_state.qa_chain = qa_chain
    st.success("HR policies loaded successfully!")

# Q&A interface
if st.session_state.qa_chain:
    st.header("2. Ask a question about your HR policies")
    query = st.text_input("Enter your question here")
    if query:
        with st.spinner("Generating answer..."):
            answer = st.session_state.qa_chain.run(query)
        st.subheader("Answer")
        st.write(answer)
else:
    st.info("Please load policies to enable Q&A.")

# Footer
st.markdown("---")
st.caption("Built with Streamlit 💖 and Google Gemini")
