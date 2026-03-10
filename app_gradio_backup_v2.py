import os
import html
import gradio as gr
from analyzer import analyze_message

APP_TITLE = "Customer Signal Analyzer"
DEFAULT_MODEL = "gpt-4.1-mini"

BANNER_CANDIDATES = [
    "banner1.png",
    "./banner1.png",
]

CUSTOM_CSS = """
body, .gradio-container {
    background: #f3f7fc !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1f2d3d;
}

.gradio-container {
    max-width: 1520px !important;
    width: 94% !important;
    margin: auto !important;
    padding-top: 18px !important;
    padding-bottom: 28px !important;
}

.panel {
    background: white;
    border-radius: 18px;
    padding: 24px;
    border: 1px solid #dbe5f2;
    box-shadow: 0 8px 24px rgba(31, 45, 61, 0.06);
}

.topbar {
    background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
    border: 1px solid #dbe5f2;
    border-radius: 18px;
    padding: 18px 22px;
    box-shadow: 0 8px 24px rgba(31, 45, 61, 0.05);
}

.metric-card {
    background: linear-gradient(180deg, #f9fbff 0%, #f4f8ff 100%);
    border: 1px solid #dde7f5;
    border-radius: 14px;
    padding: 14px 16px;
    min-height: 88px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
}

.metric-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: #6a7b91;
    font-weight: 700;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 18px;
    font-weight: 800;
    color: #1f2d3d;
    line-height: 1.3;
}

.risk-bar-card {
    background: linear-gradient(180deg, #f9fbff 0%, #f4f8ff 100%);
    border: 1px solid #dde7f5;
    border-radius: 14px;
    padding: 14px 16px;
    margin-top: 14px;
}

.risk-bar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}

.risk-bar-label {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: #6a7b91;
    font-weight: 700;
}

.risk-bar-value {
    font-size: 14px;
    font-weight: 800;
    color: #1f2d3d;
}

.risk-track {
    width: 100%;
    height: 12px;
    background: #e7eef8;
    border-radius: 999px;
    overflow: hidden;
    border: 1px solid #d9e4f2;
}

.risk-fill {
    height: 100%;
    border-radius: 999px;
}

.section-card {
    background: #fbfdff;
    border: 1px solid #dde7f5;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 14px;
}

.section-title {
    font-size: 16px;
    font-weight: 800;
    color: #23364d;
    margin-bottom: 8px;
}

.clean-list {
    padding-left: 18px;
    margin: 0;
}

.clean-list li {
    margin-bottom: 7px;
    line-height: 1.45;
}

button.primary-btn {
    background: linear-gradient(180deg, #3b82f6 0%, #2f6fdd 100%) !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    border: none !important;
    box-shadow: 0 8px 18px rgba(47, 111, 221, 0.22);
}

button.primary-btn:hover {
    filter: brightness(0.98);
}

button.secondary-btn {
    border-radius: 12px !important;
    font-weight: 700 !important;
}

.logo-frame {
    border: 1px solid #d8e4f2;
    border-radius: 16px;
    background: #f8fbff;
    padding: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 88px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.85);
}

.header-title {
    font-size: 36px;
    font-weight: 800;
    line-height: 1.08;
    color: #1f2d3d;
    margin: 0 0 8px 0;
}

.header-subtitle {
    font-size: 16px;
    line-height: 1.45;
    color: #607287;
    margin: 0;
    max-width: 980px;
}

.block-heading {
    font-size: 24px;
    font-weight: 800;
    color: #1f2d3d;
    margin: 0 0 14px 0;
}

.helper-text {
    font-size: 13px;
    color: #6f8096;
    margin-top: -4px;
    margin-bottom: 14px;
}

footer {
    visibility: hidden;
}

button[title="Share"],
button[title="Download"],
button[title="Fullscreen"] {
    display: none !important;
}
"""


