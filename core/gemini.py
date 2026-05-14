from google import genai
from google.genai import types


def fetch_models(api_key: str) -> list[str]:
    client = genai.Client(api_key=api_key)
    return [
        m.name.removeprefix("models/")
        for m in client.models.list()
        if "generateContent" in (m.supported_actions or [])
    ]


def _build_contents(messages: list[dict]) -> list:
    contents = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else msg["role"]
        parts = []
        for img_bytes, mime in msg.get("images", []):
            parts.append(types.Part(inline_data=types.Blob(data=img_bytes, mime_type=mime)))
        if msg.get("content"):
            parts.append(types.Part(text=msg["content"]))
        contents.append(types.Content(role=role, parts=parts))
    return contents


def stream_reply(api_key: str, model: str, system_prompt: str, messages: list[dict]):
    client = genai.Client(api_key=api_key)
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=_build_contents(messages),
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    ):
        if chunk.text:
            yield chunk.text
