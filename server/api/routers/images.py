import logfire
from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from fastapi.responses import Response
from typing import List, Optional
from core.image_gen import generate_image_bytes

router = APIRouter()

@router.post("/generate")
async def generate_image_endpoint(
    prompt: str = Form(...),
    reference_image: Optional[UploadFile] = File(None)
):
    """
    Generate an image.
    Accepts a prompt (string) and an optional reference image file.
    Returns the raw JPEG image bytes natively.
    """
    logfire.info(f"Received image generation request. Prompt: '{prompt}', Reference Image Included: {bool(reference_image and reference_image.filename)}")
    
    image_bytes_list = []
    if reference_image and reference_image.filename:
        # Read the uploaded multipart file directly into memory bytes
        content = await reference_image.read()
        if content:
            image_bytes_list.append(content)
                
    try:
        result_bytes = await generate_image_bytes(prompt, image_bytes_list)
        return Response(content=result_bytes, media_type="image/jpeg")
        
    except Exception as e:
        logfire.error(f"Error generating image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
