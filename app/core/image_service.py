import shutil
import os
from fastapi import UploadFile
from uuid import uuid4

UPLOAD_DIR = "app/static/uploads"

class ImageService:
    def __init__(self):
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

    async def upload_image(self, file: UploadFile) -> str:
        file_extension = file.filename.split(".")[-1]
        file_name = f"{uuid4()}.{file_extension}"
        file_path = f"{UPLOAD_DIR}/{file_name}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return f"/static/uploads/{file_name}"
