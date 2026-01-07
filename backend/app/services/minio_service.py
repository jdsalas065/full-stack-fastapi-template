"""
MinIO service for submission file uploads.

Provides helper functions for managing submission files in MinIO storage.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from minio.error import S3Error

from app.core.config import settings
from app.core.logging import get_logger
from app.services.storage_service import storage_service

logger = get_logger(__name__)


async def ensure_bucket_exists() -> None:
    """
    Ensure the submissions bucket exists in MinIO.

    Creates the bucket if it doesn't exist.
    """
    try:
        bucket_exists = await asyncio.to_thread(
            storage_service.client.bucket_exists, settings.MINIO_BUCKET
        )
        if not bucket_exists:
            await asyncio.to_thread(
                storage_service.client.make_bucket, settings.MINIO_BUCKET
            )
            logger.info(f"Created bucket: {settings.MINIO_BUCKET}")
    except S3Error as e:
        logger.error(f"Error ensuring bucket exists: {e}")
        raise


async def upload_file_to_minio(
    task_id: UUID | str, file: UploadFile
) -> dict[str, str | int]:
    """
    Upload a file to MinIO storage.

    Args:
        task_id: Task/submission ID (or "root" for root uploads)
        file: File to upload

    Returns:
        Dictionary with file metadata:
            - file_name: Original filename
            - file_path: Full path in MinIO (object_name)
            - file_size: Size in bytes
            - content_type: MIME type

    Raises:
        S3Error: If MinIO operation fails
    """
    # Ensure bucket exists
    await ensure_bucket_exists()

    # Generate unique filename to avoid collisions
    filename = file.filename or "unnamed"
    # Add timestamp prefix to make filename unique
    import time

    timestamp = int(time.time() * 1000)
    unique_filename = f"{timestamp}_{filename}"

    # Determine object path
    if str(task_id) == "root":
        object_name = f"root/{unique_filename}"
    else:
        object_name = f"{task_id}/{unique_filename}"

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Save to temp file
    temp_fd, temp_path = tempfile.mkstemp(suffix=Path(filename).suffix)
    try:
        with os.fdopen(temp_fd, "wb") as f:
            f.write(content)

        # Upload to MinIO
        await storage_service.upload_file(
            temp_path,
            object_name,
            content_type=file.content_type,
        )

        return {
            "file_name": filename,
            "file_path": object_name,
            "file_size": file_size,
            "content_type": file.content_type or "application/octet-stream",
        }

    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except Exception as e:
            logger.warning(f"Failed to delete temp file {temp_path}: {e}")


async def delete_folder(task_id: UUID | str) -> None:
    """
    Delete all files in a task folder from MinIO.

    Args:
        task_id: Task/submission ID

    Raises:
        S3Error: If MinIO operation fails
    """
    prefix = f"{task_id}/"
    try:
        # List all objects with the prefix
        objects = await asyncio.to_thread(
            list,
            storage_service.client.list_objects(
                settings.MINIO_BUCKET, prefix=prefix, recursive=True
            ),
        )

        # Delete each object
        for obj in objects:
            await asyncio.to_thread(
                storage_service.client.remove_object,
                settings.MINIO_BUCKET,
                obj.object_name,
            )
            logger.info(f"Deleted {obj.object_name}")

        logger.info(f"Deleted folder: {prefix}")
    except S3Error as e:
        logger.error(f"Error deleting folder {prefix}: {e}")
        raise
