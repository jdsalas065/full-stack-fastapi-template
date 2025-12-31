#!/usr/bin/env python3
"""Initialize MinIO bucket for file storage."""

import sys

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def init_minio() -> None:
    """Initialize MinIO bucket if it doesn't exist."""
    try:
        logger.info("Initializing MinIO...")
        logger.info(f"Connecting to MinIO at {settings.MINIO_ENDPOINT}")
        
        # Create MinIO client
        client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        
        # Check if bucket exists
        bucket_name = settings.MINIO_BUCKET
        if client.bucket_exists(bucket_name):
            logger.info(f"Bucket '{bucket_name}' already exists")
        else:
            # Create bucket
            client.make_bucket(bucket_name)
            logger.info(f"Created bucket '{bucket_name}'")
        
        logger.info("MinIO initialization completed successfully")
        
    except S3Error as e:
        logger.error(f"MinIO S3 Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"MinIO initialization error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_minio()
