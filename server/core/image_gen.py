import logfire
from google import genai
from google.genai import types
from core.constants import IMAGE_GEN_MODEL

async def generate_image_bytes(prompt: str, reference_images: list[bytes] = None) -> bytes:
    """
    Uses the modern Google GenAI SDK to generate images.
    Takes a string prompt and an optional list of raw image bytes (reference images).
    Returns the raw binary bytes of the generated image.
    """
    
    client = genai.Client()
    
    # Construct the multimodal payload
    contents = [prompt]
    
    if reference_images:
        for img_bytes in reference_images:
            contents.append(
                types.Part.from_bytes(
                    data=img_bytes,
                    mime_type='image/jpeg' # Defaulting to jpeg for API compatibility
                )
            )
            
    logfire.info(f"Creating image with {len(reference_images) if reference_images else 0} reference images.")
    
    try:
        response = client.models.generate_content(
            model=IMAGE_GEN_MODEL,
            contents=contents
        )
        
        # Extract the image from the returned parts
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    return part.inline_data.data
                    
        raise ValueError("The model responded, but no image data was found in the return parts.")
    
    except Exception as e:
        logfire.warning(f"generate_content failed ({e})")
