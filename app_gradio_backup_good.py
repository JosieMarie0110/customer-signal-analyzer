import os
import html
import gradio as gr
from analyzer import analyze_message

APP_TITLE = "Customer Signal Analyzer"
APP_SUBTITLE = (
    "Analyze written communication for behavioral, emotional, and business-risk signals "
    "to support more thoughtful, strategically grounded responses."
)

BANNER_CANDIDATES = [
    "banner.png",
    "./banner.png",
    "logo.png",
    "./logo.png",
]

DEFAULT_MODEL = "gpt-4.1-mini"

CUSTOM_CSS = """
body, .gradio-container {
    background: #edf3fb !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.gradio-container {
    max-width: 1600px !important;
    width: 95% !important;
    margin: 0 auto !important;
    padding-top: 24px !important;
    padding-bottom: 24px !important;
}

.panel {
    background: white;
    border: 1px solid #d8e4f2;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

textarea, input {
    border-radius: 12px !important;
}

button.primary-btn {
    background: #2f6fdd !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 10px 18px !important;
}

button.primary-btn:hover {
    filter: brightness(0.97);
}

button.secondary-btn {
    border-radius: 12px !important;
    font-weight: 600 !important;
}

.metric-card {
    background: #f6f9fe;
    border: 1px solid #d8e4f2;
    border-radius: 14px;
    padding: 14px 16px;
    min-height: 92px;
}

.metric-label {
    color: #5f6f82;
    font-size: 13px;
    margin-bottom: 6px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.metric-value {
    font-size: 18px;
    font-weight: 700;
    color: #1f2d3d;
    line-height: 1.35;
}

.section-card {
    background: #f8fbff;
    border: 1px solid #d8e4f2;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 14px;
}

.section-title {
    font-size: 16px;
    font-weight: 700;
    color: #2d3f57;
    margin-bottom: 8px;
}

.runbook-card {
    background: #f8fbff;
    border: 1px solid #d8e4f2;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 14px;
}

.runbook-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
}

.runbook-signal {
    font-size: 18px;
    font-weight: 700;
    color: #1f2d3d;
}

.runbook-priority {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #2f6fdd;
    background: #eaf2ff;
    border: 1px solid #cfe0ff;
    border-radius: 999px;
    padding: 4px 10px;
    white-space: nowrap;
}

.runbook-section-title {
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 6px;
    color: #2d3f57;
}

.clean-list {
    margin: 0;
    padding-left: 20px;
}

.clean-list li {
    margin-bottom: 8px;
}

.muted-empty {
    color: #6b7c93;
}

footer {
    visibility: hidden !important;
}

/* Remove Gradio image toolbar icons */
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


def clean_list_html(items, empty_text="No analysis yet."):
    if not items:
        return f'<div class="muted-empty">{html.escape(empty_text)}</div>'
    items_html = "".join(f"<li>{html.escape(str(item))}</li>" for item in items)
    return f'<ul class="clean-list">{items_html}</ul>'


def evidence_list_html(d, empty_text="No evidence captured yet."):
    if not d:
        return f'<div class="muted-empty">{html.escape(empty_text)}</div>'
    items_html = "".join(
        f"<li><strong>{html.escape(str(key))}:</strong> {html.escape(str(value))}</li>"
        for key, value in d.items()
    )
    return f'<ul class="clean-list">{items_html}</ul>'


def section_card(title, body_html):
    return f"""
    <div class="section-card">
        <div class="section-title">{html.escape(title)}</div>
        {body_html}
    </div>
    """


def format_interpretation(signals, evidence, dynamics, implications):
    cards = [
        section_card(
            "Detected Signals",
            clean_list_html(signals, "No strong signals identified."),
        ),
        section_card(
            "Signal Evidence",
            evidence_list_html(evidence, "No signal evidence captured."),
        ),
        section_card(
            "Likely Underlying Dynamics",
            clean_list_html(dynamics, "No underlying dynamics identified."),
        ),
        section_card(
            "Business Risk Implications",
            clean_list_html(implications, "No business implications identified."),
        ),
    ]
    return "".join(cards)


def format_response_guidance(strategy):
    return section_card(
        "Recommended Response Strategy",
        clean_list_html(strategy, "No response strategy generated."),
    )


def format_runbooks(runbooks):
    if not runbooks:
        return '<div class="muted-empty">No matched runbooks yet.</div>'

    blocks = []
    for rb in runbooks:
        signal = html.escape(str(rb.get("signal", "Unknown Signal")))
        interpretation = html.escape(str(rb.get("interpretation", "")))
        priority = html.escape(str(rb.get("response_priority", "unknown")))
        actions = rb.get("recommended_actions", [])
        principles = rb.get("communication_principles", [])

        actions_html = clean_list_html(actions, "No recommended actions.")
        principles_html = clean_list_html(principles, "No communication principles.")

        block = f"""
        <div class="runbook-card">
            <div class="runbook-header">
                <div class="runbook-signal">{signal}</div>
                <div class="runbook-priority">{priority} priority</div>
            </div>

            <div class="runbook-section-title">Interpretation</div>
            <p>{interpretation or "No interpretation available."}</p>

            <div class="runbook-section-title">Recommended Actions</div>
            {actions_html}

            <div class="runbook-section-title">Communication Principles</div>
            {principles_html}
        </div>
        """
        blocks.append(block)

    return "".join(blocks)


def analyze_and_format(message_text):
    result = analyze_message(message_text, model=DEFAULT_MODEL)

    temperature_html = metric_card(
        "Communication Temperature",
        result.get("communication_temperature", "Unknown"),
    )

    scores = result.get("score_breakdown", {})
    overall_html = metric_card("Overall Risk", scores.get("overall_risk", "N/A"))
    trust_html = metric_card("Trust Risk", scores.get("trust_risk", "N/A"))
    escalation_html = metric_card("Escalation Pressure", scores.get("escalation_pressure", "N/A"))
    business_html = metric_card("Business Risk", scores.get("business_risk", "N/A"))
    emotional_html = metric_card("Emotional Strain", scores.get("emotional_strain", "N/A"))

    interpretation_html = format_interpretation(
        result.get("detected_signals", []),
        result.get("signal_evidence", {}),
        result.get("likely_underlying_dynamics", []),
        result.get("business_risk_implications", []),
    )

    guidance_html = format_response_guidance(
        result.get("recommended_response_strategy", [])
    )

    runbooks_html = format_runbooks(result.get("matched_runbooks", []))
    reply_text = result.get("suggested_reply_draft", "")
    confidence_text = result.get("confidence_notes", "")

    return (
        temperature_html,
        overall_html,
        emotional_html,
        trust_html,
        escalation_html,
        business_html,
        interpretation_html,
        guidance_html,
        runbooks_html,
        reply_text,
        confidence_text,
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
        "",  # interpretation
        "",  # response guidance
        "",  # runbooks
        "",  # suggested reply
        "",  # confidence notes
    )


default_temp = metric_card("Communication Temperature", "—")
default_overall = metric_card("Overall Risk", "—")
default_emotional = metric_card("Emotional Strain", "—")
default_trust = metric_card("Trust Risk", "—")
default_escalation = metric_card("Escalation Pressure", "—")
default_business = metric_card("Business Risk", "—")

with gr.Blocks(title=APP_TITLE) as demo:
    with gr.Group(elem_classes=["panel"]):
        with gr.Row():
            with gr.Column(scale=1, min_width=90):
                banner_path = get_banner_path()
                if banner_path:
                    gr.Image(
                        banner_path,
                        show_label=False,
                        container=False,
                        width=60,
                    )

            with gr.Column(scale=10):
                gr.Markdown(
                    """
                    <div style="display:flex; flex-direction:column; justify-content:center;">
                        <div style="font-size:38px; font-weight:800; color:#1f2d3d; line-height:1.15;">
                            Customer Signal Analyzer
                        </div>
                        <div style="font-size:17px; color:#5f6f82; margin-top:6px;">
                            AI-assisted interpretation of customer communication signals for Customer Success teams.
                        </div>
                    </div>
                    """
                )

    with gr.Row():
        with gr.Column(scale=5):
            with gr.Group(elem_classes=["panel"]):
                gr.Markdown("## Message Input")

                message_input = gr.Textbox(
                    label="Customer Email, Slack Message, or Escalation Note",
                    lines=18,
                    placeholder=(
                        "Paste the message here. Example: We are still waiting on a clear resolution, "
                        "and I need to explain this internally to leadership by end of day..."
                    ),
                )

                with gr.Row():
                    analyze_btn = gr.Button(
                        "Analyze Communication",
                        elem_classes=["primary-btn"],
                    )
                    clear_btn = gr.Button(
                        "Clear",
                        elem_classes=["secondary-btn"],
                    )

        with gr.Column(scale=7):
            with gr.Group(elem_classes=["panel"]):
                gr.Markdown("## Risk Snapshot")

                with gr.Row():
                    temperature_output = gr.HTML(default_temp)
                    overall_output = gr.HTML(default_overall)

                with gr.Row():
                    emotional_output = gr.HTML(default_emotional)
                    trust_output = gr.HTML(default_trust)
                    escalation_output = gr.HTML(default_escalation)
                    business_output = gr.HTML(default_business)

    with gr.Row():
        with gr.Column(scale=6):
            with gr.Group(elem_classes=["panel"]):
                gr.Markdown("## Interpretation")
                interpretation_output = gr.HTML("")

        with gr.Column(scale=6):
            with gr.Group(elem_classes=["panel"]):
                gr.Markdown("## Response Guidance")
                response_guidance_output = gr.HTML("")
                suggested_reply = gr.Textbox(
                    label="Suggested Reply Draft",
                    lines=10,
                    placeholder="Suggested reply will appear here...",
                )
                confidence_notes = gr.Textbox(
                    label="Confidence / Caution Notes",
                    lines=4,
                    placeholder="Confidence notes will appear here...",
                )

    with gr.Row():
        with gr.Column():
            with gr.Group(elem_classes=["panel"]):
                gr.Markdown("## Matched Runbooks")
                matched_runbooks = gr.HTML("")

    analyze_btn.click(
        fn=analyze_and_format,
        inputs=[message_input],
        outputs=[
            temperature_output,
            overall_output,
            emotional_output,
            trust_output,
            escalation_output,
            business_output,
            interpretation_output,
            response_guidance_output,
            matched_runbooks,
            suggested_reply,
            confidence_notes,
        ],
    )

    clear_btn.click(
        fn=clear_all,
        inputs=[],
        outputs=[
            message_input,
            temperature_output,
            overall_output,
            emotional_output,
            trust_output,
            escalation_output,
            business_output,
            interpretation_output,
            response_guidance_output,
            matched_runbooks,
            suggested_reply,
            confidence_notes,
        ],
    )

if __name__ == "__main__":
    demo.launch(css=CUSTOM_CSS)
