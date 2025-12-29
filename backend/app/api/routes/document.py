"""
Document processing routes.

This module implements the document submission processing endpoint,
migrated from Flask to FastAPI.
"""

import asyncio
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status

# MinIO client import (placeholder - install minio package if needed)
# from minio import Minio
from app.core.constants import Tags
from app.core.logging import get_logger
from app.schemas.document import (
    CompareDocumentRequest,
    CompareDocumentResponse,
    DocumentSubmissionRequest,
    DocumentSubmissionResponse,
)

logger = get_logger(__name__)

# Placeholder imports for business classes
# These would normally be in separate modules
# from app.models.settlement import Settlement
# from app.models.item_master import ItemMaster
# ... other business class imports


# MinIO Configuration (similar to Flask configuration)
# TODO: Move these to environment variables or config file for production
# SECURITY: Do not hardcode credentials in production code
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_SECURE = False
MINIO_BUCKET = "test1"  # Default bucket name

# File path constants
# TODO: Make these configurable via environment variables or config file
# These are temporary paths - adjust for your deployment environment
PDF_FILE_PATH = "/tmp/pdf_files"
DOWNLOAD_FILE_PATH = "/tmp/downloads"
BASE_DOCUMENT_PATH = "/tmp/documents"

# Initialize MinIO client (placeholder)
# minio_client = Minio(
#     MINIO_ENDPOINT,
#     access_key=MINIO_ACCESS_KEY,
#     secret_key=MINIO_SECRET_KEY,
#     secure=MINIO_SECURE
# )

# Helper function to get MinIO client (lazy initialization)
def get_minio_client() -> Any:
    """
    Get MinIO client instance.

    Returns:
        Minio client instance or None if not initialized

    Note:
        Uncomment when minio package is installed:
        from minio import Minio
        return Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY,
                     secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)
    """
    # Placeholder - return None until minio is installed
    return None

router = APIRouter(prefix="/document", tags=[Tags.DOCUMENT])


# Helper functions - Improved async implementations
async def load_document_set(task_id: str, bucket: str = MINIO_BUCKET) -> dict[str, Any]:
    """
    Load document set for the given task ID from MinIO.

    This is an improved async version that addresses issues in the Flask implementation:
    - Uses async/await for non-blocking I/O operations
    - Uses pathlib.Path for cross-platform path handling
    - Includes proper error handling and logging
    - Avoids file system cleanup (uses temp directories managed by OS)
    - Returns metadata about downloaded files instead of just side effects

    Args:
        task_id: Unique identifier for the task
        bucket: MinIO bucket name (default: MINIO_BUCKET)

    Returns:
        Dictionary containing:
        - task_id: The task identifier
        - documents: List of downloaded document metadata
        - item_master_path: Path to Item_Master.xlsx
        - download_dir: Directory where files were downloaded

    Raises:
        HTTPException: If MinIO operations fail

    Example:
        result = await load_document_set("task-123")
        # Returns:
        # {
        #     "task_id": "task-123",
        #     "documents": [
        #         {"name": "doc1.pdf", "size": 1024, "path": "/tmp/documents/task-123/doc1.pdf"},
        #         ...
        #     ],
        #     "item_master_path": "/tmp/documents/task-123/Item_Master.xlsx",
        #     "download_dir": "/tmp/documents/task-123"
        # }
    """
    logger.info(f"Loading document set for task_id: {task_id}")

    try:
        # Create task-specific directory using pathlib
        task_dir = Path(BASE_DOCUMENT_PATH) / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Created/verified directory: {task_dir}")

        # Get MinIO client
        minio_client = get_minio_client()

        # If MinIO client is not available (placeholder mode), return mock data
        if minio_client is None:
            logger.warning("MinIO client not initialized - returning placeholder data")
            return {
                "task_id": task_id,
                "documents": [],
                "item_master_path": str(task_dir / "Item_Master.xlsx"),
                "download_dir": str(task_dir),
                "status": "placeholder_mode"
            }

        # Download Item_Master.xlsx (shared across all tasks)
        item_master_path = task_dir / "Item_Master.xlsx"
        await asyncio.to_thread(
            _download_file_from_minio,
            minio_client,
            bucket,
            "item_master",
            item_master_path
        )
        logger.info(f"Downloaded Item_Master.xlsx to {item_master_path}")

        # List and download all files for this task_id
        documents = []
        prefix = f"{task_id}/"

        # Use asyncio.to_thread to run blocking MinIO operations in thread pool
        file_objects = await asyncio.to_thread(
            list,
            minio_client.list_objects(bucket, prefix=prefix, recursive=False)
        )

        # Download each file asynchronously
        download_tasks = []
        for file_obj in file_objects:
            file_path = task_dir / Path(file_obj.object_name).name
            download_tasks.append(
                asyncio.to_thread(
                    _download_file_from_minio,
                    minio_client,
                    bucket,
                    file_obj.object_name,
                    file_path
                )
            )

        # Wait for all downloads to complete
        downloaded_files = await asyncio.gather(*download_tasks, return_exceptions=True)

        # Collect metadata about downloaded files
        for idx, file_obj in enumerate(file_objects):
            if isinstance(downloaded_files[idx], Exception):
                logger.error(f"Failed to download {file_obj.object_name}: {downloaded_files[idx]}")
                continue

            file_path = task_dir / Path(file_obj.object_name).name
            if file_path.exists():
                documents.append({
                    "name": file_obj.object_name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "downloaded": True
                })

        logger.info(f"Successfully downloaded {len(documents)} documents for task {task_id}")

        return {
            "task_id": task_id,
            "documents": documents,
            "item_master_path": str(item_master_path),
            "download_dir": str(task_dir),
            "total_files": len(documents)
        }

    except Exception as e:
        logger.error(f"Error loading document set for task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load documents from MinIO: {str(e)}"
        )


