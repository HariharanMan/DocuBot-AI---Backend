import os
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()

client = Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-flash"   # recommended stable model


def generate_doc_name(text: str) -> str:
    """
    Generates a short title for a document using Gemini.
    """

    prompt = f"""
    Generate a short, meaningful title (max 6 words)
    for the following document.
    Return ONLY the title text, no quotes.

    Content:
    {text[:2000]}
    """

    result = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return result.text.strip()
