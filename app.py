import streamlit as st
from twin import chat, ConversationHistory

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Thomas He — Digital Twin",
    page_icon="🤖",
    layout="centered"
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🤖 Thomas He — Digital Twin")
st.caption(
    "Ask me anything about my research, projects, opinions, or background."
)
st.divider()

# ── Session State Init ────────────────────────────────────────────────────────
# Streamlit reruns the entire script on every interaction,
# so we use session_state to persist history across reruns
if "history" not in st.session_state:
    st.session_state.history = ConversationHistory()

if "messages" not in st.session_state:
    st.session_state.messages = []  # display messages for UI rendering

# ── Render Chat History ───────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat Input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask Thomas something...")

if user_input:
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Add to display history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat(
                user_input,
                st.session_state.history
            )
        st.markdown(response)

    # Add to display history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("About this Twin")
    st.write(
        "This is a digital twin of Thomas He, powered by RAG "
        "over his personal knowledge base and GPT-4o-mini."
    )

    st.divider()

    # Show conversation turn count
    turn_count = len(st.session_state.messages) // 2
    st.metric("Conversation Turns", turn_count)

    st.divider()

    # Clear history button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.history.clear()
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # Debug panel — shows retrieved chunks for last query
    if st.toggle("🔍 Show Retrieved Context"):
        if st.session_state.messages:
            last_user_msg = next(
                (m["content"] for m in reversed(st.session_state.messages)
                 if m["role"] == "user"),
                None
            )
            if last_user_msg:
                from retriever import retrieve
                context = retrieve(last_user_msg)
                st.subheader("Retrieved Chunks")
                st.text(context)
        else:
            st.info("No conversation yet.")