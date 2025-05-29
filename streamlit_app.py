import streamlit as st
import google.generativeai as genai
import pypdf
import requests  # for downloading sample HR manual

# Set page configuration
st.set_page_config(
    page_title="HR Policy Bot",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Google Gemini Setup ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found in Streamlit Secrets. Add it under Settings → Secrets.")
    st.stop()
# Configure the Google Generative AI client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Sidebar: Load HR Policies ---
st.sidebar.subheader("Get a Sample HR Manual")
# Button to download sample HR manual from GitHub
sample_url = "https://raw.githubusercontent.com/anubhvv360/HR-Policy-ChatBot/main/Data/hr_policy_manual.pdf"
try:
    sample_pdf = requests.get(sample_url).content
    st.sidebar.download_button(
        label="Download Sample HR Manual",
        data=sample_pdf,
        file_name="hr_policy_manual.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.sidebar.error(f"Could not fetch sample manual: {e}")

# Only PDF upload option
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF files", type=["pdf"], accept_multiple_files=True
)

if st.sidebar.button("Load Policies"):
    if not uploaded_files:
        st.sidebar.warning("Please upload at least one PDF file.")
    else:
        combined_text = ""
        # Read and concatenate PDF text
        for pdf in uploaded_files:
            reader = pypdf.PdfReader(pdf)
            for page in reader.pages:
                combined_text += (page.extract_text() or "") + "\n"
        st.session_state.policy_text = combined_text
        st.sidebar.success("Policies loaded into the bot!")

# --- Main: Chat Interface ---
st.title("💼 HR Policy Bot")

if 'policy_text' not in st.session_state or not st.session_state.policy_text:
    st.info("Please upload your HR policy PDF in the sidebar to begin.")
else:
    user_question = st.text_input("Ask a question about your HR policies...")
    if user_question:
        prompt = (
            "You are an HR policy assistant. Read the policy below and answer the question concisely.\n\n"
            f"{st.session_state.policy_text}\n\nQuestion: {user_question}\nAnswer:")
        # Send prompt to Gemini chat and get response
        chat = model.start_chat()
        response = chat.send_message(prompt)
        # Extract and display the answer
        answer = getattr(response, 'text', None) or response.parts[0].text
        st.markdown(f"**Answer:** {answer}")
# --- Sidebar: About & Load HR Policies ---
st.sidebar.title("ℹ️ About This App")
st.sidebar.markdown("""
HR Policy Bot lets you upload your HR policy PDFs and chat with an AI assistant to get concise answers grounded in your documents.
""")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📦 Library Versions")
st.sidebar.markdown(f"🔹 **Streamlit**: {st.__version__}")
st.sidebar.markdown(f"🔹 **Google Generative AI**: {genai.__version__ if hasattr(genai, '__version__') else 'N/A'}")
st.sidebar.markdown(f"🔹 **pypdf**: {pypdf.__version__}")
st.sidebar.markdown(f"🔹 **requests**: {requests.__version__}")
st.sidebar.markdown("### 💡 Tips for Best Results")
st.sidebar.markdown("""
- Upload clear, text-based PDF manuals for accurate extraction.
- Keep individual PDF file sizes under 10MB.
- Ask specific, concise questions for precise answers.
- For broad policy overviews, include fewer documents at a time.
""")
st.sidebar.markdown("---")
st.sidebar.markdown("Have feedback? [Reach out!](mailto:anubhav.verma360@gmail.com) 😊", unsafe_allow_html=True)
st.sidebar.caption("Disclaimer: This tool provides assistance but may not reflect official legal advice.")
# --- Footer ---
st.markdown("""
    <style>
    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .animated-gradient {
        background: linear-gradient(90deg, blue, purple, blue);
        background-size: 300% 300%;
        animation: gradientAnimation 8s ease infinite;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-top: 20px;
        color: white;
        font-weight: normal;
        font-size: 18px;
    }
    </style>

    <div class="animated-gradient">
        Made with ❤️ by Anubhav Verma
    </div>
""", unsafe_allow_html=True)
