import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_doc_name(text: str) -> str:
    prompt = f"""
    Generate a short, meaningful title (max 6 words)
    for the following document.
    Return ONLY the title.

    Content:
    {text[:2000]}
    """
    response = model.generate_content(prompt)
    return response.text.strip()
