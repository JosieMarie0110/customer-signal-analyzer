import os
import json
import html
import base64
from typing import Dict, List, Tuple

import gradio as gr
from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# =========================================================
# CONFIG
# =========================================================
APP_TITLE = "Customer Signal Analyzer"
RUNBOOK_FILE = "cs_runbooks.json"
LOGO_FILE = "logo.png"  # optional

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# =========================================================
# LOAD RUNBOOKS
# =========================================================
def load_runbooks(filepath: str) -> Dict:
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

CS_RUNBOOKS = load_runbooks(RUNBOOK_FILE)

# =========================================================
# PROMPT
# =========================================================
ANALYZER_SYSTEM_PROMPT = """
You are an expert Senior Customer Success strategist analyzing customer communications in a B2B SaaS environment.

Your job is to identify visible and hidden customer signals, including:
- executive escalation risk
- churn risk
- trust erosion
- adoption stall
- value realization risk
- support frustration
- credibility pressure
- expectation misalignment
- communication breakdown
- renewal risk

You must analyze the message like a senior CSM/TAM, not like a generic sentiment tool.

Return ONLY valid JSON matching this schema:

{
  "summary": {
    "sentiment": "Positive | Neutral | Concerned | Frustrated | Escalation Risk",
    "risk_level": "Low | Medium | High",
    "urgency": "Low | Medium | High",
    "top_read": "1-3 sentence strategic interpretation of what the customer is really signaling"
  },
  "primary_signals": ["signal 1", "signal 2", "signal 3"],
  "psychological_signals": ["signal 1", "signal 2"],
  "likely_root_causes": ["cause 1", "cause 2"],
  "recommended_csm_strategy": ["step 1", "step 2", "step 3", "step 4"],
  "suggested_reply": "A professional, empathetic, concise reply draft to the customer.",
  "evidence": [
    {
      "quote": "exact phrase from the customer message",
      "signal": "what this phrase indicates"
    }
  ]
}

Important rules:
- Do not default to Neutral unless the message is truly neutral.
- If leadership is mentioned, consider executive pressure or credibility risk.
- If outages, repeated issues, delays, or lack of progress are mentioned, consider trust erosion and escalation risk.
- If the customer is polite but dissatisfied, capture hidden frustration.
- Be specific and concrete.
"""

# =========================================================
# STYLING
# =========================================================
custom_css = """
body, .gradio-container {
    background: #eaf4ff !important;
}

.gradio-container {
    max-width: 1420px !important;
    margin: 0 auto !important;
    padding-top: 14px !important;
    padding-bottom: 14px !important;
}

.banner-shell {
    background: #dcecff;
    border-radius: 16px;
    padding: 14px 18px;
    margin-bottom: 14px;
    border: 1px solid #c5ddff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.hero-card {
    display: flex;
    align-items: center;
    gap: 20px;
}
.hero-logo {
    width: 82px;
    height: 82px;
    border-radius: 14px;
    object-fit: cover;
    background: white;
    border: 1px solid #d7e6ff;
    padding: 6px;
}

.hero-title-wrap h1 {
    margin: 0;
    font-size: 30px;
    line-height: 1.1;
    color: #123b68;
}

.hero-title-wrap p {
    margin: 5px 0 0 0;
    color: #436687;
    font-size: 14px;
}

.panel-card {
    background: #f7fbff !important;
    border: 1px solid #d6e7ff !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04) !important;
}

.result-card {
    background: white;
    border: 1px solid #d7e6ff;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 12px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.04);
}

.result-card h3 {
    margin: 0 0 10px 0;
    color: #123b68;
    font-size: 18px;
}

.result-card p, .result-card li {
    color: #284761;
    line-height: 1.5;
    font-size: 14px;
}

.result-card ul {
    margin-top: 8px;
    padding-left: 20px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(120px, 1fr));
    gap: 10px;
    margin-bottom: 12px;
}

.kpi-card {
    background: #f3f8ff;
    border: 1px solid #d7e6ff;
    border-radius: 12px;
    padding: 10px 12px;
}

.kpi-label {
    font-size: 12px;
    color: #567798;
    margin-bottom: 4px;
}

.kpi-value {
    font-size: 18px;
    font-weight: 700;
    color: #123b68;
}

button.primary-btn, .gradio-button, .gr-button {
    background: #1f5fae !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
}

button.primary-btn:hover, .gradio-button:hover, .gr-button:hover {
    filter: brightness(0.96);
}

textarea, .gr-textbox textarea {
    font-size: 14px !important;
}

pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    font-size: 12px;
    color: #24455e;
}

.footer-note {
    color: #52718f;
    font-size: 12px;
    margin-top: 6px;
}
"""

