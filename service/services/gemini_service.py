import os
import google.genai as genai
from google.genai import types
from core.prompts import LLM_SYSTEM_INSTRUCTIONS
from core.secrets import access_secret
from services.function_calling_service import get_user_specific_logs

EMBEDDING_DIMENSIONALITY = 768
client = genai.Client(api_key=access_secret(project_id=os.getenv("PROJECT_ID"), secret_id="GEMINI-API-KEY-DEV"))

def generate_response(user_id: str, input_text: str) -> str | None:
    config = types.GenerateContentConfig(
        system_instruction=LLM_SYSTEM_INSTRUCTIONS,
        max_output_tokens=500,
        tools=[get_user_specific_logs(user_id=user_id)]
    )

    response = client.models.generate_content(
        model=os.getenv("LLM_MODEL", "gemini-2.5-flash-lite"),
        contents=input_text,
        config=config
    )

    return response.text
