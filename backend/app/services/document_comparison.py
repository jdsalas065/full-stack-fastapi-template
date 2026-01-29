"""
Document comparison module for comparing Excel and PDF documents.

This module implements the flow for comparing documents:
1. load_document_set: Download files from MinIO to local directory
2. classify_input_documents: Classify documents by pattern matching
3. compare_document_pair (CDP): Compare Excel and PDF documents with visual diff
4. compare_document_pair_optimized: Optimized version with parallel processing

Libraries used:
- Step 3 (classify): os (Python standard library)
- Step 4.1 (conversion): os, subprocess (Python standard library)
- Step 4.2 (PDF to images): pdf2image, cv2 (opencv-python)
- Step 4.3 (OCR): openai, base64, re, time (Python standard library)
- Step 4.4 (draw boxes): cv2 (opencv-python)
- Step 4.5 (storage): minio

External services:
- LibreOffice (soffice): Excel to PDF conversion
- VLM API: Vision Language Model for OCR with bounding boxes
- MinIO Server: Object storage for processed images
"""

import asyncio
import base64
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from openai import OpenAI
from pdf2image import convert_from_path
from PIL import Image

from app.core.config import settings
from app.core.logging import get_logger
from app.services.storage_service import storage_service

logger = get_logger(__name__)

# Base path for document storage
BASE_DOCUMENT_PATH = Path("/tmp/documents")


async def load_document_set(task_id: str) -> Path:
    """
    Load document set from MinIO storage to local directory.

    Downloads all files associated with a task_id from MinIO bucket
    to a local directory structure.

    Args:
        task_id: Unique identifier for the task

    Returns:
        Path to the local directory containing downloaded files

    Raises:
        Exception: If download fails
    """
    logger.info(f"Loading document set for task_id: {task_id}")

    # Create local directory for task
    task_dir = BASE_DOCUMENT_PATH / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    # List all files in MinIO for this task
    files = await storage_service.list_files(task_id)

    if not files:
        logger.warning(f"No files found for task_id: {task_id}")
        return task_dir

    # Download each file
    for file_info in files:
        object_name = file_info["name"]
        # Extract just the filename without the task_id prefix
        filename = object_name.split("/")[-1]
        local_path = task_dir / filename

        # Download file to local path
        temp_path = await storage_service.download_file_to_temp(object_name)
        # Move from temp to task directory
        import shutil

        shutil.move(temp_path, local_path)
        logger.info(f"Downloaded {filename} to {local_path}")

    return task_dir


def classify_input_documents(task_id: str) -> dict[str, str | list[str]]:
    """
    Classify documents in a task directory by pattern matching.

    Scans the local directory and classifies files based on naming patterns
    and file extensions.

    Args:
        task_id: Unique identifier for the task

    Returns:
        Dictionary with document type keys and filename values:
        - settle_file_name: Settle document (contains "Settle", .XLSX/.XLS)
        - einvoice_file_name: E-invoice (contains "VAT" or "E-INV", .XML)
        - cinvoice_file_name: Commercial Invoice (contains "CI", .XLSX/.XLS)
        - packing_list_file_name: Packing List (contains "PKL", .XLSX/.XLS)
        - cinvoice_plist_file_name: Combined CI&PKL (contains "CI&PKL", .XLSX/.XLS)
        - export_CD_file_name: Export CD (contains "TKX", .XLSX/.XLS, can be list)
        - PO_SO_file_name: PO/SO (contains "PO"/"SO"/"PC"/"SC", .XLSX/.XLS)
    """
    logger.info(f"Classifying documents for task_id: {task_id}")

    task_dir = BASE_DOCUMENT_PATH / task_id
    if not task_dir.exists():
        logger.warning(f"Task directory not found: {task_dir}")
        return {}

    result: dict[str, str | list[str]] = {}
    export_cd_files: list[str] = []

    # Scan directory
    for file_path in task_dir.iterdir():
        if not file_path.is_file():
            continue

        filename = file_path.name
        filename_upper = filename.upper()
        file_ext = file_path.suffix.upper()

        # Classify by pattern
        if "SETTLE" in filename_upper and file_ext in [".XLSX", ".XLS"]:
            result["settle_file_name"] = filename
            logger.info(f"Classified as settle: {filename}")

        elif ("VAT" in filename_upper or "E-INV" in filename_upper) and file_ext == ".XML":
            result["einvoice_file_name"] = filename
            logger.info(f"Classified as e-invoice: {filename}")

        elif "CI&PKL" in filename_upper and file_ext in [".XLSX", ".XLS"]:
            result["cinvoice_plist_file_name"] = filename
            logger.info(f"Classified as CI&PKL: {filename}")

        elif "CI" in filename_upper and file_ext in [".XLSX", ".XLS"]:
            # Check if not already classified as CI&PKL
            if "cinvoice_plist_file_name" not in result or result["cinvoice_plist_file_name"] != filename:
                result["cinvoice_file_name"] = filename
                logger.info(f"Classified as commercial invoice: {filename}")

        elif "PKL" in filename_upper and file_ext in [".XLSX", ".XLS"]:
            # Check if not already classified as CI&PKL
            if "cinvoice_plist_file_name" not in result or result["cinvoice_plist_file_name"] != filename:
                result["packing_list_file_name"] = filename
                logger.info(f"Classified as packing list: {filename}")

        elif "TKX" in filename_upper and file_ext in [".XLSX", ".XLS"]:
            export_cd_files.append(filename)
            logger.info(f"Classified as export CD: {filename}")

        elif any(
            keyword in filename_upper for keyword in ["PO", "SO", "PC", "SC"]
        ) and file_ext in [".XLSX", ".XLS"]:
            result["PO_SO_file_name"] = filename
            logger.info(f"Classified as PO/SO: {filename}")

    # Add export CD files (can be multiple)
    if export_cd_files:
        result["export_CD_file_name"] = export_cd_files

    logger.info(f"Classification result: {result}")
    return result


