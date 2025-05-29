import streamlit as st
import google.generativeai as genai
import pypdf

# --- App Config ---
st.set_page_config(page_title="HR Policy Bot", layout="wide")

# --- Google Gemini Setup ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found in Streamlit Secrets. Add it under Settings → Secrets.")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Load HR Policies ---
st.sidebar.header("1. Load HR Policies")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF files", type=["pdf"], accept_multiple_files=True
)
#policy_input = st.sidebar.text_area(
#    "Or paste HR policy text here", height=200
#)

if st.sidebar.button("Load Policies"):
    combined_text = ""
    # Read PDFs
    for pdf in uploaded_files:
        reader = pypdf.PdfReader(pdf)
        for page in reader.pages:
            text = page.extract_text() or ""
            combined_text += text + "\n"
    # Append free-text policy
    combined_text += policy_input
    st.session_state.policy_text = combined_text
    st.sidebar.success("Policies loaded into the bot!")

# --- Chat Interface ---
st.title("💼 HR Policy Bot")

if 'policy_text' not in st.session_state or not st.session_state.policy_text:
    st.info("Please load your HR policy (PDF or text) from the sidebar to begin.")
else:
    user_question = st.text_input("Ask a question about your HR policies...")
    if user_question:
        prompt = (
            "You are an HR policy assistant. Read the policy below and answer the question concisely.\n\n"
            f"{st.session_state.policy_text}\n\nQuestion: {user_question}\nAnswer:")
        # Send prompt to Gemini
        chat = model.start_chat()
        response = chat.send_message(prompt)
        # Extract text
        answer = getattr(response, 'text', None) or response.parts[0].text
        st.markdown(f"**Answer:** {answer}")

# --- Footer ---
st.caption("Built with Streamlit 💖 and Google Gemini")
