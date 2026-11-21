import os
import time
import streamlit as st

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="AI Agent | AquaSentinel AI",
    page_icon="🤖",
    layout="wide",
)

# ============================================================
# 2. PAGE-SCOPED VISUAL DESIGN
#    Keep styles scoped to this page so the shared app.py header
#    and theme.py styles are not unintentionally overridden.
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Do not style html/body/all Streamlit markdown globally here. */
    .agent-eyebrow,
    .agent-title,
    .agent-subtitle,
    .agent-status,
    .agent-footnote {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .agent-heading {
        padding-top: 0.7rem;
        padding-bottom: 0.2rem;
        position: relative;
        clear: both;
    }

    .agent-eyebrow {
        color: #5eead4;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        line-height: 1.5;
        margin: 0 0 0.55rem 0;
    }

    .agent-title {
        color: #f1f5f9;
        font-size: clamp(1.8rem, 3vw, 2.25rem);
        font-weight: 700;
        letter-spacing: -0.035em;
        line-height: 1.2;
        margin: 0 0 0.6rem 0;
    }

    .agent-subtitle {
        color: #a8b6c9;
        font-size: 1rem;
        line-height: 1.7;
        max-width: 850px;
        margin: 0;
    }

    .agent-status {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.42rem 0.78rem;
        border: 1px solid rgba(94,234,212,0.25);
        border-radius: 999px;
        background: rgba(20,184,166,0.09);
        color: #99f6e4;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 0.9rem 0 0.4rem;
    }

    .agent-status.local {
        border-color: rgba(148,163,184,0.25);
        background: rgba(148,163,184,0.08);
        color: #cbd5e1;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 16px;
        padding: 0.9rem 1.05rem;
        margin: 0.7rem 0;
        background: #142235;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        color: #e5edf7;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.94rem;
        line-height: 1.72;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p:last-child {
        margin-bottom: 0.15rem;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 {
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #123b3b;
        border-color: rgba(94,234,212,0.24);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #142235;
        border-color: rgba(96,165,250,0.20);
    }

    /* Quick-prompt buttons */
    div.stButton > button {
        border: 1px solid rgba(148,163,184,0.20);
        border-radius: 12px;
        background: #142235;
        color: #dbe7f5;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.84rem;
        font-weight: 500;
        min-height: 2.8rem;
        transition: border-color 0.18s ease, background 0.18s ease;
    }

    div.stButton > button:hover {
        border-color: #5eead4;
        color: #99f6e4;
        background: #183344;
    }

    /* Native Streamlit chat composer: remove the bright white dock. */
    [data-testid="stBottom"] {
        background: rgba(11,18,32,0.97) !important;
        border-top: 1px solid rgba(148,163,184,0.16) !important;
    }

    [data-testid="stBottom"] > div {
        background: transparent !important;
    }

    [data-testid="stChatInput"] {
        border: 1px solid rgba(94,234,212,0.34) !important;
        border-radius: 16px !important;
        background: #142235 !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.20) !important;
        overflow: hidden !important;
    }

    /* Streamlit uses a BaseWeb textarea wrapper inside the chat input.
       Style the wrapper as well as the outer component to avoid a white box. */
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] [data-baseweb="textarea"],
    [data-testid="stChatInput"] [data-baseweb="textarea"] > div {
        background: #142235 !important;
        border: 0 !important;
        box-shadow: none !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #f1f5f9 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #91a2b8 !important;
    }

    [data-testid="stChatInput"] button {
        color: #5eead4 !important;
    }

    [data-testid="stDivider"] {
        border-color: rgba(148,163,184,0.16);
    }

    .agent-footnote {
        color: #8293a9;
        font-size: 0.78rem;
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 3. GEMINI CONFIGURATION
# ============================================================
def get_gemini_client():
    """Create a Gemini client from an environment variable or Streamlit secret."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            api_key = None

    if not api_key:
        return None

    try:
        from google import genai
        from google.genai import types

        # Bound the network wait and disable SDK-level repeated attempts.
        http_options = types.HttpOptions(
            timeout=12000,
            retry_options=types.HttpRetryOptions(attempts=1),
        )
        return genai.Client(
            api_key=api_key,
            http_options=http_options,
        )
    except Exception as exc:
        # Keep the page usable if the SDK cannot initialize.
        st.session_state["gemini_init_error"] = (
            f"{type(exc).__name__}: {str(exc)[:220]}"
        )
        return None


client = get_gemini_client()

# ============================================================
# 4. PROJECT KNOWLEDGE
# ============================================================
PROJECT_CONTEXT = """
You are AquaSentinel AI, an urban water intelligence decision-support assistant.

AquaSentinel AI is an AI-powered predictive urban water intelligence and
equitable resource allocation prototype.

CORE WORKFLOW: Predict water demand; detect unusual consumption patterns;
optimize resource allocation; explain crisis scenarios and recommended actions.

DATASET: HSB Living Lab water consumption dataset: 652,315 records, 16 columns,
214 sensors, 28 apartments, 9 clusters, approximately 10-minute temporal
resolution, date range 2019-12-31 to 2023-01-31.

DATA LIMITATION: The dataset contains household and fixture-level consumption
records. It is not live municipal reservoir or pipeline telemetry.

FORECASTING: Evaluated pooled Random Forest test metrics: MAE 0.011779,
RMSE 0.018123, R-squared 0.847731. Persistence baseline: MAE 0.014345,
RMSE 0.022425, R-squared 0.766857.

ANOMALY DETECTION: Previously reported Isolation Forest analysis: 123,208
modelled records, 2,561 flagged anomalies, 211 affected sensors, 2.08% anomaly rate.

RESOURCE OPTIMIZATION: The allocator protects essential demand first and
distributes remaining supply using priority weights. It compares results
with proportional allocation and reports essential coverage, satisfaction,
unmet demand and fairness metrics. Treat all scenario results as synthetic
unless explicitly identified as measured data. Priority weights are policy
inputs, not automatically inferred income or vulnerability scores.

CRISIS SIMULATOR: Uses synthetic neighbourhood demand and supply to model
shortages, unmet demand, essential coverage and assumed supply recovery.

LIMITATIONS: Do not claim live municipal integration or real-time reservoir
monitoring. Do not invent model results or dataset observations. Clearly
distinguish measured dataset results from synthetic simulation scenarios.
Answer clearly, accurately and concisely. If information is unavailable, say so.
"""

# ============================================================
# 5. LOCAL DECISION SUPPORT
# ============================================================
def local_response(question):
    q = question.lower()

    if any(word in q for word in ["forecast", "prediction", "demand prediction", "future demand"]):
        return """### Demand Forecasting

AquaSentinel uses historical water-consumption patterns to estimate future demand.

The evaluated pooled Random Forest model achieved:
- Test MAE: 0.011779
- Test RMSE: 0.018123
- Test R²: 0.847731

Its reported test performance was better than the persistence baseline. These are historical dataset evaluation results, not guaranteed future municipal forecasts."""

    if any(word in q for word in ["anomaly", "leak", "unusual", "abnormal", "isolation forest"]):
        return """### Anomaly Detection

AquaSentinel uses Isolation Forest to identify unusual consumption patterns in sensor-level data.

Previously reported analysis:
- Modelled records: 123,208
- Flagged anomalies: 2,561
- Affected sensors: 211
- Anomaly rate: 2.08%

An anomaly is an investigation signal, not proof of a leak. Compare the sensor with its history and investigate persistent unusual readings."""

    if any(word in q for word in ["allocation", "optimization", "optimisation", "fairness", "distribute", "essential demand"]):
        return """### Equitable Resource Allocation

AquaSentinel follows an essential-needs-first allocation strategy.

1. **Stage 1:** Prioritise essential water requirements.
2. **Stage 2:** Distribute remaining supply using neighbourhood priority weights, subject to remaining demand.

The optimizer can be compared with proportional allocation using essential coverage, unmet demand and neighbourhood satisfaction. Results depend on the scenario inputs and policy weights; this does not guarantee better performance on every fairness metric."""

    if any(word in q for word in ["crisis", "drought", "shortage", "reservoir", "emergency", "recovery"]):
        return """### Water Crisis Management

The Crisis Simulator models supply shortages and recovery using synthetic neighbourhood inputs. It evaluates available supply, unmet demand, neighbourhood allocation, essential-demand coverage and assumed supply recovery.

The simulator does not use live reservoir measurements."""

    if any(word in q for word in ["dataset", "data", "hsb", "sensor"]):
        return """### HSB Living Lab Dataset

- 652,315 records
- 16 columns
- 214 sensors
- 28 apartments
- 9 clusters
- Approximately 10-minute temporal resolution
- Period: December 2019 to January 2023

The dataset contains household and fixture-level records, not city-wide municipal telemetry. Urban neighbourhood and infrastructure scenarios are supplemented with synthetic data."""

    if any(word in q for word in ["technology", "tech stack", "architecture", "built"]):
        return """### AquaSentinel AI — Technology

- Python, Pandas and NumPy for data processing and analysis
- Scikit-learn for machine learning
- Random Forest for demand forecasting
- Isolation Forest for anomaly detection
- Streamlit for the interactive application
- Plotly for interactive charts
- Essential-needs-first allocation algorithm
- Gemini for AI-assisted explanations when configured

**Workflow:** Predict → Detect → Optimize → Explain."""

    if any(word in q for word in ["hello", "hi", "hey"]):
        return "Hello! I am AquaSentinel AI. I can explain demand forecasting, anomaly detection, resource optimization, crisis simulations and the project dataset. What would you like to investigate?"

    return """I can help with AquaSentinel AI's four capabilities:

1. **Predict:** Historical water-demand forecasting.
2. **Detect:** Unusual consumption patterns.
3. **Optimize:** Essential-needs-first water allocation.
4. **Explain:** Water-shortage and recovery scenarios.

Ask me about any of these modules. Live sensor and municipal integrations are not currently available."""


# ============================================================
# 6. GEMINI RESPONSE
# ============================================================
def generate_response(question, history):
    """Generate a response with Gemini; use local answers only as an explicit fallback."""
    if client is None:
        init_error = st.session_state.get("gemini_init_error")
        if init_error:
            return (
                local_response(question),
                f"Local mode — Gemini client could not initialize ({init_error})",
            )
        return local_response(question), "Local mode — GEMINI_API_KEY not found"

    # Send one unambiguous prompt. This avoids malformed Gemini role sequences
    # when the saved chat history begins with an assistant greeting.
    recent_history = []
    for message in history[-8:]:
        role = "User" if message.get("role") == "user" else "AquaSentinel AI"
        text = str(message.get("content", "")).strip()
        if text:
            recent_history.append(f"{role}: {text}")

    history_text = "\\n".join(recent_history)
    prompt = f"""
{PROJECT_CONTEXT}

CONVERSATION SO FAR:
{history_text if history_text else "(No previous conversation.)"}

CURRENT USER QUESTION:
{question}

INSTRUCTIONS:
Answer the current question using the project context and relevant conversation
history. Be precise, concise and conversational. Do not invent facts or claim
live municipal integrations. Clearly label synthetic scenario assumptions.
"""

    # Make one bounded Gemini request. Temporary overloads or timeouts
    # fall back promptly instead of keeping the Streamlit page waiting.
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )
        answer = getattr(response, "text", None)

        if answer and answer.strip():
            return answer.strip(), "Gemini AI response"

        return (
            local_response(question),
            "Local fallback — Gemini returned an empty response",
        )

    except Exception as exc:
        error_detail = f"{type(exc).__name__}: {str(exc)[:180]}"
        return (
            local_response(question),
            f"Local fallback — Gemini request failed ({error_detail})",
        )


# ============================================================
# 7. PAGE HEADER
#    app.py already renders the shared AquaSentinel brand header.
#    This is only the page-specific heading.
# ============================================================
st.markdown(
    """
    <div class="agent-heading">
        <div class="agent-eyebrow">INTELLIGENT WATER DECISION SUPPORT</div>
        <div class="agent-title">AI Assistant</div>
        <p class="agent-subtitle">
            Ask questions about water-demand forecasting, unusual consumption,
            equitable allocation and crisis scenarios. Responses are grounded
            in the project information.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if client:
    st.markdown(
        '<div class="agent-status">● Gemini API configured — verified when you send a message</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="agent-status local">● Local decision-support mode — Gemini API key not loaded</div>',
        unsafe_allow_html=True,
    )

st.divider()

# ============================================================
# 8. CHAT STATE
# ============================================================
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = [{
        "role": "assistant",
        "content": (
            "Hello! I am **AquaSentinel AI**. I can help you understand "
            "water-demand forecasting, anomaly detection, equitable "
            "allocation and crisis simulations. What would you like to explore?"
        ),
        "mode": "Project assistant",
    }]

if "agent_pending_prompt" not in st.session_state:
    st.session_state.agent_pending_prompt = None

# ============================================================
# 9. QUICK PROMPTS
# ============================================================
st.markdown("#### Try asking")

quick_prompts = [
    "Explain demand forecasting",
    "How does anomaly detection work?",
    "Explain equitable resource allocation",
    "Analyse the water shortage stress test",
    "Tell me about the HSB dataset",
    "Explain the project architecture",
]

prompt_cols = st.columns(3)
for index, prompt in enumerate(quick_prompts):
    with prompt_cols[index % 3]:
        if st.button(
            prompt,
            key=f"agent_quick_{index}",
            use_container_width=True,
        ):
            st.session_state.agent_pending_prompt = prompt
            st.rerun()

st.divider()
st.markdown("#### Conversation")

# ============================================================
# 10. CONVERSATION DISPLAY
# ============================================================
for message in st.session_state.agent_messages:
    role = message.get("role", "assistant")
    avatar = "💧" if role == "assistant" else "🙂"

    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])
        if role == "assistant" and message.get("mode"):
            st.caption(message["mode"])

# ============================================================
# 11. CHAT COMPOSER AND RESPONSE
# ============================================================
user_question = st.chat_input("Message AquaSentinel AI…")

if st.session_state.agent_pending_prompt:
    user_question = st.session_state.agent_pending_prompt
    st.session_state.agent_pending_prompt = None

if user_question:
    st.session_state.agent_messages.append({
        "role": "user",
        "content": user_question,
    })

    history = st.session_state.agent_messages[:-1]

    with st.chat_message("user", avatar="🙂"):
        st.markdown(user_question)

    with st.chat_message("assistant", avatar="💧"):
        with st.spinner("AquaSentinel is preparing a response…"):
            answer, mode = generate_response(user_question, history)

        st.markdown(answer)
        st.caption(mode)

    st.session_state.agent_messages.append({
        "role": "assistant",
        "content": answer,
        "mode": mode,
    })
    st.rerun()

# ============================================================
# 12. FOOTER CONTROLS
# ============================================================
st.divider()
footer_left, footer_right = st.columns([1, 4])

with footer_left:
    if st.button("Clear conversation", key="clear_agent_chat"):
        st.session_state.agent_messages = [{
            "role": "assistant",
            "content": "Conversation cleared. How can I help you?",
            "mode": "Project assistant",
        }]
        st.rerun()

with footer_right:
    st.markdown(
        '<div class="agent-footnote">'
        'AquaSentinel AI is a prototype decision-support assistant. '
        'Recommendations are informational and do not operate real '
        'municipal water infrastructure.'
        '</div>',
        unsafe_allow_html=True,
    )
