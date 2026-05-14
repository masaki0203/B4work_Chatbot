from google import genai
from google.genai import types


def generate_image(api_key: str, prompt: str, model: str = "imagen-3.0-generate-002") -> list[bytes]:
    """プロンプトから画像を生成してバイト列のリストで返す。"""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=types.GenerateImagesConfig(number_of_images=1),
    )
    return [img.image.image_bytes for img in response.generated_images]
