from fastapi import APIRouter, UploadFile, File
from services.tryon_service import save_uploaded_images

router = APIRouter()

@router.post("/upload")
async def upload_images(
    person_image: UploadFile = File(...),
    cloth_image: UploadFile = File(...)
):
    person_path, cloth_path = save_uploaded_images(
        person_image, cloth_image
    )
    return {
        "person_image": str(person_path),
        "cloth_image": str(cloth_path),
    }