# =========================================================
# HELPERS
# =========================================================
def file_to_base64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""

def safe_text(value: str) -> str:
    return html.escape(value or "")

def safe_list(items: List[str], empty_text: str) -> List[str]:
    cleaned = [str(x).strip() for x in (items or []) if str(x).strip()]
    return cleaned if cleaned else [empty_text]

def render_list_card(title: str, items: List[str]) -> str:
    li_html = "".join(f"<li>{safe_text(item)}</li>" for item in items)
    return f"""
    <div class="result-card">
        <h3>{safe_text(title)}</h3>
        <ul>{li_html}</ul>
    </div>
    """

def render_message(text: str, title: str = "Notice") -> str:
    return f"""
    <div class="result-card">
        <h3>{safe_text(title)}</h3>
        <p>{safe_text(text)}</p>
    </div>
    """

def parse_model_output(raw_text: str) -> Dict:
    try:
        return json.loads(raw_text)
    except Exception:
        return {
            "summary": {
                "sentiment": "Unknown",
                "risk_level": "Unknown",
                "urgency": "Unknown",
                "top_read": raw_text[:500] if raw_text else "Model did not return valid JSON."
            },
            "primary_signals": ["Model output could not be parsed"],
            "psychological_signals": [],
            "likely_root_causes": [],
            "recommended_csm_strategy": [],
            "suggested_reply": "",
            "evidence": []
        }

def keyword_match_runbooks(text: str, runbooks: Dict) -> List[str]:
    if not runbooks:
        return []

    text_lower = text.lower()
    matches = []

    # Supports either:
    # { "runbooks": [ { "name": "...", "keywords": [...], "steps": [...] } ] }
    # or
    # { "some_key": { "keywords": [...], "steps": [...] } }
    if isinstance(runbooks, dict) and "runbooks" in runbooks and isinstance(runbooks["runbooks"], list):
        for rb in runbooks["runbooks"]:
            name = rb.get("name", "Unnamed runbook")
            keywords = [str(k).lower() for k in rb.get("keywords", [])]
            if any(k in text_lower for k in keywords):
                matches.append(name)
    elif isinstance(runbooks, dict):
        for name, rb in runbooks.items():
            if isinstance(rb, dict):
                keywords = [str(k).lower() for k in rb.get("keywords", [])]
                if any(k in text_lower for k in keywords):
                    matches.append(name)

    return matches[:5]

def build_runbook_card(matches: List[str]) -> str:
    if not matches:
        return render_message("No runbook match detected from local playbooks.", "Runbook Match")
    items = "".join(f"<li>{safe_text(m)}</li>" for m in matches)
    return f"""
    <div class="result-card">
        <h3>Runbook Match</h3>
        <ul>{items}</ul>
    </div>
    """

def analyze_with_model(context: str, message: str) -> Tuple[Dict, str]:
    if not client:
        raise RuntimeError("Missing OPENAI_API_KEY. Add it to your environment or .env file.")

    account_context = context.strip() if context.strip() else "No additional account context provided."

    user_prompt = f"""
Analyze the following customer communication.

Account context:
{account_context}

Customer message:
{message}

Return only valid JSON.
"""

    response = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "system", "content": ANALYZER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw_text = getattr(response, "output_text", "") or ""
    parsed = parse_model_output(raw_text)
    return parsed, raw_text

