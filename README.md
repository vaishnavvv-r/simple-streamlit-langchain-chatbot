# 💬 Simple Streamlit Chatbot using LangChain & HuggingFace

A minimal chatbot built using **Streamlit**, **LangChain**, and **Hugging Face LLMs**.  
The chatbot maintains a simple chat history and provides a clean UI similar to ChatGPT.

---

## 🚀 Features

- 🧠 Powered by **Meta LLaMA-3-8B-Instruct**
- 💬 ChatGPT-style UI using Streamlit
- 🗂️ Simple chat history (no complex memory)
- 🧹 Clear Chat button
- 🔐 Secure environment variable handling
- ⚡ Efficient model loading with caching
- 🌐 Optional **Tavily** web search (sidebar toggle) for up-to-date answers

---

## Environment variables

Create a `.env` file next to `app.py` (see `.gitignore` — do not commit secrets):

| Variable | Required | Purpose |
|----------|----------|---------|
| `HF_TOKEN` or `HUGGINGFACEHUB_API_TOKEN` | Yes | Hugging Face Inference API for the LLM |
| `TAVILY_API_KEY` | Only if using web search | [Tavily](https://app.tavily.com/) Search API |

With **Use web search (Tavily)** enabled in the sidebar, each message runs a Tavily search first; snippets are injected into the model prompt for that turn only. Chat history still shows the plain user question. A **Sources** expander lists result links when search was used.

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **LangChain**
- **HuggingFace Inference API**
- **Meta-Llama-3-8B-Instruct**
- **Tavily Search** (optional)

---

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---
link: https://simple-app-langchain-chatbot-sjsvpj65xbdw9pjvkp4nnk.streamlit.app/
