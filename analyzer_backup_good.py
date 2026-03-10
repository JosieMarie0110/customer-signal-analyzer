import json
import os
from openai import OpenAI
from taxonomy import get_all_signals, get_taxonomy
from scoring import score_detected_signals, format_score_summary

SYSTEM_PROMPT = """
You are a communication intelligence assistant for customer-facing teams.

Your task is to analyze written communication and identify subtle communication, behavioral, and business relationship signals.

Important rules:
- Do not diagnose intent or personality with certainty.
- Do not claim psychological conclusions as facts.
- Surface patterns in language that may suggest tension, risk, or misalignment.
- Keep interpretations cautious, practical, and useful for customer-facing teams.
- Focus on communication strategy, customer relationship dynamics, and business implications.
- Return valid JSON only.
""".strip()


def load_runbooks():
    try:
        with open("cs_runbooks.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def match_runbooks(detected_signals):
    runbooks = load_runbooks()
    matches = []

    for signal in detected_signals:
        key = signal.lower()
        if key in runbooks:
            entry = runbooks[key]
            matches.append(
                {
                    "signal": signal,
                    "interpretation": entry.get("interpretation", ""),
                    "response_priority": entry.get("response_priority", ""),
                    "recommended_actions": entry.get("recommended_actions", []),
                    "communication_principles": entry.get("communication_principles", []),
                }
            )

    return matches


def _build_analysis_prompt(message_text: str) -> str:
    taxonomy = get_taxonomy()

    return f"""
Analyze the following customer communication.

Message:
\"\"\"
{message_text}
\"\"\"

Evaluate the message against these signal categories.

Communication signals:
{json.dumps(list(taxonomy["communication_signals"].keys()), indent=2)}

Behavioral signals:
{json.dumps(list(taxonomy["behavioral_signals"].keys()), indent=2)}

Business relationship signals:
{json.dumps(list(taxonomy["business_signals"].keys()), indent=2)}

Return your analysis as JSON using exactly this schema:

{{
  "communication_temperature": "short label such as Calm, Neutral, Guarded, Strained, Escalating",
  "detected_signals": [
    "signal name 1",
    "signal name 2"
  ],
  "signal_evidence": {{
    "signal name 1": "brief explanation tied to wording or tone in the message",
    "signal name 2": "brief explanation tied to wording or tone in the message"
  }},
  "likely_underlying_dynamics": [
    "careful interpretation 1",
    "careful interpretation 2"
  ],
  "business_risk_implications": [
    "practical business or relationship implication 1",
    "practical business or relationship implication 2"
  ],
  "recommended_response_strategy": [
    "recommended action 1",
    "recommended action 2",
    "recommended action 3"
  ],
  "suggested_reply_draft": "a professional response draft",
  "confidence_notes": "brief caution note about ambiguity, limitations, or uncertainty"
}}

Requirements:
- Only use signal names from the provided taxonomy.
- Include 2 to 6 detected signals when present.
- If evidence is weak, be conservative.
- Tie evidence to actual wording, tone, or structure in the message.
- The suggested reply should be calm, professional, and relationship-preserving.
- Do not include markdown fences.
""".strip()


def _normalize_detected_signals(detected_signals):
    valid_signals = {s.lower(): s for s in get_all_signals()}
    normalized = []

    for signal in detected_signals or []:
        cleaned = str(signal).strip().lower()
        if cleaned in valid_signals and valid_signals[cleaned] not in normalized:
            normalized.append(valid_signals[cleaned])

    return normalized


def _safe_json_parse(text: str) -> dict:
    text = text.strip()

    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()

    return json.loads(text)


def _fallback_analysis(message_text: str) -> dict:
    lowered = message_text.lower()

    detected_signals = []

    keyword_map = {
        "passive aggression": ["as mentioned before", "per my last email", "once again"],
        "defensiveness": ["we already", "as explained", "we have already"],
        "blame language": ["your team", "you failed", "because of your"],
        "support frustration": ["frustrated", "disappointed", "still waiting", "unacceptable"],
        "trust erosion": ["concerned about", "losing confidence", "this keeps happening"],
        "executive pressure": ["leadership", "executive", "management", "vp", "cio"],
        "renewal concern": ["renewal", "contract", "reevaluate", "reconsider"],
        "competitive evaluation": ["alternative", "other vendor", "competitor", "options"],
        "credibility pressure": ["i need to explain", "i have to justify", "hard to defend"],
    }

    for signal, terms in keyword_map.items():
        if any(term in lowered for term in terms):
            detected_signals.append(signal)

    detected_signals = _normalize_detected_signals(detected_signals)
    scores = score_detected_signals(detected_signals)
    formatted_scores = format_score_summary(scores)
    matched_runbooks = match_runbooks(detected_signals)

    return {
        "communication_temperature": "Guarded" if detected_signals else "Neutral",
        "detected_signals": detected_signals,
        "signal_evidence": {
            signal: "Detected through simple keyword-based fallback matching." for signal in detected_signals
        },
        "likely_underlying_dynamics": [
            "Some wording may suggest tension or reduced confidence."
        ] if detected_signals else [
            "No strong communication signals were detected in fallback mode."
        ],
        "business_risk_implications": [
            "If these signals continue across interactions, they may contribute to strained rapport or broader account risk."
        ] if detected_signals else [
            "No clear business relationship risk was identified in fallback mode."
        ],
        "recommended_response_strategy": [
            "Acknowledge the concern directly.",
            "Reduce ambiguity in next steps.",
            "Respond calmly and reinforce ownership."
        ] if detected_signals else [
            "Respond clearly and maintain a steady, professional tone."
        ],
        "suggested_reply_draft": (
            "Thank you for the note. I understand the concern and want to make sure we address it clearly. "
            "We are reviewing the issue, aligning internally on next steps, and will follow up with a more specific update shortly."
        ),
        "confidence_notes": "Fallback mode uses simple pattern matching and should be treated as directional only.",
        "matched_runbooks": matched_runbooks,
        "score_breakdown": formatted_scores,
        "raw_scores": scores
    }


def analyze_message(message_text: str, model: str = "gpt-4.1-mini") -> dict:
    if not message_text or not message_text.strip():
        empty_scores = {
            "emotional_strain": 0,
            "trust_risk": 0,
            "escalation_pressure": 0,
            "business_risk": 0,
            "overall_risk": 0,
        }
        return {
            "communication_temperature": "Unknown",
            "detected_signals": [],
            "signal_evidence": {},
            "likely_underlying_dynamics": ["No message content provided."],
            "business_risk_implications": ["Unable to assess without message content."],
            "recommended_response_strategy": ["Provide a message to analyze."],
            "suggested_reply_draft": "",
            "confidence_notes": "No content was supplied for analysis.",
            "matched_runbooks": [],
            "score_breakdown": format_score_summary(empty_scores),
            "raw_scores": empty_scores,
        }

    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        return _fallback_analysis(message_text)

    prompt = _build_analysis_prompt(message_text)

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        parsed = _safe_json_parse(response.output_text)
        parsed["detected_signals"] = _normalize_detected_signals(parsed.get("detected_signals", []))

        scores = score_detected_signals(parsed["detected_signals"])
        parsed["raw_scores"] = scores
        parsed["score_breakdown"] = format_score_summary(scores)
        parsed["matched_runbooks"] = match_runbooks(parsed["detected_signals"])

        parsed.setdefault("communication_temperature", "Unknown")
        parsed.setdefault("signal_evidence", {})
        parsed.setdefault("likely_underlying_dynamics", [])
        parsed.setdefault("business_risk_implications", [])
        parsed.setdefault("recommended_response_strategy", [])
        parsed.setdefault("suggested_reply_draft", "")
        parsed.setdefault("confidence_notes", "")

        return parsed

    except Exception as exc:
        fallback = _fallback_analysis(message_text)
        fallback["confidence_notes"] = (
            f"Model analysis failed and fallback mode was used instead. Error: {exc}"
        )
        return fallback
