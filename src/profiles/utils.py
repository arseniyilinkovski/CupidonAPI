import uuid

import cloudinary.uploader
import pycountry
from fastapi import UploadFile, HTTPException
from starlette import status


def get_valid_regions(country_code: str) -> set[str]:
    return {
        subdivision.name
        for subdivision in pycountry.subdivisions
        if subdivision.country_code == country_code
    }


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB = 5


def upload_photo_to_cloudinary(photo: UploadFile) -> str:
    if photo.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть изображением"
        )
    photo.file.seek(0, 2)
    size_mb = photo.file.tell() / (1024 * 1024)
    photo.file.seek(0)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл слишком большой (макс. 5МВ)"
        )
    unique_filename = str(uuid.uuid4())

    result = cloudinary.uploader.upload(
        photo.file,
        public_id=unique_filename,
        folder="user_photos",
        overwrite=True,
        resource_type="image"
    )
    return result["secure_url"]