def _download_file_from_minio(
    client: Any, bucket: str, object_name: str, file_path: Path
) -> None:
    """
    Download a file from MinIO to local path.

    This is a synchronous helper function to be run in a thread pool.

    Args:
        client: MinIO client instance
        bucket: Bucket name
        object_name: Object name in MinIO
        file_path: Local file path to save to

    Raises:
        Exception: If download fails
    """
    obj = client.get_object(bucket, object_name)
    try:
        data = obj.read()
        file_path.write_bytes(data)
    finally:
        obj.close()
        obj.release_conn()


def classify_input_documents(task_id: str) -> dict[str, Any]:
    """
    Classify input documents based on their content and type.

    Args:
        task_id: Unique identifier for the task

    Returns:
        Dictionary containing classification results

    TODO: Implement document classification logic
    - Analyze document content
    - Determine document types
    - Apply business rules for classification
    """
    # Placeholder implementation
    return {"task_id": task_id, "classification": "pending"}


def compare_document_pair(
    task_id: str, excel_file_name: str, pdf_file_name: str
) -> dict[str, Any]:
    """
    Compare content between an Excel file and a PDF file using OCR.

    This function uses OCR-based comparison by:
    1. Converting Excel to PDF
    2. Converting both PDFs to images
    3. Extracting text via OCR
    4. Comparing the extracted texts

    Args:
        task_id: Unique identifier for the task
        excel_file_name: Name of the Excel file to compare
        pdf_file_name: Name of the PDF file to compare

    Returns:
        Dictionary containing comparison results with:
        - task_id: Task identifier
        - excel_file: Excel filename
        - pdf_file: PDF filename
        - comparison_status: success/partial/failed
        - comparison_method: "ocr" indicating OCR-based comparison
        - similarity_score: Overall similarity percentage
        - matches: List of matching text segments
        - differences: List of differences found
        - excel_only: Text found only in Excel
        - pdf_only: Text found only in PDF
        - summary: Statistics about comparison

    Raises:
        FileNotFoundError: If files don't exist
        ValueError: If files cannot be processed

    Libraries used:
        - pdf2image: Convert PDF to images
        - openpyxl/libreoffice: Convert Excel to PDF
        - pytesseract: OCR text extraction
    """
    logger.info(f"Comparing documents using OCR for task {task_id}: {excel_file_name} vs {pdf_file_name}")

    try:
        # Import OCR tools
        from app.services.ocr_tools import (
            compare_ocr_texts,
            convert_excel_to_pdf,
            convert_pdf_to_images,
            extract_ocr_texts,
        )

        # Get task directory
        task_dir = Path(BASE_DOCUMENT_PATH) / task_id

        # Build file paths
        excel_path = task_dir / excel_file_name
        pdf_path = task_dir / pdf_file_name

        # Check if files exist
        if not excel_path.exists():
            logger.error(f"Excel file not found: {excel_path}")
            return {
                "task_id": task_id,
                "excel_file": excel_file_name,
                "pdf_file": pdf_file_name,
                "comparison_status": "failed",
                "comparison_method": "ocr",
                "error": f"Excel file not found: {excel_file_name}",
                "similarity_score": 0.0,
                "matches": [],
                "differences": [],
                "excel_only": [],
                "pdf_only": [],
                "summary": {
                    "total_excel_pages": 0,
                    "total_pdf_pages": 0,
                    "comparison_note": "File not found"
                }
            }

        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return {
                "task_id": task_id,
                "excel_file": excel_file_name,
                "pdf_file": pdf_file_name,
                "comparison_status": "failed",
                "comparison_method": "ocr",
                "error": f"PDF file not found: {pdf_file_name}",
                "similarity_score": 0.0,
                "matches": [],
                "differences": [],
                "excel_only": [],
                "pdf_only": [],
                "summary": {
                    "total_excel_pages": 0,
                    "total_pdf_pages": 0,
                    "comparison_note": "File not found"
                }
            }

        logger.info(f"Files found: {excel_path.name} ({excel_path.stat().st_size} bytes), "
                   f"{pdf_path.name} ({pdf_path.stat().st_size} bytes)")

        # Step 1: Convert Excel to PDF
        logger.info("Step 1: Converting Excel to PDF")
        excel_pdf_path = convert_excel_to_pdf(excel_path)

        # Step 2: Convert both PDFs to images
        logger.info("Step 2: Converting Excel PDF to images")
        excel_images = convert_pdf_to_images(excel_pdf_path)

        logger.info("Step 2: Converting original PDF to images")
        pdf_images = convert_pdf_to_images(pdf_path)

        # Step 3: Extract text from images using OCR
        logger.info("Step 3: Extracting text from Excel images")
        excel_texts = extract_ocr_texts(excel_images)

        logger.info("Step 3: Extracting text from PDF images")
        pdf_texts = extract_ocr_texts(pdf_images)

        # Step 4: Compare the extracted texts
        logger.info("Step 4: Comparing extracted texts")
        comparison_result = compare_ocr_texts(excel_texts, pdf_texts)

        # Build final result
        result = {
            "task_id": task_id,
            "excel_file": excel_file_name,
            "pdf_file": pdf_file_name,
            "comparison_status": "success",
            "comparison_method": "ocr",
            "similarity_score": comparison_result.get("similarity_score", 0.0),
            "matches": comparison_result.get("matches", []),
            "differences": comparison_result.get("differences", []),
            "excel_only": comparison_result.get("excel_only", []),
            "pdf_only": comparison_result.get("pdf_only", []),
            "summary": {
                "total_excel_pages": comparison_result.get("total_excel_pages", 0),
                "total_pdf_pages": comparison_result.get("total_pdf_pages", 0),
                "similarity_score": comparison_result.get("similarity_score", 0.0),
                "comparison_note": "OCR-based comparison completed"
            }
        }

        logger.info(f"OCR comparison completed for task {task_id}")
        return result

    except Exception as e:
        logger.error(f"Error comparing documents for task {task_id}: {str(e)}")
        return {
            "task_id": task_id,
            "excel_file": excel_file_name,
            "pdf_file": pdf_file_name,
            "comparison_status": "error",
            "error": f"Comparison failed: {str(e)}",
            "matches": [],
            "mismatches": [],
            "excel_only": [],
            "pdf_only": [],
            "summary": {
                "total_excel_records": 0,
                "total_pdf_records": 0,
                "matched_records": 0,
                "mismatched_records": 0
            }
        }


