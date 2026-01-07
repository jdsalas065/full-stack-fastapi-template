import uuid
from datetime import timedelta
from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class MinIOService:
    def __init__(self) -> None:
        self.client = Minio(
            settings.MINIO_URL,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Ensure the bucket exists, create it if it doesn't."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise Exception(f"Error ensuring bucket exists: {str(e)}")

    def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        folder: str | None = None,
    ) -> tuple[str, int]:
        """
        Upload a file to MinIO.
        Returns (file_path, file_size).
        """
        try:
            # Generate file path
            file_id = str(uuid.uuid4())
            if folder:
                file_path = f"{folder}/{file_id}_{filename}"
            else:
                file_path = f"{file_id}_{filename}"

            # Upload file
            file_stream = BytesIO(file_data)
            file_size = len(file_data)

            self.client.put_object(
                self.bucket_name,
                file_path,
                file_stream,
                file_size,
                content_type=content_type,
            )

            return file_path, file_size
        except S3Error as e:
            raise Exception(f"Error uploading file: {str(e)}")

    def get_presigned_url(self, file_path: str, expires: timedelta = timedelta(hours=1)) -> str:
        """
        Get a presigned URL for downloading a file.
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                file_path,
                expires=expires,
            )
            return url
        except S3Error as e:
            raise Exception(f"Error generating presigned URL: {str(e)}")

    def delete_file(self, file_path: str) -> None:
        """
        Delete a file from MinIO.
        """
        try:
            self.client.remove_object(self.bucket_name, file_path)
        except S3Error as e:
            raise Exception(f"Error deleting file: {str(e)}")

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in MinIO.
        """
        try:
            self.client.stat_object(self.bucket_name, file_path)
            return True
        except S3Error:
            return False


# Singleton instance
minio_service = MinIOService()
