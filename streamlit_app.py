import streamlit as st
import google.generativeai as genai
import pypdf

# --- App Config ---
st.set_page_config(page_title="HR Policy Bot", layout="wide")

# --- Google Generative AI Setup ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found in Streamlit Secrets. Add it under Settings → Secrets.")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)

# --- Sidebar: Load HR Policies ---
st.sidebar.header("1. Load HR Policies")
uploaded_files = st.sidebar.file_uploader(
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
'''
policy_text_input = st.sidebar.text_area(
    "Or paste HR policy text here", value=default_policy, height=200
)
if st.sidebar.button("Load Policies"):
    combined_text = ""
    # Extract text from PDFs
    for pdf_file in uploaded_files:
        reader = pypdf.PdfReader(pdf_file)
        for page in reader.pages:
            combined_text += (page.extract_text() or "") + ""

    # Append free-text policy
    combined_text += policy_text_input
    st.session_state.policy_text = combined_text
    st.sidebar.success("Policies loaded into the bot!")

# --- Main: Chat Interface ---
st.title("💼 HR Policy Bot")
if 'policy_text' not in st.session_state:
    st.info("Please load your HR policy (PDF or text) from the sidebar to begin.")
else:
    user_question = st.text_input("Ask a question about your HR policies...")
    if user_question:
        # Build prompt
        prompt = (
            "You are an HR policy assistant. Read the policy below and answer concisely." +
            f"{st.session_state.policy_text}

Question: {user_question}
Answer:")
        # Generate answer
        response = genai.generate_text(
            model="text-bison-001",
            prompt=prompt,
        )
        # Extract response text
        answer = getattr(response, 'text', None) or response
        st.markdown(f"**Answer:** {answer}")

# --- Footer ---
st.caption("Built with Streamlit 💖 and Google Generative AI")
