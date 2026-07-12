import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

import streamlit as st
from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

load_dotenv()

ROOT = Path(__file__).resolve().parent
KNOWLEDGE_BASE_PATH = ROOT / "knowledge_base.json"


@st.cache_data(show_spinner=False)
def load_knowledge_base(path: Path) -> Dict[str, List[Dict[str, str]]]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


KNOWLEDGE_BASE = load_knowledge_base(KNOWLEDGE_BASE_PATH)


def find_kb_matches(query: str) -> List[Dict[str, str]]:
    lowered_query = query.lower()
    if re.search(r"\b(forgot|reset|recover)\b", lowered_query) and re.search(r"\bpassword\b", lowered_query):
        matches: List[Dict[str, str]] = []
        for category in KNOWLEDGE_BASE.values():
            for entry in category:
                title = entry.get("title", "").lower()
                summary = entry.get("summary", "").lower()
                if "password" in title or "password" in summary:
                    matches.append(entry)
        return matches[:3]

    if any(term in lowered_query for term in ("login", "log in", "sign in", "signin", "cannot access", "access")):
        return []

    query_tokens = set(re.findall(r"[a-z0-9]+", lowered_query))
    matches = []
    for category in KNOWLEDGE_BASE.values():
        for entry in category:
            entry_text = " ".join(
                [entry.get("title", ""), entry.get("summary", ""), entry.get("keywords", "")]
            ).lower()
            entry_tokens = set(re.findall(r"[a-z0-9]+", entry_text))
            entry_tokens = {token for token in entry_tokens if len(token) > 2}
            if query_tokens & entry_tokens:
                matches.append(entry)
    return matches[:3]


def should_escalate(query: str, matches: List[Dict[str, str]], history: List[Dict[str, str]]) -> bool:
    lowered_query = query.lower()
    escalation_terms = [
        "refund",
        "charge",
        "billing",
        "payment",
        "cancel",
        "subscription",
        "security",
        "data loss",
        "data",
        "urgent",
        "human",
        "representative",
        "suspicious",
        "cannot access",
        "locked out",
        "crash",
        "broken",
        "bug",
        "error",
    ]
    # escalate only when the query contains clear escalation signals
    if any(term in lowered_query for term in escalation_terms):
        return True
    # if the user explicitly asks for a human/representative, escalate
    if any(x in lowered_query for x in ("human", "representative", "agent", "support specialist")):
        return True
    return False


def build_follow_up_question(query: str, matches: List[Dict[str, str]], history: List[Dict[str, str]]) -> str:
    if not matches:
        return "Could you tell me which product or service you are using and what you expected to happen?"
    if "billing" in query.lower() or "charge" in query.lower():
        return "Can you share the billing issue in more detail, such as the date of the charge or the plan you are on?"
    if "login" in query.lower() or "password" in query.lower() or "access" in query.lower():
        return "Are you seeing a specific error message when trying to sign in?"
    return "What happened right before the issue started, and what steps have you already tried?"


def build_escalation_summary(query: str, history: List[Dict[str, str]], matches: List[Dict[str, str]]) -> str:
    recent_context = " | ".join(item["content"] for item in history[-4:])
    match_summaries = "; ".join(entry.get("title", "") for entry in matches[:3])
    return (
        f"Customer issue: {query}\n"
        f"Context: {recent_context}\n"
        f"Relevant knowledge base matches: {match_summaries or 'None'}"
    )


def generate_support_response(query: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    matches = find_kb_matches(query)
    # Only escalate for clear escalation signals
    if should_escalate(query, matches, history):
        summary = build_escalation_summary(query, history, matches)
        return (
            "I’m escalating this to a human support specialist because it looks complex or sensitive. "
            f"Here is a summary for the next agent:\n\n{summary}",
            True,
        )

    # If we have no KB matches, ask a follow-up instead of escalating immediately.
    if not matches:
        lowered = query.lower()
        # Common non-escalation user intents we can clarify for
        if any(x in lowered for x in ("discount", "student", "promo", "coupon")):
            return (
                "I don't see any information about discounts in the knowledge base. "
                "I can check current promotions or escalate this to billing — would you like me to do that?",
                False,
            )
        follow_up = build_follow_up_question(query, matches, history)
        return f"I want to help, but I need a bit more context. {follow_up}", False

    top_match = matches[0]
    response = (
        f"Based on the knowledge base, {top_match.get('title', 'this issue')} appears to be the closest match.\n"
        f"{top_match.get('summary', '')}\n\n"
        f"Suggested next step: {top_match.get('resolution', 'Please contact support if this persists.')}"
    )

    if len(matches) > 1:
        response += "\n\nI also found a couple of related articles that may help."

    return response, False


def llm_enhanced_response(query: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key or not api_key.strip() or OpenAI is None:
        return generate_support_response(query, history)

    try:
        base_url = os.getenv("LLM_BASE_URL")
        if base_url:
            base_url = base_url.rstrip("/")
            if base_url.endswith("/chat/completions"):
                base_url = base_url.rsplit("/chat/completions", 1)[0]
        model = os.getenv("LLM_MODEL") or "gpt-4o-mini"
        client = OpenAI(api_key=api_key, base_url=base_url)
        system_prompt = SYSTEM_PROMPT
        history_text = "\n".join(f"{item['role']}: {item['content']}" for item in history[-6:])
        completion = client.chat.completions.create(
            model=model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Knowledge base context:\n{json.dumps(KNOWLEDGE_BASE)}\n\nConversation:\n{history_text}\n\nCustomer message:\n{query}"},
            ],
        )
        answer = completion.choices[0].message.content or ""
        if "escalat" in answer.lower() or "human agent" in answer.lower():
            return answer, True
        return answer, False
    except Exception:
        return generate_support_response(query, history)


def reset_session() -> None:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I can help with product questions, troubleshooting, or routing complex issues to a human agent.",
        }
    ]


if "messages" not in st.session_state:
    reset_session()


st.set_page_config(page_title="Customer Support AI Agent", page_icon="🤖", layout="wide")
st.title("Customer Support AI Agent")
st.caption("Chat or voice support assistant with a built-in troubleshooting knowledge base")

with st.sidebar:
    st.header("Controls")
    st.info("Set your OpenRouter API key and model in the .env file to enable LLM-powered responses.")
    if st.button("Clear conversation"):
        reset_session()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_input = st.chat_input("Ask a customer support question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response, escalated = llm_enhanced_response(user_input, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

    if escalated:
        st.success("Complex issue escalated and summarized for a human agent.")


st.markdown("\n---")
st.caption("Tip: add your OpenRouter API key and model to .env and restart the app for full LLM support.")
