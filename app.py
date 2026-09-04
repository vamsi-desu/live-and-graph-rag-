import streamlit as st

from router import route_question
from structured_rag import structured_rag_query
from graph_rag import graph_rag_query
from live_rag import live_rag_query


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Employee AI Assistant",
    page_icon="🤖",
    layout="wide"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown(
    """
    <style>

    /* Main page */
    .main {
        padding-top: 1rem;
    }

    /* Header */
    .app-header {
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(128,128,128,0.25);
    }

    .app-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .app-subtitle {
        font-size: 1rem;
        opacity: 0.7;
    }

    /* Retrieval badge */
    .retrieval-badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
        border: 1px solid rgba(128,128,128,0.3);
    }

    /* Sidebar */
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 700;
    }

    /* Footer */
    .footer {
        text-align: center;
        opacity: 0.55;
        font-size: 0.8rem;
        margin-top: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# HEADER
# ==================================================

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">
            🤖 Employee AI Assistant
        </div>
        <div class="app-subtitle">
            Intelligent employee assistant powered by Structured RAG,
            Graph RAG and Live RAG
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">🔧 AI Architecture</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### 📊 Structured RAG")
    st.caption("Employee information from SQLite")

    st.markdown("### 🔗 Graph RAG")
    st.caption("Employee relationships using NetworkX")

    st.markdown("### 🌤️ Live RAG")
    st.caption("Real-time weather information")

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):

        st.session_state.messages = []

        st.rerun()


# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==================================================
# DISPLAY CHAT HISTORY
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("strategy"):

            st.markdown(
                f"""
                <div class="retrieval-badge">
                    🔎 {message["strategy"]}
                </div>
                """,
                unsafe_allow_html=True
            )


# ==================================================
# QUERY FUNCTION
# ==================================================

def process_question(question):

    # ----------------------------------------------
    # STEP 1: ROUTER
    # ----------------------------------------------

    route = route_question(question)

    strategy = route.get("strategy")

    # ----------------------------------------------
    # STEP 2: STRUCTURED RAG
    # ----------------------------------------------

    if strategy == "structured_rag":

        answer = structured_rag_query(
            question=question,
            employee_id=route.get("employee_id"),
            department=route.get("department"),
            location=route.get("location"),
            status=route.get("status")
        )

        return answer, strategy

    # ----------------------------------------------
    # STEP 3: GRAPH RAG
    # ----------------------------------------------

    if strategy == "graph_rag":

        employee_name = route.get("employee_name")

        if not employee_name:

            return (
                "I couldn't identify the employee in your question.",
                strategy
            )

        answer = graph_rag_query(
            question,
            employee_name
        )

        return answer, strategy

    # ----------------------------------------------
    # STEP 4: LIVE RAG
    # ----------------------------------------------

    if strategy == "live_rag":

        city = route.get("city")

        if not city:

            return (
                "I couldn't identify the city in your question.",
                strategy
            )

        answer = live_rag_query(
            question=question,
            city=city
        )

        return answer, strategy

    # ----------------------------------------------
    # UNKNOWN
    # ----------------------------------------------

    return (
        "I couldn't determine which retrieval strategy to use.",
        strategy
    )


# ==================================================
# CHAT INPUT
# ==================================================

question = st.chat_input(
    "Ask about employees, relationships, or live weather..."
)


if question:

    # ----------------------------------------------
    # USER MESSAGE
    # ----------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    # ----------------------------------------------
    # ASSISTANT RESPONSE
    # ----------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                answer, strategy = process_question(
                    question
                )

                st.markdown(answer)

                st.markdown(
                    f"""
                    <div class="retrieval-badge">
                        🔎 {strategy}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "strategy": strategy
                    }
                )

            except Exception as e:

                error_message = (
                    f"Something went wrong: {str(e)}"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )


# ==================================================
# FOOTER
# ==================================================

st.markdown(
    """
    <div class="footer">
        Employee AI Assistant • Structured RAG • Graph RAG • Live RAG
    </div>
    """,
    unsafe_allow_html=True
)

