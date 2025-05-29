import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import VertexAIEmbeddings
from langchain.vectorstores import FAISS
#from langchain.chat_models import ChatGoogleGenerativeAI
from langchain.chat_models import ChatVertexAI
from langchain.chains import RetrievalQA
import tempfile

# ─── PAGE SETUP ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Policies Chatbot",
    layout="wide",
    page_icon="💬"
)
st.title("🤖 HR Policies Chatbot")
st.write("Ask questions about your company's HR policies with ease.")

# ─── DOCUMENT UPLOAD & INDEXING ───────────────────────────────────────────────────

uploaded_file = st.file_uploader(
    "Upload HR Policy Document (PDF)", type=["pdf"]
)

if uploaded_file:
    # Save uploaded PDF to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # 1. Load the document
    loader = PyPDFLoader(tmp_path)
    docs = loader.load()

    # 2. Split into passages
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)

    # 3. Embed and index
    embeddings = VertexAIEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)

    # 4. Setup RetrievalQA chain
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.2)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 4})
    )

    # ─── QUERY INTERFACE ───────────────────────────────────────────────────────────
    query = st.text_input("Enter your question about HR policies:")
    if query:
        with st.spinner("Searching policies..."):
            answer = qa_chain.run(query)
        st.markdown("**Answer:**")
        st.write(answer)

    # Optional: Display source passages
    if st.checkbox("Show source passages"):
        results = qa_chain.retriever.get_relevant_documents(query)
        for idx, doc in enumerate(results, start=1):
            st.markdown(f"**Source {idx}:**")
            st.write(doc.page_content)
else:
    st.info("Please upload a PDF of your HR policy documents to begin.")
