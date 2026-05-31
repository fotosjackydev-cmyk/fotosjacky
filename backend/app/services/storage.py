# =============================================================================
# Servicio — Storage de Imágenes
# Sube y elimina imágenes de Supabase Storage
# =============================================================================
import uuid
from fastapi import UploadFile
from app.database import get_supabase_admin
from app.config import settings


async def upload_product_image(file: UploadFile, product_id: str) -> str:
    """
    Sube una imagen de producto a Supabase Storage.
    Retorna la URL pública de la imagen.

    Estructura en el bucket:
        product-images/{product_id}/{uuid}.{ext}
    """
    db = get_supabase_admin()

    # Determinar extensión del archivo
    ext_map = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }
    ext = ext_map.get(file.content_type, "jpg")

    # Generar nombre único
    filename = f"{product_id}/{uuid.uuid4().hex}.{ext}"

    # Leer contenido del archivo
    content = await file.read()

    # Subir a Supabase Storage
    db.storage.from_(settings.STORAGE_BUCKET).upload(
        path=filename,
        file=content,
        file_options={
            "content-type": file.content_type,
            "cache-control": "public, max-age=31536000",  # 1 año de cache
        },
    )

    # Obtener URL pública
    public_url = db.storage.from_(settings.STORAGE_BUCKET).get_public_url(filename)

    return public_url


async def delete_image(image_url: str) -> None:
    """
    Elimina una imagen de Supabase Storage a partir de su URL pública.
    Extrae el path relativo de la URL para el borrado.
    """
    db = get_supabase_admin()

    # Extraer el path del archivo desde la URL
    # URL formato: https://xxx.supabase.co/storage/v1/object/public/product-images/path
    bucket_name = settings.STORAGE_BUCKET
    marker = f"/object/public/{bucket_name}/"

    if marker in image_url:
        file_path = image_url.split(marker)[1]
        db.storage.from_(bucket_name).remove([file_path])
