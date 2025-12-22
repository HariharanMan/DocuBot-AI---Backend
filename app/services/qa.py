import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def answer_question(context, question):
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
    response = model.generate_content(prompt)
    return response.text.strip()
