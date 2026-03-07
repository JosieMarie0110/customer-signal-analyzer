import os
from dotenv import load_dotenv
from openai import OpenAI
from taxonomy import TAXONOMY

# load environment variables
load_dotenv()

# initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_customer_message(message: str):

    prompt = f"""
You are an AI assistant that analyzes customer communication for Customer Success teams.

Analyze the message and identify:

1. Emotional signals
2. Cognitive bias
3. Risk signals
4. Risk level
5. Recommended response strategy
6. Draft reply email

Only use labels from this taxonomy:

Emotions: {TAXONOMY["emotions"]}

Bias: {TAXONOMY["bias"]}

Risk signals: {TAXONOMY["risk_signals"]}

Customer message:
{message}

Return the analysis in structured readable sections.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text