def check_documents(task_id: str, document_names: dict[str, Any]) -> dict[str, Any]:
    """
    Check, compare and aggregate results between financial document types.

    This function validates and cross-references various financial documents including:
    - Settlement documents
    - E-Invoice
    - Commercial Invoice
    - Packing List
    - PO/SO (Purchase Order / Sales Order)
    - Export-CD (Export Custom Declaration)

    Args:
        task_id: Unique identifier for the task
        document_names: Dictionary containing classified document names and metadata

    Returns:
        Dictionary containing:
        - task_id: Task identifier
        - validation_status: Overall validation status (success/partial/failed)
        - checked_documents: List of documents that were checked
        - comparisons: Cross-document comparison results
        - errors: List of validation errors found
        - warnings: List of validation warnings
        - summary: Summary statistics

    Example:
        result = check_documents("task-123", {"settlement": ["doc1.pdf"], ...})
        # Returns comprehensive validation results with cross-references

    TODO: Implement detailed business logic for each document type
    - Parse Item_Master.xlsx for reference data
    - Extract data from each document type (PDF/Excel parsing)
    - Cross-validate amounts, quantities, dates between documents
    - Check for missing required documents
    - Validate data consistency across document types
    """
    logger.info(f"Checking documents for task_id: {task_id}")

    try:
        # Get the download directory for this task
        task_dir = Path(BASE_DOCUMENT_PATH) / task_id

        # Initialize result structure with explicit types
        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        comparisons: list[dict[str, Any]] = []
        missing_documents: list[str] = []

        # Define required document types for financial processing
        required_doc_types = [
            "settlement",
            "e_invoice",
            "commercial_invoice",
            "packing_list",
            "po_so",
            "export_cd"
        ]

        # Check if task directory exists
        if not task_dir.exists():
            errors.append({
                "type": "missing_directory",
                "message": f"Task directory not found: {task_dir}",
                "severity": "critical"
            })
            return {
                "task_id": task_id,
                "validation_status": "failed",
                "checked_documents": document_names,
                "comparisons": comparisons,
                "errors": errors,
                "warnings": warnings,
                "summary": {
                    "total_documents": 0,
                    "validated_documents": 0,
                    "failed_documents": 1,
                    "missing_documents": missing_documents
                }
            }

        # Check for Item_Master.xlsx
        item_master_path = task_dir / "Item_Master.xlsx"
        if not item_master_path.exists():
            warnings.append({
                "type": "missing_reference",
                "message": "Item_Master.xlsx not found - reference data unavailable",
                "severity": "medium"
            })

        # List all files in task directory
        task_files = list(task_dir.glob("*"))
        total_documents = len(task_files)

        logger.info(f"Found {total_documents} files in task directory")

        # Check for required document types
        # This is a placeholder - actual implementation would parse document_names
        # from classification results
        for doc_type in required_doc_types:
            # Placeholder check - in real implementation, check if documents
            # of each type exist based on classification results
            if doc_type not in str(document_names).lower():
                missing_documents.append(doc_type)
                warnings.append({
                    "type": "missing_document_type",
                    "message": f"No {doc_type} document found",
                    "doc_type": doc_type,
                    "severity": "high"
                })

        # Placeholder: Cross-document validation
        # In production, this would:
        # 1. Parse Item_Master.xlsx for reference data (item codes, prices, etc.)
        # 2. Extract structured data from each document type
        # 3. Compare amounts, quantities, dates across documents
        # 4. Validate business rules (e.g., Settlement amount matches Invoice total)

        comparison_results: dict[str, Any] = {
            "settlement_vs_invoice": {
                "status": "pending",
                "description": "Compare settlement amount with invoice total",
                "details": "TODO: Extract and compare amounts"
            },
            "invoice_vs_packing_list": {
                "status": "pending",
                "description": "Compare item quantities and descriptions",
                "details": "TODO: Extract and compare line items"
            },
            "po_so_vs_invoice": {
                "status": "pending",
                "description": "Verify invoice matches purchase/sales order",
                "details": "TODO: Match order references and amounts"
            },
            "export_cd_vs_commercial_invoice": {
                "status": "pending",
                "description": "Validate export declaration against commercial invoice",
                "details": "TODO: Compare customs data with invoice data"
            }
        }

        # Determine overall validation status
        validation_status = "success"
        failed_documents = 0

        if errors:
            validation_status = "failed"
            failed_documents = len(errors)
        elif warnings:
            validation_status = "partial"

        logger.info(f"Document check completed for task {task_id}: {validation_status}")

        return {
            "task_id": task_id,
            "validation_status": validation_status,
            "checked_documents": document_names,
            "comparisons": comparison_results,
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "total_documents": total_documents,
                "validated_documents": total_documents,
                "failed_documents": failed_documents,
                "missing_documents": missing_documents
            }
        }

    except Exception as e:
        logger.error(f"Error checking documents for task {task_id}: {str(e)}")
        return {
            "task_id": task_id,
            "validation_status": "error",
            "checked_documents": document_names,
            "comparisons": [],
            "errors": [{
                "type": "processing_error",
                "message": f"Failed to check documents: {str(e)}",
                "severity": "critical"
            }],
            "warnings": [],
            "summary": {
                "total_documents": 0,
                "validated_documents": 0,
                "failed_documents": 1,
                "missing_documents": []
            }
        }


