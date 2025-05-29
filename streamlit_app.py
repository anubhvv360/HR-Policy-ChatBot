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
# Configure the Google Generative AI client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Sidebar: Load HR Policies ---
st.sidebar.header("1. Load HR Policies")
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

# Loop through files and create download buttons
for filename, url in files.items():
    download_file_from_github(url, filename)

# --- Footer ---
st.caption("Built with Streamlit 💖 and Google Gemini")
