import os
import google.genai as genai
from google.genai import types
from core.secrets import access_secret

EMBEDDING_DIMENSIONALITY = 768
client = genai.Client(api_key=access_secret(project_id=os.getenv("PROJECT_ID"), secret_id="GEMINI-API-KEY-DEV"))

def generate_embedding(text: str) -> list[float]:
    result = client.models.embed_content(
        model=os.getenv("EMBEDDING_MODEL", "gemini-embedding-001"),
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONALITY)
    )

    res = result.embeddings[0].values if result.embeddings else None
    if res is None:
        raise ValueError("Embedding generation failed")
    
    return res