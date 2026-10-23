import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for model in client.models.list():
    name = model.name.replace("models/", "")
    if "gemini" in name and "generateContent" in (model.supported_actions or []):
        print(name)