def get_banner_path():
    for path in BANNER_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def metric_card(label, value):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{html.escape(label)}</div>
        <div class="metric-value">{html.escape(value)}</div>
    </div>
    """


def parse_overall_score(score_text: str) -> int:
    try:
        number = str(score_text).split("/")[0].strip()
        return max(0, min(10, int(number)))
    except Exception:
        return 0


def risk_fill_color(score: int) -> str:
    if score <= 3:
        return "#22c55e"
    if score <= 6:
        return "#f59e0b"
    if score <= 8:
        return "#f97316"
    return "#ef4444"


def risk_bar(score_text: str) -> str:
    score = parse_overall_score(score_text)
    percent = score * 10
    color = risk_fill_color(score)
    return f"""
    <div class="risk-bar-card">
        <div class="risk-bar-header">
            <div class="risk-bar-label">Risk Level</div>
            <div class="risk-bar-value">{html.escape(score_text)}</div>
        </div>
        <div class="risk-track">
            <div class="risk-fill" style="width:{percent}%; background:{color};"></div>
        </div>
    </div>
    """


def list_html(items):
    if not items:
        return ""
    li = "".join([f"<li>{html.escape(str(i))}</li>" for i in items])
    return f"<ul class='clean-list'>{li}</ul>"


def dict_html(d):
    if not d:
        return ""
    li = "".join(
        f"<li><strong>{html.escape(str(k))}:</strong> {html.escape(str(v))}</li>"
        for k, v in d.items()
    )
    return f"<ul class='clean-list'>{li}</ul>"


def section(title, body):
    if not body:
        return ""
    return f"""
    <div class="section-card">
        <div class="section-title">{html.escape(title)}</div>
        {body}
    </div>
    """


def runbooks_html(runbooks):
    if not runbooks:
        return ""

    blocks = []
    for rb in runbooks:
        signal = html.escape(str(rb.get("signal", "")))
        interpretation = html.escape(str(rb.get("interpretation", "")))
        priority = html.escape(str(rb.get("response_priority", "")).upper())
        actions = list_html(rb.get("recommended_actions", []))
        principles = list_html(rb.get("communication_principles", []))

        block = f"""
        <div class="section-card">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:10px;">
                <div class="section-title" style="margin-bottom:0;">{signal}</div>
                <div style="font-size:11px; font-weight:800; color:#2f6fdd; background:#eaf2ff; border:1px solid #cfe0ff; border-radius:999px; padding:4px 10px;">
                    {priority} PRIORITY
                </div>
            </div>
            <div style="font-size:14px; color:#223247; margin-bottom:10px;"><strong>Interpretation</strong><br>{interpretation}</div>
            <div style="font-size:14px; color:#223247; margin-bottom:8px;"><strong>Recommended Actions</strong></div>
            {actions}
            <div style="font-size:14px; color:#223247; margin:10px 0 8px 0;"><strong>Communication Principles</strong></div>
            {principles}
        </div>
        """
        blocks.append(block)

    return "".join(blocks)


def analyze_and_format(message):
    result = analyze_message(message, model=DEFAULT_MODEL)
    scores = result.get("score_breakdown", {})

    overall_text = scores.get("overall_risk", "N/A")

    temperature = metric_card("Communication Temperature", result.get("communication_temperature", "Unknown"))
    overall = metric_card("Overall Risk", overall_text)
    emotional = metric_card("Emotional Strain", scores.get("emotional_strain", "N/A"))
    trust = metric_card("Trust Risk", scores.get("trust_risk", "N/A"))
    escalation = metric_card("Escalation Pressure", scores.get("escalation_pressure", "N/A"))
    business = metric_card("Business Risk", scores.get("business_risk", "N/A"))
    risk_meter = risk_bar(overall_text)

    interpretation = (
        section("Detected Signals", list_html(result.get("detected_signals", []))) +
        section("Signal Evidence", dict_html(result.get("signal_evidence", {}))) +
        section("Likely Underlying Dynamics", list_html(result.get("likely_underlying_dynamics", []))) +
        section("Business Risk Implications", list_html(result.get("business_risk_implications", [])))
    )

    strategy = section(
        "Recommended Response Strategy",
        list_html(result.get("recommended_response_strategy", []))
    )

    runbooks = runbooks_html(result.get("matched_runbooks", []))
    reply = result.get("suggested_reply_draft", "")
    confidence = result.get("confidence_notes", "")

    return (
        temperature,
        overall,
        emotional,
        trust,
        escalation,
        business,
        risk_meter,
        interpretation,
        strategy,
        runbooks,
        reply,
        confidence
    )


def clear_all():
    return (
        "",  # message input
        metric_card("Communication Temperature", "—"),
        metric_card("Overall Risk", "—"),
        metric_card("Emotional Strain", "—"),
        metric_card("Trust Risk", "—"),
        metric_card("Escalation Pressure", "—"),
        metric_card("Business Risk", "—"),
        risk_bar("0/10 (Low)"),
        "",  # interpretation
        "",  # strategy
        "",  # runbooks
        "",  # reply
        "",  # confidence
    )


default_temp = metric_card("Communication Temperature", "—")
default_overall = metric_card("Overall Risk", "—")
default_emotional = metric_card("Emotional Strain", "—")
default_trust = metric_card("Trust Risk", "—")
default_escalation = metric_card("Escalation Pressure", "—")
default_business = metric_card("Business Risk", "—")
default_risk_bar = risk_bar("0/10 (Low)")

with gr.Blocks(css=CUSTOM_CSS, title=APP_TITLE) as demo:
    with gr.Group(elem_classes=["topbar"]):
        banner = get_banner_path()

        with gr.Row():
            with gr.Column(scale=1, min_width=135):
                if banner:
                    with gr.Group(elem_classes=["logo-frame"]):
                        gr.Image(
                            value=banner,
                            show_label=False,
                            container=False,
                            width=104,
                            height=72,
                            interactive=False
                        )

            with gr.Column(scale=10):
                gr.HTML("""
                <div style="display:flex; flex-direction:column; justify-content:center; min-height:88px;">
                    <div class="header-title">Customer Signal Analyzer</div>
                    <div class="header-subtitle">
                        AI-assisted analysis of customer communication signals for Customer Success teams.
                    </div>
                </div>
                """)

    with gr.Row():
        with gr.Column(scale=5):
            with gr.Group(elem_classes=["panel"]):
                gr.HTML('<div class="block-heading">Message Input</div>')
                gr.HTML('<div class="helper-text">Paste a customer email, Slack message, or escalation note for structured analysis.</div>')

                message = gr.Textbox(
                    lines=14,
                    label="Customer Email, Slack Message, or Escalation Note"
                )

                with gr.Row():
                    analyze = gr.Button("Analyze Communication", elem_classes=["primary-btn"])
                    clear = gr.Button("Clear", elem_classes=["secondary-btn"])

        with gr.Column(scale=7):
            with gr.Group(elem_classes=["panel"]):
                gr.HTML('<div class="block-heading">Risk Snapshot</div>')
                gr.HTML('<div class="helper-text">A high-level view of communication temperature and relationship risk.</div>')

                with gr.Row():
                    temp = gr.HTML(default_temp)
                    overall = gr.HTML(default_overall)

                with gr.Row():
                    emotional = gr.HTML(default_emotional)
                    trust = gr.HTML(default_trust)
                    escalation = gr.HTML(default_escalation)
                    business = gr.HTML(default_business)

                risk_meter = gr.HTML(default_risk_bar)

    with gr.Row():
        with gr.Column(scale=6):
            with gr.Group(elem_classes=["panel"]):
                gr.HTML('<div class="block-heading">Interpretation</div>')
                interpretation = gr.HTML("")

        with gr.Column(scale=6):
            with gr.Group(elem_classes=["panel"]):
                gr.HTML('<div class="block-heading">Response Guidance</div>')
                strategy = gr.HTML("")

                reply = gr.Textbox(
                    label="Suggested Reply Draft",
                    lines=8
                )

                confidence = gr.Textbox(
                    label="Confidence / Caution Notes",
                    lines=4
                )

    with gr.Group(elem_classes=["panel"]):
        gr.HTML('<div class="block-heading">Matched Runbooks</div>')
        runbooks = gr.HTML("")

    analyze.click(
        fn=analyze_and_format,
        inputs=[message],
        outputs=[
            temp,
            overall,
            emotional,
            trust,
            escalation,
            business,
            risk_meter,
            interpretation,
            strategy,
            runbooks,
            reply,
            confidence
        ]
    )

    clear.click(
        fn=clear_all,
        inputs=[],
        outputs=[
            message,
            temp,
            overall,
            emotional,
            trust,
            escalation,
            business,
            risk_meter,
            interpretation,
            strategy,
            runbooks,
            reply,
            confidence
        ]
    )

if __name__ == "__main__":
    demo.launch()
