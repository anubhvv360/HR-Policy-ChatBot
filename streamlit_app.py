import streamlit as st
import google.generativeai as genai
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import GooglePalmEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
import os

# --- App Config ---
st.set_page_config(page_title="HR Policy Bot", layout="wide")

# --- Google Gemini Setup ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found in Streamlit Secrets. Add it under Settings → Secrets.")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# --- Sidebar: Upload & Ingest Policies ---
with st.sidebar:
    st.header("Load HR Policies")
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
    '''
    policy_text = st.text_area(
        "Or paste HR policy text", value=default_policy, height=200
    )
    if st.button("Ingest Policies"):
        docs = []
        # Load PDF docs
        for pdf in uploaded_files:
            loader = PyPDFLoader(pdf)
            docs.extend(loader.load())
        # Include free-text policy
        if policy_text:
            docs.append(Document(page_content=policy_text, metadata={}))
        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        # Build vector store in-memory
        embeddings = GooglePalmEmbeddings(google_api_key=GEMINI_API_KEY)
        vectorstore = Chroma.from_documents(chunks, embeddings)
        st.session_state.vectorstore = vectorstore
        st.success("Policies ingested successfully!")

# --- Main: Chat Interface ---
st.title("💼 HR Policy Bot")
if "vectorstore" not in st.session_state:
    st.info("Please load HR policies from the sidebar to get started.")
else:
    # Initialize chat history
    if "history" not in st.session_state:
        st.session_state.history = []
    # Display chat history
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    # Accept user input
    if user_input := st.chat_input("Ask a question about HR policies..."):
        # Record user message
        st.session_state.history.append({"role": "user", "content": user_input})
        # Retrieve relevant policy chunks
        docs = st.session_state.vectorstore.similarity_search(user_input, k=4)
        context = "\n\n".join([d.page_content for d in docs])
        prompt = (
            "You are an HR policy assistant. Use the following excerpts to answer the question."
            f"\n\n{context}\n\nQuestion: {user_input}"
        )
        # Stream assistant response
        full_response = ""
        with st.chat_message("assistant"):
            placeholder = st.empty()
            chat = model.start_chat()
            for chunk in chat.send_message(prompt, stream=True):
                for word in chunk.text.split(" "):
                    full_response += word + " "
                    placeholder.write(full_response + "▌")
            placeholder.write(full_response)
        # Save assistant message
        st.session_state.history.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
st.caption("Built with Streamlit 💖 and Google Gemini")
