"""
Context managers for resource management.

Provides safe resource handling with automatic cleanup.
"""

import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def temp_file_context(
    suffix: str | None = None,
    prefix: str | None = None,
    delete: bool = True,
) -> AsyncIterator[str]:
    """
    Context manager for temporary files with automatic cleanup.

    Args:
        suffix: File suffix (e.g., '.pdf')
        prefix: File prefix
        delete: Whether to delete file on exit

    Yields:
        Path to temporary file

    Example:
        async with temp_file_context(suffix='.pdf') as temp_path:
            # Use temp_path
            pass
        # File automatically deleted
    """
    temp_fd = None
    temp_path = None

    try:
        temp_fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        os.close(temp_fd)  # Close file descriptor, we'll use path
        logger.debug(f"Created temp file: {temp_path}")
        yield temp_path
    finally:
        if delete and temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                logger.debug(f"Deleted temp file: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_path}: {e}")


@asynccontextmanager
async def temp_directory_context(
    suffix: str | None = None,
    prefix: str | None = None,
    delete: bool = True,
) -> AsyncIterator[Path]:
    """
    Context manager for temporary directories with automatic cleanup.

    Args:
        suffix: Directory suffix
        prefix: Directory prefix
        delete: Whether to delete directory on exit

    Yields:
        Path to temporary directory

    Example:
        async with temp_directory_context() as temp_dir:
            # Use temp_dir
            file_path = temp_dir / "file.txt"
            pass
        # Directory automatically deleted
    """
    temp_dir = None

    try:
        temp_dir = Path(
            tempfile.mkdtemp(suffix=suffix, prefix=prefix)
        )
        logger.debug(f"Created temp directory: {temp_dir}")
        yield temp_dir
    finally:
        if delete and temp_dir and temp_dir.exists():
            try:
                import shutil

                shutil.rmtree(temp_dir)
                logger.debug(f"Deleted temp directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to delete temp directory {temp_dir}: {e}")


@asynccontextmanager
async def multiple_temp_files_context(
    count: int,
    suffix: str | None = None,
    prefix: str | None = None,
    delete: bool = True,
) -> AsyncIterator[list[str]]:
    """
    Context manager for multiple temporary files.

    Args:
        count: Number of temp files to create
        suffix: File suffix
        prefix: File prefix
        delete: Whether to delete files on exit

    Yields:
        List of temp file paths

    Example:
        async with multiple_temp_files_context(3, suffix='.pdf') as temp_files:
            # Use temp_files[0], temp_files[1], temp_files[2]
            pass
        # All files automatically deleted
    """
    temp_files: list[str] = []

    try:
        for i in range(count):
            temp_fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            os.close(temp_fd)
            temp_files.append(temp_path)
            logger.debug(f"Created temp file {i+1}/{count}: {temp_path}")

        yield temp_files
    finally:
        if delete:
            for temp_path in temp_files:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                        logger.debug(f"Deleted temp file: {temp_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete temp file {temp_path}: {e}")