def convert_excel_to_pdf(excel_path: Path) -> Path:
    """
    Convert Excel file to PDF using LibreOffice (soffice headless).

    Args:
        excel_path: Path to the Excel file

    Returns:
        Path to the generated PDF file

    Raises:
        FileNotFoundError: If Excel file doesn't exist
        subprocess.CalledProcessError: If conversion fails
    """
    logger.info(f"Converting Excel to PDF: {excel_path}")

    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    # Generate output path
    output_dir = excel_path.parent
    pdf_path = excel_path.with_suffix(".pdf")

    try:
        # Use LibreOffice to convert Excel to PDF
        subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(output_dir),
                str(excel_path),
            ],
            check=True,
            capture_output=True,
            timeout=60,
        )

        logger.info(f"Converted Excel to PDF: {pdf_path}")
        return pdf_path

    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting Excel to PDF: {e.stderr.decode()}")
        raise
    except subprocess.TimeoutExpired:
        logger.error("Excel to PDF conversion timed out")
        raise


def export_pdf_to_images(pdf_path: Path, dpi: int = 200) -> tuple[list[Path], int]:
    """
    Export PDF pages to JPG images using pdf2image.

    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for image conversion (default: 200)

    Returns:
        Tuple of (list of image file paths, number of pages)

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If conversion fails
    """
    logger.info(f"Exporting PDF to images: {pdf_path} (DPI: {dpi})")

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        # Convert PDF to images
        images = convert_from_path(str(pdf_path), dpi=dpi)
        num_pages = len(images)

        # Save images
        image_paths: list[Path] = []
        for i, image in enumerate(images, start=1):
            # Create image filename
            image_path = pdf_path.parent / f"{pdf_path.stem}_page_{i}.jpg"

            # Crop white space (optional)
            image_array = np.array(image)
            # Find non-white pixels
            non_white = np.where(
                (image_array[:, :, 0] < 250)
                | (image_array[:, :, 1] < 250)
                | (image_array[:, :, 2] < 250)
            )

            if len(non_white[0]) > 0 and len(non_white[1]) > 0:
                # Crop to content
                y_min, y_max = non_white[0].min(), non_white[0].max()
                x_min, x_max = non_white[1].min(), non_white[1].max()
                cropped = image.crop((x_min, y_min, x_max + 1, y_max + 1))
            else:
                cropped = image

            # Save image
            cropped.save(image_path, "JPEG", quality=95)
            image_paths.append(image_path)
            logger.info(f"Saved image: {image_path}")

        logger.info(f"Exported {num_pages} pages to images")
        return image_paths, num_pages

    except Exception as e:
        logger.error(f"Error exporting PDF to images: {str(e)}")
        raise


