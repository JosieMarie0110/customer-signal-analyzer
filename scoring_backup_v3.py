from collections import defaultdict

SIGNAL_WEIGHTS = {
    "tone shifts": {"emotional_strain": 1, "trust_risk": 1},
    "passive aggression": {"emotional_strain": 2, "trust_risk": 2},
    "defensiveness": {"emotional_strain": 2, "trust_risk": 1},
    "deflection": {"trust_risk": 1, "escalation_pressure": 1},
    "emotional distancing": {"emotional_strain": 1, "trust_risk": 2},
    "blame language": {"trust_risk": 2, "escalation_pressure": 2},
    "projection": {"trust_risk": 1, "escalation_pressure": 1},
    "minimization": {"trust_risk": 1},
    "communication inconsistencies": {"trust_risk": 1, "business_risk": 1},
    "avoidance": {"trust_risk": 1, "business_risk": 1},
    "frustration masking": {"emotional_strain": 2, "trust_risk": 1},
    "accountability concerns": {"trust_risk": 2, "business_risk": 1},
    "black-and-white thinking": {"emotional_strain": 1, "escalation_pressure": 1},
    "cognitive bias indicators": {"trust_risk": 1},
    "support frustration": {"emotional_strain": 2, "business_risk": 1},
    "trust erosion": {"trust_risk": 3, "business_risk": 2},
    "executive pressure": {"escalation_pressure": 3, "business_risk": 2},
    "adoption stall": {"business_risk": 2},
    "value realization risk": {"business_risk": 3},
    "renewal concern": {"business_risk": 3, "trust_risk": 2},
    "competitive evaluation": {"business_risk": 3, "escalation_pressure": 1},
    "credibility pressure": {"trust_risk": 2, "business_risk": 2},
}


def clamp_score(value: int, max_score: int = 10) -> int:
    return max(0, min(value, max_score))


def score_detected_signals(detected_signals: list[str]) -> dict:
    scores = defaultdict(int)

    for signal in detected_signals:
        weights = SIGNAL_WEIGHTS.get(signal.lower(), {})
        for dimension, weight in weights.items():
            scores[dimension] += weight

    normalized = {
        "emotional_strain": clamp_score(scores["emotional_strain"]),
        "trust_risk": clamp_score(scores["trust_risk"]),
        "escalation_pressure": clamp_score(scores["escalation_pressure"]),
        "business_risk": clamp_score(scores["business_risk"]),
    }

    overall_raw = (
        normalized["emotional_strain"]
        + normalized["trust_risk"]
        + normalized["escalation_pressure"]
        + normalized["business_risk"]
    ) / 4

    normalized["overall_risk"] = clamp_score(round(overall_raw))
    return normalized


def score_label(score: int) -> str:
    if score <= 3:
        return "Low"
    if score <= 6:
        return "Moderate"
    if score <= 8:
        return "High"
    return "Severe"


def format_score_summary(scores: dict) -> dict:
    return {
        "emotional_strain": f'{scores["emotional_strain"]}/10 ({score_label(scores["emotional_strain"])})',
        "trust_risk": f'{scores["trust_risk"]}/10 ({score_label(scores["trust_risk"])})',
        "escalation_pressure": f'{scores["escalation_pressure"]}/10 ({score_label(scores["escalation_pressure"])})',
        "business_risk": f'{scores["business_risk"]}/10 ({score_label(scores["business_risk"])})',
        "overall_risk": f'{scores["overall_risk"]}/10 ({score_label(scores["overall_risk"])})',
    }
