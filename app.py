import json
import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_tavily import TavilySearch

load_dotenv()

st.set_page_config(page_title="Simple Chatbot", page_icon="💬")
st.title("Simple Chatbot")

use_web_search = st.sidebar.checkbox("Use web search (Tavily)", value=False)
if use_web_search and not os.environ.get("TAVILY_API_KEY"):
    st.sidebar.error("Set TAVILY_API_KEY in your .env file to use web search.")

@st.cache_resource
def load_model():
    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
        task="text-generation",
        max_new_tokens=512,
    )
    return ChatHuggingFace(llm=llm)


@st.cache_resource
def load_search_tool():
    return TavilySearch(max_results=5, search_depth="basic")


model = load_model()

SYSTEM_PROMPT = (
    "You are a helpful AI assistant. "
    "When the user's message includes web search results, answer from those results "
    "when possible and cite sources by title and URL. If the results are insufficient, say so."
)


def parse_tavily_payload(raw):
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"results": []}
    if isinstance(raw, dict):
        return raw
    return {"results": []}


def format_tavily_snippets(data):
    results = data.get("results") or []
    blocks = []
    for i, r in enumerate(results, 1):
        title = r.get("title") or "Untitled"
        url = r.get("url") or ""
        content = r.get("content") or ""
        blocks.append(f"[{i}] {title} ({url})\n{content}")
    return "\n\n".join(blocks).strip()


def build_invoke_messages(chat_messages, user_input, use_search):
    invoke_messages = list(chat_messages)
    if not use_search or not os.environ.get("TAVILY_API_KEY"):
        return invoke_messages, None

    try:
        raw = load_search_tool().invoke({"query": user_input})
    except Exception as e:
        raise RuntimeError(f"Tavily search failed: {e}") from e

    data = parse_tavily_payload(raw)
    snippets = format_tavily_snippets(data)
    augmented = (
        "Web search results (use these; cite sources when relevant):\n"
        f"{snippets}\n\n"
        f"User question: {user_input}"
    )
    if invoke_messages and isinstance(invoke_messages[-1], HumanMessage):
        invoke_messages[-1] = HumanMessage(content=augmented)

    system_extended = (
        SYSTEM_PROMPT
        + " Prioritize the web search snippets in this turn; do not invent facts beyond them."
    )
    if invoke_messages and isinstance(invoke_messages[0], SystemMessage):
        invoke_messages[0] = SystemMessage(content=system_extended)

    return invoke_messages, data.get("results") or []


if "chat" not in st.session_state:
    st.session_state.chat = [SystemMessage(content=SYSTEM_PROMPT)]

if st.button("Clear Chat"):
    st.session_state.chat = [SystemMessage(content=SYSTEM_PROMPT)]
    st.rerun()


for msg in st.session_state.chat:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)


user_input = st.chat_input("You:")

if user_input:
    st.session_state.chat.append(HumanMessage(content=user_input))

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        if use_web_search and not os.environ.get("TAVILY_API_KEY"):
            st.error(
                "Web search is enabled but TAVILY_API_KEY is not set. "
                "Add it to your .env file or turn off the sidebar toggle."
            )
            err_text = (
                "I could not run web search because TAVILY_API_KEY is missing from the environment."
            )
            st.session_state.chat.append(AIMessage(content=err_text))
        else:
            sources = None
            try:
                if use_web_search:
                    with st.spinner("Searching the web..."):
                        invoke_messages, sources = build_invoke_messages(
                            st.session_state.chat, user_input, use_search=True
                        )
                    with st.spinner("Thinking..."):
                        result = model.invoke(invoke_messages)
                else:
                    with st.spinner("Thinking..."):
                        result = model.invoke(st.session_state.chat)
            except RuntimeError as e:
                st.error(str(e))
                result = type("obj", (), {"content": f"Search error: {e}"})()
                sources = None

            st.write(result.content)
            if sources:
                with st.expander("Sources"):
                    for r in sources:
                        title = r.get("title") or "Link"
                        url = r.get("url") or "#"
                        st.markdown(f"- [{title}]({url})")

            st.session_state.chat.append(AIMessage(content=result.content))
