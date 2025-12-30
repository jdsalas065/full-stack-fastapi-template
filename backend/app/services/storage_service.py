"""
MinIO storage service with temp file support.

Provides async file operations from MinIO object storage,
downloading files to temp directory for processing.
"""

import asyncio
import json
import os
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """MinIO storage service with temp file support."""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET

    async def list_files(self, task_id: str) -> list[dict[str, Any]]:
        """
        List all files for a task_id.

        Args:
            task_id: Unique identifier for the task

        Returns:
            List of file metadata dictionaries

        Raises:
            S3Error: If MinIO operation fails
        """
        prefix = f"{task_id}/"
        try:
            objects = await asyncio.to_thread(
                list,
                self.client.list_objects(self.bucket, prefix=prefix, recursive=True),
            )
            return [
                {
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                }
                for obj in objects
            ]
        except S3Error as e:
            logger.error(f"Error listing files: {e}")
            raise

    async def download_file_to_temp(self, object_name: str) -> str:
        """
        Download file from MinIO to temp directory.

        Args:
            object_name: Object name in MinIO

        Returns:
            Path to the downloaded temp file

        Raises:
            S3Error: If MinIO operation fails
        """
        try:
            # Create temp file with proper extension
            file_ext = Path(object_name).suffix
            temp_fd, temp_path = tempfile.mkstemp(suffix=file_ext)
            os.close(temp_fd)
            
            # Download file to temp path
            await asyncio.to_thread(
                self.client.fget_object,
                self.bucket,
                object_name,
                temp_path,
            )
            logger.info(f"Downloaded {object_name} to {temp_path}")
            return temp_path
        except S3Error as e:
            logger.error(f"Error downloading file {object_name}: {e}")
            # Clean up temp file on error
            if 'temp_path' in locals():
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
            raise

    async def get_file_stream(self, object_name: str) -> BytesIO:
        """
        Get file as stream (in-memory, no disk I/O).
        
        DEPRECATED: Use download_file_to_temp instead.

        Args:
            object_name: Object name in MinIO

        Returns:
            BytesIO stream containing file data

        Raises:
            S3Error: If MinIO operation fails
        """
        try:
            response = await asyncio.to_thread(
                self.client.get_object,
                self.bucket,
                object_name,
            )
            # Read entire file into memory (for small-medium files)
            # For large files, consider chunked processing
            data = response.read()
            response.close()
            response.release_conn()
            return BytesIO(data)
        except S3Error as e:
            logger.error(f"Error getting file {object_name}: {e}")
            raise

    async def upload_file(self, file_path: str, object_name: str, content_type: str | None = None) -> str:
        """
        Upload file from local path to MinIO.

        Args:
            file_path: Local file path to upload
            object_name: Destination object name in MinIO
            content_type: Optional content type for the file

        Returns:
            Object name where file was uploaded

        Raises:
            S3Error: If MinIO operation fails
        """
        try:
            await asyncio.to_thread(
                self.client.fput_object,
                self.bucket,
                object_name,
                file_path,
                content_type=content_type,
            )
            logger.info(f"Uploaded {file_path} to {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise

    async def delete_file(self, object_name: str) -> None:
        """
        Delete file from MinIO.

        Args:
            object_name: Object name to delete

        Raises:
            S3Error: If MinIO operation fails
        """
        try:
            await asyncio.to_thread(
                self.client.remove_object,
                self.bucket,
                object_name,
            )
            logger.info(f"Deleted {object_name}")
        except S3Error as e:
            logger.error(f"Error deleting file {object_name}: {e}")
            raise

    async def save_ocr_result(self, task_id: str, result_data: dict[str, Any]) -> str:
        """
        Save OCR extraction results to MinIO.

        Args:
            task_id: Unique identifier for the task
            result_data: OCR results dictionary

        Returns:
            Object name where results were saved

        Raises:
            S3Error: If MinIO operation fails
        """
        object_name = f"{task_id}/ocr_results.json"
        data = json.dumps(result_data, indent=2).encode("utf-8")

        try:
            await asyncio.to_thread(
                self.client.put_object,
                self.bucket,
                object_name,
                BytesIO(data),
                length=len(data),
                content_type="application/json",
            )
            logger.info(f"Saved OCR results to {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Error saving OCR results: {e}")
            raise

    async def get_ocr_result(self, task_id: str) -> dict[str, Any] | None:
        """
        Retrieve saved OCR results.

        Args:
            task_id: Unique identifier for the task

        Returns:
            OCR results dictionary or None if not found

        Raises:
            S3Error: If MinIO operation fails (except NoSuchKey)
        """
        object_name = f"{task_id}/ocr_results.json"
        try:
            response = await asyncio.to_thread(
                self.client.get_object,
                self.bucket,
                object_name,
            )
            data = json.loads(response.read())
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            if e.code == "NoSuchKey":
                return None
            logger.error(f"Error getting OCR results: {e}")
            raise


# Singleton instance
storage_service = StorageService()

