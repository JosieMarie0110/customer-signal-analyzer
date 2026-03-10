"""
Signal taxonomy for Customer Signal Analyzer.

Defines the communication, behavioral, and business signals that the analyzer
can detect when interpreting customer messages.

The taxonomy provides:
- signal categories
- signal descriptions
- helper functions for lookup and validation
"""

SIGNAL_TAXONOMY = {

    "communication_signals": {
        "tone shifts": "A noticeable change in tone within the same message, such as moving from polite to frustrated or neutral to urgent.",

        "passive aggression": "Indirect expressions of frustration, resentment, or criticism masked by polite or formal language.",

        "defensiveness": "Language that justifies actions, resists accountability, or protects a position.",

        "deflection": "Attempts to redirect attention away from the core issue or responsibility.",

        "emotional distancing": "Detached or reduced emotional engagement that may signal disengagement or loss of rapport.",

        "blame language": "Language that places fault on another person, team, or organization.",

        "minimization": "Downplaying the seriousness or impact of a problem.",

        "communication inconsistencies": "Mismatch between tone, urgency, or message content and stated expectations."
    },


    "behavioral_signals": {
        "avoidance": "Reluctance to engage directly with the issue, decision, or next step.",

        "frustration masking": "Polite wording that still contains subtle signals of frustration or dissatisfaction.",

        "accountability concerns": "Language suggesting the sender may be under pressure to justify outcomes or decisions.",

        "projection": "Attributing frustration, responsibility, or failure outward toward others.",

        "black-and-white thinking": "Rigid framing that presents situations as extreme or binary outcomes.",

        "cognitive bias indicators": "Language patterns that suggest assumptions, distortions, or emotionally influenced reasoning."
    },


    "business_signals": {
        "support frustration": "Indicators that dissatisfaction with support or issue resolution may be growing.",

        "trust erosion": "Signals that confidence in the team, vendor, or solution may be weakening.",

        "executive pressure": "References to leadership, management visibility, or internal pressure behind the message.",

        "adoption stall": "Signals that implementation progress or usage may be slowing down.",

        "value realization risk": "Indicators that the customer may not be seeing sufficient value from the solution.",

        "renewal concern": "Language suggesting potential commercial or contract risk.",

        "competitive evaluation": "Signals that the customer may be comparing vendors or evaluating alternatives.",

        "credibility pressure": "Language indicating the sender is under pressure to justify their decision to adopt the product or vendor."
    }
}


# Flattened signal list
ALL_SIGNALS = [
    signal
    for category in SIGNAL_TAXONOMY.values()
    for signal in category.keys()
]


def get_all_signals():
    """
    Return a list of all signal names.
    """
    return ALL_SIGNALS


def get_taxonomy():
    """
    Return the full taxonomy dictionary.
    """
    return SIGNAL_TAXONOMY


def get_signal_description(signal_name):
    """
    Return the description for a given signal.
    """
    signal_name = signal_name.lower()

    for category in SIGNAL_TAXONOMY.values():
        for signal, description in category.items():
            if signal.lower() == signal_name:
                return description

    return ""


def get_signal_category(signal_name):
    """
    Return which category a signal belongs to.
    """
    signal_name = signal_name.lower()

    for category_name, category in SIGNAL_TAXONOMY.items():
        for signal in category.keys():
            if signal.lower() == signal_name:
                return category_name

    return "unknown"


def validate_signal(signal_name):
    """
    Check if a signal exists in the taxonomy.
    """
    return signal_name.lower() in [s.lower() for s in ALL_SIGNALS]
