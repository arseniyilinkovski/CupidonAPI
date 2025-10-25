import os
import tempfile
import uuid

import cloudinary.uploader
import pycountry
from fastapi import UploadFile, HTTPException, Request
from starlette import status
from nsfw_detector import predict


def get_valid_regions(country_code: str) -> set[str]:
    return {
        subdivision.name
        for subdivision in pycountry.subdivisions
        if subdivision.country_code == country_code
    }


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB = 5


def upload_photo_to_cloudinary(photo: UploadFile, request: Request) -> dict:
    nsfw_model = request.app.state.nsfw_model
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
    if not is_image_safe(photo, nsfw_model):
        raise HTTPException(
            status_code=status. HTTP_400_BAD_REQUEST,
            detail="Фото содержит неприемлемый контент"
        )

    unique_filename = str(uuid.uuid4())
    photo.file.seek(0)
    result = cloudinary.uploader.upload(
        photo.file,
        public_id=unique_filename,
        folder="user_photos",
        resource_type="image"
    )
    return {
        "photo_url": result["secure_url"],
        "photo_public_id": result["public_id"]
    }


def is_image_safe(photo: UploadFile, model) -> bool:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(photo.file.read())
        tmp_path = tmp.name

    result = predict.classify(model, tmp_path)
    os.remove(tmp_path)

    scores = result[tmp_path]
    print(scores)
    return not (
        scores["porn"] >= 0.2 or
        scores["hentai"] >= 0.3 or
        scores["sexy"] >= 0.5
    )


def delete_photo_from_cloudinary(public_id: str):
    print("delete_photo_from_cloudinary")
    try:
        print(public_id)
        cloudinary.uploader.destroy(public_id)
        print("Файл удален")
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")