# =========================================================
# MAIN ANALYSIS
# =========================================================
def analyze_customer_message(context: str, message: str) -> Tuple[str, str, str, str]:
    context = (context or "").strip()
    message = (message or "").strip()

    if not message:
        empty = render_message("Please paste a customer email or message to analyze.", "Summary")
        return empty, "", "", ""

    try:
        result, raw_text = analyze_with_model(context, message)
    except Exception as e:
        result = {
            "summary": {
                "sentiment": "Unknown",
                "risk_level": "Unknown",
                "urgency": "Unknown",
                "top_read": f"Analyzer error: {str(e)}"
            },
            "primary_signals": ["Could not complete model analysis"],
            "psychological_signals": [],
            "likely_root_causes": [],
            "recommended_csm_strategy": [],
            "suggested_reply": "",
            "evidence": []
        }
        raw_text = str(e)

    summary = result.get("summary", {}) or {}
    sentiment = summary.get("sentiment", "Unknown")
    risk_level = summary.get("risk_level", "Unknown")
    urgency = summary.get("urgency", "Unknown")
    top_read = summary.get("top_read", "No interpretation provided.")

    primary_signals = safe_list(
        result.get("primary_signals", []),
        "No primary signals returned by model"
    )
    psychological_signals = safe_list(
        result.get("psychological_signals", []),
        "No psychological signals returned by model"
    )
    likely_root_causes = safe_list(
        result.get("likely_root_causes", []),
        "No root causes returned by model"
    )
    recommended_csm_strategy = safe_list(
        result.get("recommended_csm_strategy", []),
        "No strategy returned by model"
    )
    suggested_reply = result.get("suggested_reply", "") or "No reply draft returned by model."
    evidence_items = result.get("evidence", []) or []

    runbook_matches = keyword_match_runbooks(f"{context}\n{message}", CS_RUNBOOKS)

    summary_html = f"""
    <div class="result-card">
        <h3>Summary</h3>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Sentiment</div>
                <div class="kpi-value">{safe_text(sentiment)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Risk Level</div>
                <div class="kpi-value">{safe_text(risk_level)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Urgency</div>
                <div class="kpi-value">{safe_text(urgency)}</div>
            </div>
        </div>

        <p><strong>Top Read:</strong> {safe_text(top_read)}</p>
    </div>
    """

    summary_html += render_list_card("Primary Signals", primary_signals)
    summary_html += render_list_card("Psychological Signals", psychological_signals)
    summary_html += render_list_card("Likely Root Causes", likely_root_causes)
    summary_html += render_list_card("Recommended CSM Strategy", recommended_csm_strategy)
    summary_html += build_runbook_card(runbook_matches)

    reply_html = f"""
    <div class="result-card">
        <h3>Suggested Reply</h3>
        <p>{safe_text(suggested_reply).replace(chr(10), '<br>')}</p>
    </div>
    """

    if evidence_items:
        evidence_html = ""
        for item in evidence_items:
            quote = item.get("quote", "")
            signal = item.get("signal", "")
            evidence_html += f"""
            <div class="result-card">
                <h3>Evidence</h3>
                <p><strong>Quote:</strong> {safe_text(quote)}</p>
                <p><strong>Signal:</strong> {safe_text(signal)}</p>
            </div>
            """
    else:
        evidence_html = render_message("No evidence returned by model.", "Evidence")

    raw_html = f"""
    <div class="result-card">
        <h3>Raw Debug Output</h3>
        <pre>{safe_text(raw_text)}</pre>
    </div>
    """

    return summary_html, reply_html, evidence_html, raw_html