def extract_OCR_texts_2(image_path: Path) -> tuple[list[str], list[tuple[int, int, int, int]]]:
    """
    Extract text and bounding boxes from image using VLM (Vision Language Model) API.

    Uses OpenAI SDK configured with custom VLM endpoint to extract text and
    bounding box coordinates from images.

    Args:
        image_path: Path to the image file

    Returns:
        Tuple of (list of text strings, list of bounding boxes)
        Bounding box format: (x, y, width, height)

    Raises:
        Exception: If VLM API call fails
    """
    logger.info(f"Extracting OCR text from: {image_path} using VLM API")

    try:
        # Load and encode image to base64
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")

        # Configure OpenAI client with custom VLM endpoint
        if settings.VLM_ENDPOINT:
            client = OpenAI(
                api_key=settings.VLM_API_KEY or settings.OPENAI_API_KEY,
                base_url=settings.VLM_ENDPOINT,
            )
            model = settings.VLM_ID or settings.OPENAI_MODEL
        else:
            # Fall back to standard OpenAI if VLM not configured
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            model = settings.OPENAI_MODEL

        # Prepare prompt for OCR with bounding boxes
        prompt = """
        Extract all text from this image along with bounding box coordinates.
        For each text element, provide:
        - text: the text content
        - x: left coordinate
        - y: top coordinate
        - width: width of bounding box
        - height: height of bounding box
        
        Return as JSON array: [{"text": "...", "x": 0, "y": 0, "width": 0, "height": 0}, ...]
        """

        # Call VLM API
        start_time = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=4096,
        )
        elapsed_time = time.time() - start_time
        logger.info(f"VLM API call took {elapsed_time:.2f}s")

        # Parse response
        content = response.choices[0].message.content
        
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON array directly
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = content

        import json
        ocr_results = json.loads(json_str)

        texts: list[str] = []
        bboxes: list[tuple[int, int, int, int]] = []

        # Extract text and bounding boxes from VLM response
        for item in ocr_results:
            if isinstance(item, dict) and "text" in item:
                text = item["text"]
                x = int(item.get("x", 0))
                y = int(item.get("y", 0))
                w = int(item.get("width", 0))
                h = int(item.get("height", 0))

                if text.strip():  # Skip empty text
                    texts.append(text)
                    bboxes.append((x, y, w, h))

        logger.info(f"Extracted {len(texts)} text elements using VLM")
        return texts, bboxes

    except Exception as e:
        logger.error(f"Error extracting OCR text with VLM: {str(e)}")
        # Log more details for debugging
        logger.error(f"VLM_ENDPOINT: {settings.VLM_ENDPOINT}")
        logger.error(f"VLM_ID: {settings.VLM_ID}")
        raise


def find_text_differences(
    texts1: list[str],
    texts2: list[str],
) -> tuple[list[int], list[int]]:
    """
    Find differences between two text sets.

    Normalizes texts (remove spaces, uppercase) and compares them.

    Args:
        texts1: First list of text strings
        texts2: Second list of text strings

    Returns:
        Tuple of (indices of different texts in texts1, indices in texts2)
    """
    logger.info(f"Finding text differences between {len(texts1)} and {len(texts2)} texts")

    # Normalize function
    def normalize(text: str) -> str:
        return re.sub(r"\s+", "", text).upper()

    # Normalize all texts
    norm_texts1 = [normalize(t) for t in texts1]
    norm_texts2 = [normalize(t) for t in texts2]

    # Find differences
    diff_indices1: list[int] = []
    diff_indices2: list[int] = []

    # Compare texts
    for i, text1_norm in enumerate(norm_texts1):
        if text1_norm not in norm_texts2:
            diff_indices1.append(i)

    for i, text2_norm in enumerate(norm_texts2):
        if text2_norm not in norm_texts1:
            diff_indices2.append(i)

    logger.info(
        f"Found {len(diff_indices1)} differences in first doc, "
        f"{len(diff_indices2)} in second doc"
    )
    return diff_indices1, diff_indices2


