import os
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()

client = Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-flash"


def answer_question(context: str, question: str) -> str:
    """
    Answers a question strictly using provided document context.
    """

    prompt = f"""
    You are an AI assistant.

    Rules:
    - Answer ONLY using the provided context.
    - If the answer is not present, say:
      "The uploaded document does not contain this information."
    - Do NOT guess or use external knowledge.

    Context:
    {context}

    Question:
    {question}
    """

    result = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return result.text.strip()