@router.post(
    "/process_document_submission",
    response_model=DocumentSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Process document submission",
    description="Process a document submission request by loading, classifying, and checking documents."
)
async def process_document_submission(
    payload: DocumentSubmissionRequest
) -> DocumentSubmissionResponse:
    """
    Process document submission endpoint.

    This endpoint handles the complete document processing workflow:
    1. Load document set from storage
    2. Classify input documents
    3. Check documents for validity and completeness

    Args:
        payload: Document submission request containing task_id

    Returns:
        DocumentSubmissionResponse with processing results and status code 201

    Raises:
        HTTPException: 422 if payload validation fails (FastAPI automatic)
        HTTPException: 500 if processing fails

    Note:
        FastAPI automatically validates JSON content-type and returns 422
        for invalid JSON or non-JSON content.
    """
    try:
        # Extract task_id from payload
        task_id = payload.task_id

        # Step 1: Load document set (now async)
        # Returns metadata about downloaded files
        await load_document_set(task_id)

        # Step 2: Classify input documents
        classification_result = classify_input_documents(task_id)

        # Step 3: Check documents (using classification results as document names)
        check_result = check_documents(task_id, classification_result)

        # Return the check result with 201 status
        return DocumentSubmissionResponse(
            status="processed",
            result=check_result
        )

    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payload: {str(e)}"
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )


@router.post(
    "/compare_document_contents",
    response_model=CompareDocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare document contents",
    description="Compare content between an Excel file and a PDF file for a specific task."
)
async def compare_document_contents(
    payload: CompareDocumentRequest
) -> CompareDocumentResponse:
    """
    Compare document contents endpoint.

    This endpoint handles the document comparison workflow using OCR:
    1. Load document set from storage
    2. Classify input documents (identify document types)
    3. Compare Excel vs PDF content using OCR-based comparison
    4. Return detailed comparison results

    Workflow:
        load_document_set => classify_input_documents => compare_document_pair

    Args:
        payload: Compare document request containing task_id, excel_file_name, pdf_file_name

    Returns:
        CompareDocumentResponse with OCR comparison results and status code 200

    Raises:
        HTTPException: 422 if payload validation fails (FastAPI automatic)
        HTTPException: 404 if files not found
        HTTPException: 500 if comparison fails

    Note:
        FastAPI automatically validates JSON content-type and returns 422
        for invalid JSON or non-JSON content.
    """
    logger.info(f"Received compare request: {payload.model_dump()}")

    try:
        # Extract parameters from payload
        task_id = payload.task_id.strip()
        excel_file_name = payload.excel_file_name.strip()
        pdf_file_name = payload.pdf_file_name.strip()

        logger.info(f"Comparing documents - task_id: {task_id}, "
                   f"excel: {excel_file_name}, pdf: {pdf_file_name}")

        # Step 1: Load document set from MinIO
        logger.info("Step 1: Loading document set from MinIO")
        await load_document_set(task_id)

        # Step 2: Classify input documents (identify document types)
        logger.info("Step 2: Classifying input documents")
        classification_result = classify_input_documents(task_id)
        logger.info(f"Classification result: {classification_result}")

        # Step 3: Compare the document pair using OCR
        logger.info("Step 3: Comparing document pair using OCR")
        comparison_result = compare_document_pair(task_id, excel_file_name, pdf_file_name)

        # Check if comparison failed
        if comparison_result.get("comparison_status") == "failed":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=comparison_result.get("error", "Files not found")
            )

        if comparison_result.get("comparison_status") == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=comparison_result.get("error", "Comparison failed")
            )

        # Return successful comparison result
        return CompareDocumentResponse(
            status="compared",
            result=comparison_result
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payload: {str(e)}"
        )
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in compare_document_contents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document comparison failed: {str(e)}"
        )