def draw_bounding_boxes(
    image_path: Path,
    bboxes: list[tuple[int, int, int, int]],
    indices: list[int],
    output_suffix: str = "_with_bboxes",
) -> Path:
    """
    Draw bounding boxes on image using OpenCV.

    Args:
        image_path: Path to the image file
        bboxes: List of bounding boxes (x, y, w, h)
        indices: Indices of bboxes to highlight
        output_suffix: Suffix to add to output filename

    Returns:
        Path to the output image with bounding boxes
    """
    logger.info(f"Drawing {len(indices)} bounding boxes on: {image_path}")

    try:
        # Load image with OpenCV
        image = cv2.imread(str(image_path))

        # Draw bounding boxes for differences
        for idx in indices:
            if idx < len(bboxes):
                x, y, w, h = bboxes[idx]
                # Draw rectangle (color: red, thickness: 2)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Generate output path
        output_path = image_path.parent / f"{image_path.stem}{output_suffix}.jpg"

        # Save image
        cv2.imwrite(str(output_path), image)
        logger.info(f"Saved image with bounding boxes: {output_path}")

        return output_path

    except Exception as e:
        logger.error(f"Error drawing bounding boxes: {str(e)}")
        raise


async def save_image_to_storage(
    task_id: str,
    image_path: Path,
) -> str:
    """
    Upload image to MinIO storage output bucket.

    Uploads processed images with bounding box annotations to the
    vpas-output bucket in MinIO.

    Args:
        task_id: Unique identifier for the task
        image_path: Path to the image file

    Returns:
        Object name in MinIO storage

    Raises:
        Exception: If upload fails
    """
    logger.info(f"Uploading image to vpas-output bucket: {image_path}")

    try:
        # Determine object name in MinIO output bucket
        filename = image_path.name
        object_name = f"{task_id}/{filename}"

        # Upload to MinIO output bucket (vpas-output)
        await storage_service.upload_file(
            str(image_path),
            object_name,
            content_type="image/jpeg",
            bucket=settings.MINIO_OUTPUT_BUCKET,
        )

        logger.info(f"Uploaded image to output bucket: {object_name}")
        return object_name

    except Exception as e:
        logger.error(f"Error uploading image to storage: {str(e)}")
        raise


