import shutil
from pathlib import Path
from fastapi import UploadFile

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_uploaded_images(
    person_image: UploadFile,
    cloth_image: UploadFile
):
    person_path = UPLOAD_DIR / person_image.filename
    cloth_path = UPLOAD_DIR / cloth_image.filename

    with open(person_path, "wb") as f:
        shutil.copyfileobj(person_image.file, f)

    with open(cloth_path, "wb") as f:
        shutil.copyfileobj(cloth_image.file, f)

    return person_path, cloth_path
