
# HR Policy Bot 📄

A lightweight Streamlit chatbot that lets you load your company’s HR policy documents (PDF only) and ask concise, AI-powered questions. Built with Google Generative AI for instant, accurate policy answers.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]((https://hr-policy-chatbot.streamlit.app/))

---

## Overview

HR Policy Bot simplifies access to your organization’s HR policies. Upload one or more PDF manuals, and the bot will extract the text and let you chat with an AI assistant powered by Google Gemini. No database or vector store required—just PDF ingestion and prompt-based retrieval.

---

## ⚙️ Features

- **PDF-Only Input**  
  Upload multiple HR policy PDFs directly via the sidebar.
- **Sample HR Manual**  
  Download a pre-filled sample policy for instant testing.
- **AI-Powered Q&A**  
  Pose natural-language questions about policies and receive concise answers.
- **Streamlined UI**  
  Simple sidebar workflow for loading policies and a main chat interface for queries.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/hr-policy-bot.git
cd hr-policy-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Your Google API Key
Add your Google Generative AI key under Streamlit Secrets:
```toml
# ~/.streamlit/secrets.toml
GEMINI_API_KEY = "YOUR_GOOGLE_API_KEY"
```

---

## 🏃‍♂️ Run the App

```bash
streamlit run streamlit_app.py
```

1. Use **Download Sample HR Manual** in the sidebar to grab a test PDF.  
2. Upload your own HR policy PDFs.  
3. Enter your question in the chat input and press Enter.  
4. View the AI-generated answer instantly.

---

## 🔧 Customization

- **Model**: Change `GenerativeModel("gemini-2.0-flash")` to another supported model if available.  
- **Prompt**: Modify the system prompt template in `streamlit_app.py` to tune answer style (e.g., bullet points, tone).

---

## 📄 License

This project is licensed under the MIT License. Feel free to adapt and extend!