async def compare_document_pair(
    task_id: str,
    excel_file_name: str,
    pdf_file_name: str,
) -> list[dict[str, str]]:
    """
    Compare Excel and PDF documents (CDP function).

    Performs visual comparison between Excel and PDF documents:
    1. Handle duplicate names
    2. Convert Excel to PDF
    3. Export both PDFs to images
    4. Extract text and bounding boxes from images
    5. Find differences
    6. Draw bounding boxes on images
    7. Upload results to storage

    Args:
        task_id: Unique identifier for the task
        excel_file_name: Name of the Excel file
        pdf_file_name: Name of the PDF file

    Returns:
        List of dictionaries containing result image names:
        [{"EXCEL": "excel_page_1_with_bboxes.jpg", "PDF": "pdf_page_1_with_bboxes.jpg"}, ...]

    Raises:
        ValueError: If page counts don't match
        Exception: If comparison fails
    """
    logger.info(
        f"Comparing document pair - task_id: {task_id}, "
        f"excel: {excel_file_name}, pdf: {pdf_file_name}"
    )

    task_dir = BASE_DOCUMENT_PATH / task_id
    excel_path = task_dir / excel_file_name
    pdf_path = task_dir / pdf_file_name

    # Verify files exist
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    result_images: list[dict[str, str]] = []

    try:
        # Step 1: Handle duplicate names
        excel_stem = excel_path.stem
        pdf_stem = pdf_path.stem

        if excel_stem == pdf_stem:
            # Rename Excel file to avoid collision
            renamed_excel_path = task_dir / f"{excel_stem}_RENAMED{excel_path.suffix}"
            excel_path.rename(renamed_excel_path)
            excel_path = renamed_excel_path
            logger.info(f"Renamed Excel file to avoid collision: {excel_path}")

        # Step 2: Convert Excel to PDF
        excel_pdf_path = convert_excel_to_pdf(excel_path)

        # Step 3: Export Excel PDF to images
        excel_image_paths, excel_num_pages = export_pdf_to_images(excel_pdf_path)

        # Step 4: Export PDF to images
        pdf_image_paths, pdf_num_pages = export_pdf_to_images(pdf_path)

        # Step 5: Check page count
        if excel_num_pages != pdf_num_pages:
            error_msg = (
                f"INVALID! The two docs have different numbers of pages! "
                f"Excel: {excel_num_pages}, PDF: {pdf_num_pages}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Step 6: Compare each page
        for page_num in range(excel_num_pages):
            excel_img_path = excel_image_paths[page_num]
            pdf_img_path = pdf_image_paths[page_num]

            # Extract OCR texts and bounding boxes
            excel_texts, excel_bboxes = extract_OCR_texts_2(excel_img_path)
            pdf_texts, pdf_bboxes = extract_OCR_texts_2(pdf_img_path)

            # Find differences
            excel_diff_indices, pdf_diff_indices = find_text_differences(
                excel_texts, pdf_texts
            )

            # Draw bounding boxes
            excel_bbox_path = draw_bounding_boxes(
                excel_img_path, excel_bboxes, excel_diff_indices
            )
            pdf_bbox_path = draw_bounding_boxes(
                pdf_img_path, pdf_bboxes, pdf_diff_indices
            )

            # Upload to storage
            await save_image_to_storage(task_id, excel_bbox_path)
            await save_image_to_storage(task_id, pdf_bbox_path)

            # Add to result
            result_images.append(
                {
                    "EXCEL": excel_bbox_path.name,
                    "PDF": pdf_bbox_path.name,
                }
            )

            logger.info(f"Processed page {page_num + 1}/{excel_num_pages}")

        logger.info(f"Document comparison completed. Generated {len(result_images)} result pages")
        return result_images

    except Exception as e:
        logger.error(f"Error comparing document pair: {str(e)}")
        raise


async def compare_document_pair_optimized(
    task_id: str,
    excel_file_name: str,
    pdf_file_name: str,
) -> list[dict[str, str]]:
    """
    Optimized version of compare_document_pair with parallel processing.

    Performs visual comparison between Excel and PDF documents:
    1. Handle duplicate names
    2. Convert Excel to PDF
    3. Export both PDFs to images (concurrent)
    4. Extract text and bounding boxes from images (parallel processing)
    5. Find differences (parallel)
    6. Draw bounding boxes on images (parallel)
    7. Upload results to storage (parallel)

    Optimizations:
    - Parallel PDF to image conversion where possible
    - Parallel OCR extraction for all pages
    - Parallel bounding box drawing
    - Parallel upload to storage
    - Better error handling with granular recovery

    Args:
        task_id: Unique identifier for the task
        excel_file_name: Name of the Excel file
        pdf_file_name: Name of the PDF file

    Returns:
        List of dictionaries containing result image names:
        [{"EXCEL": "excel_page_1_with_bboxes.jpg", "PDF": "pdf_page_1_with_bboxes.jpg"}, ...]

    Raises:
        ValueError: If page counts don't match
        Exception: If comparison fails
    """
    logger.info(
        f"[OPTIMIZED] Comparing document pair - task_id: {task_id}, "
        f"excel: {excel_file_name}, pdf: {pdf_file_name}"
    )

    task_dir = BASE_DOCUMENT_PATH / task_id
    excel_path = task_dir / excel_file_name
    pdf_path = task_dir / pdf_file_name

    # Verify files exist
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    result_images: list[dict[str, str]] = []

    try:
        # Step 1: Handle duplicate names
        excel_stem = excel_path.stem
        pdf_stem = pdf_path.stem

        if excel_stem == pdf_stem:
            # Rename Excel file to avoid collision
            renamed_excel_path = task_dir / f"{excel_stem}_RENAMED{excel_path.suffix}"
            excel_path.rename(renamed_excel_path)
            excel_path = renamed_excel_path
            logger.info(f"Renamed Excel file to avoid collision: {excel_path}")

        # Step 2: Convert Excel to PDF (blocking operation, but necessary)
        excel_pdf_path = await asyncio.to_thread(convert_excel_to_pdf, excel_path)

        # Step 3: Export both PDFs to images concurrently
        logger.info("Exporting PDFs to images in parallel...")
        excel_images_task = asyncio.to_thread(export_pdf_to_images, excel_pdf_path)
        pdf_images_task = asyncio.to_thread(export_pdf_to_images, pdf_path)
        
        (excel_image_paths, excel_num_pages), (pdf_image_paths, pdf_num_pages) = (
            await asyncio.gather(excel_images_task, pdf_images_task)
        )

        # Step 4: Check page count
        if excel_num_pages != pdf_num_pages:
            error_msg = (
                f"INVALID! The two docs have different numbers of pages! "
                f"Excel: {excel_num_pages}, PDF: {pdf_num_pages}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Processing {excel_num_pages} pages in parallel...")

        # Step 5: Process all pages in parallel
        page_tasks = []
        for page_num in range(excel_num_pages):
            task = _process_page_pair(
                task_id,
                excel_image_paths[page_num],
                pdf_image_paths[page_num],
                page_num,
                excel_num_pages,
            )
            page_tasks.append(task)

        # Wait for all pages to be processed
        page_results = await asyncio.gather(*page_tasks, return_exceptions=True)

        # Collect results and handle errors
        for idx, result in enumerate(page_results):
            if isinstance(result, Exception):
                logger.error(f"Error processing page {idx + 1}: {result}", exc_info=result)
                # Continue processing other pages
                continue
            if result:
                result_images.append(result)

        if not result_images:
            raise Exception("Failed to process any pages")

        logger.info(
            f"[OPTIMIZED] Document comparison completed. "
            f"Generated {len(result_images)} result pages"
        )
        return result_images

    except Exception as e:
        logger.error(f"Error in optimized document comparison: {str(e)}")
        raise


async def _process_page_pair(
    task_id: str,
    excel_img_path: Path,
    pdf_img_path: Path,
    page_num: int,
    total_pages: int,
) -> dict[str, str]:
    """
    Process a single page pair (Excel and PDF) in parallel.

    Extracts OCR text, finds differences, draws bounding boxes,
    and uploads results to storage.

    Args:
        task_id: Unique identifier for the task
        excel_img_path: Path to Excel page image
        pdf_img_path: Path to PDF page image
        page_num: Current page number (0-indexed)
        total_pages: Total number of pages

    Returns:
        Dictionary with EXCEL and PDF result image names

    Raises:
        Exception: If processing fails
    """
    try:
        # Step 1: Extract OCR texts and bounding boxes in parallel
        logger.debug(f"Page {page_num + 1}/{total_pages}: Extracting OCR text...")
        excel_ocr_task = asyncio.to_thread(extract_OCR_texts_2, excel_img_path)
        pdf_ocr_task = asyncio.to_thread(extract_OCR_texts_2, pdf_img_path)
        
        (excel_texts, excel_bboxes), (pdf_texts, pdf_bboxes) = await asyncio.gather(
            excel_ocr_task, pdf_ocr_task
        )

        # Step 2: Find differences (CPU-bound but fast)
        logger.debug(f"Page {page_num + 1}/{total_pages}: Finding differences...")
        excel_diff_indices, pdf_diff_indices = find_text_differences(
            excel_texts, pdf_texts
        )

        # Step 3: Draw bounding boxes in parallel
        logger.debug(f"Page {page_num + 1}/{total_pages}: Drawing bounding boxes...")
        excel_bbox_task = asyncio.to_thread(
            draw_bounding_boxes, excel_img_path, excel_bboxes, excel_diff_indices
        )
        pdf_bbox_task = asyncio.to_thread(
            draw_bounding_boxes, pdf_img_path, pdf_bboxes, pdf_diff_indices
        )
        
        excel_bbox_path, pdf_bbox_path = await asyncio.gather(
            excel_bbox_task, pdf_bbox_task
        )

        # Step 4: Upload to storage in parallel
        logger.debug(f"Page {page_num + 1}/{total_pages}: Uploading to storage...")
        await asyncio.gather(
            save_image_to_storage(task_id, excel_bbox_path),
            save_image_to_storage(task_id, pdf_bbox_path),
        )

        logger.info(f"Page {page_num + 1}/{total_pages}: Processing completed")

        # Return result
        return {
            "EXCEL": excel_bbox_path.name,
            "PDF": pdf_bbox_path.name,
        }

    except Exception as e:
        logger.error(
            f"Error processing page {page_num + 1}/{total_pages}: {str(e)}",
            exc_info=e,
        )
        raise


# Alias for CDP
CDP = compare_document_pair
# New optimized alias
CDP_optimized = compare_document_pair_optimized