# =========================================================
# SAMPLE MESSAGES
# =========================================================
SAMPLE_MESSAGES = {
    "Executive escalation": """Hi Josie,

Our CIO asked me this morning why we’re still experiencing these outages after the last upgrade. I didn’t have a great answer for him, which obviously isn’t ideal.

Can you provide an update that I can pass along to leadership?

Thanks.""",

    "Passive frustration": """Hi Josie,

We’re still seeing the same performance issues we mentioned during the last call. I understand the team is looking into it, but it’s becoming difficult to explain internally why this hasn’t been resolved yet.

We really need more clarity on what’s actually being done and when we can expect improvement.

Thanks.""",

    "Hidden churn signal": """Hi Josie,

We're currently evaluating a few different approaches to solve the monitoring gaps we've been experiencing. We’ll continue using the platform for now, but we want to understand what improvements might be coming in the roadmap.

Appreciate any updates you can share.""",

    "Neutral baseline": """Hi Josie,

Just checking in on the timeline for the next release. Our team is planning some internal upgrades and we want to coordinate schedules if possible.

Thanks!"""
}

def load_sample(sample_name: str) -> str:
    return SAMPLE_MESSAGES.get(sample_name, "")

# =========================================================
# UI
# =========================================================
def build_header_html() -> str:
    logo_b64 = file_to_base64(LOGO_FILE)
    logo_html = (
        f'<img class="hero-logo" src="data:image/png;base64,{logo_b64}" alt="logo" />'
        if logo_b64 else
        '<div class="hero-logo"></div>'
    )

    return f"""
    <div class="banner-shell">
        <div class="hero-card">
            {logo_html}
            <div class="hero-title-wrap">
                <h1>{safe_text(APP_TITLE)}</h1>
                <p>Analyze tone, risk, executive pressure, churn signals, and suggested response strategy.</p>
            </div>
        </div>
    </div>
    """

with gr.Blocks(css=custom_css, title=APP_TITLE) as demo:
    gr.HTML(build_header_html())

    with gr.Row():
        with gr.Column(scale=5):
            with gr.Group(elem_classes=["panel-card"]):
                context_input = gr.Textbox(
                    label="Account Context (optional)",
                    placeholder="Example: Enterprise account, renewal in 90 days, open Sev 1 incident, low executive confidence...",
                    lines=5
                )

                sample_selector = gr.Dropdown(
                    choices=list(SAMPLE_MESSAGES.keys()),
                    label="Load Sample Message",
                    value=None
                )

                message_input = gr.Textbox(
                    label="Customer Message",
                    placeholder="Paste a customer email, Slack message, or escalation note here...",
                    lines=12
                )

                with gr.Row():
                    analyze_btn = gr.Button("Analyze", variant="primary")
                    clear_btn = gr.Button("Clear")

                gr.HTML(
                    """
                    <div class="footer-note">
                        Tip: paste messages that include mixed tone, executive visibility, repeated issues, or vague dissatisfaction to test deeper signal detection.
                    </div>
                    """
                )

        with gr.Column(scale=7):
            with gr.Tabs():
                with gr.Tab("Summary"):
                    summary_output = gr.HTML()

                with gr.Tab("Reply Draft"):
                    reply_output = gr.HTML()

                with gr.Tab("Evidence"):
                    evidence_output = gr.HTML()

                with gr.Tab("Raw Debug"):
                    raw_output = gr.HTML()

    sample_selector.change(
        fn=load_sample,
        inputs=[sample_selector],
        outputs=[message_input]
    )

    analyze_btn.click(
        fn=analyze_customer_message,
        inputs=[context_input, message_input],
        outputs=[summary_output, reply_output, evidence_output, raw_output]
    )

    clear_btn.click(
        fn=lambda: ("", "", "", "", "", None),
        inputs=[],
        outputs=[context_input, message_input, summary_output, reply_output, evidence_output, sample_selector]
    )

if __name__ == "__main__":
    demo.launch()
