# 🤖 Customer Support AI Agent

An AI-powered **Customer Support Assistant** built with **Streamlit** and an **OpenRouter/OpenAI-compatible LLM**. The application answers product and service-related questions using a local knowledge base, asks intelligent follow-up questions to better understand customer issues, troubleshoots common problems, and escalates complex cases with concise summaries for human support agents.

---

## ✨ Features

- 💬 AI-powered customer support chatbot
- 📚 Knowledge base-driven question answering
- ❓ Intelligent follow-up questions for better issue resolution
- 🛠️ Troubleshooting guidance for common technical issues
- 📄 Automatic escalation summaries for complex cases
- 🔍 Local knowledge base with keyword matching
- 🤖 Optional OpenRouter/OpenAI LLM integration
- ⚡ Fast responses with built-in fallback logic
- 🎨 Clean and responsive Streamlit interface

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **OpenRouter API / OpenAI API**
- **Large Language Models (LLMs)**
- **JSON Knowledge Base**
- **python-dotenv**
- **unittest**

---

## 📂 Project Structure

```text
.
├── app.py
├── knowledge_base.json
├── requirements.txt
├── tests/
│   └── test_app.py
├── .env.example
└── README.md
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/customer-support-ai-agent.git
cd customer-support-ai-agent
```

Create and activate a virtual environment.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENAI_API_KEY=your_openai_api_key
LLM_BASE_URL=https://openrouter.ai/api/v1/chat/completions
LLM_MODEL=your_model_name
```

> **Note:** If no API key is configured, the application automatically falls back to the built-in knowledge base for answering customer queries.

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

---

## 🎯 How It Works

1. The user submits a support question.
2. The application searches the local knowledge base for relevant information.
3. If additional information is needed, the AI asks follow-up questions.
4. Common issues are resolved using predefined troubleshooting steps.
5. Sensitive or unresolved issues are summarized and escalated to a human support agent.
6. When configured, the LLM enhances responses with conversational explanations.

---

---

## 🌟 Future Enhancements

- 🎙️ Voice-enabled customer support
- 🌐 Multi-language support
- 📄 PDF conversation summaries
- 📊 Customer analytics dashboard
- 🎫 Ticket management integration
- 🔎 Semantic search with vector database
- 📧 Email and Slack support integration
- 🤝 CRM integration (Zendesk, Freshdesk, Salesforce)

---

Deployed link : https://customer-support-ai-agent-ii5dpcxqqole54vevntxtc.streamlit.app/

## ⚠️ Disclaimer

The AI assistant provides guidance based on the configured knowledge base and language model. Responses should be reviewed before being used in production environments. Sensitive issues such as security breaches, legal matters, or data loss should always be escalated to a qualified human support representative.

---

⭐ If you found this project useful, consider giving it a **Star** on GitHub!

The application will automatically open in your default browser.

---
