"""
Document processing routes.

Implements document processing and comparison endpoints using:
- MinIO streaming for file access
- LLM OCR for PDF processing
- Field extraction and comparison
"""

import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.core.constants import Tags
from app.core.logging import get_logger
from app.schemas.document import (
    CompareDocumentRequest,
    CompareDocumentResponse,
    DocumentSubmissionRequest,
    DocumentSubmissionResponse,
)
from app.services.document_processor import document_processor
from app.services.field_comparison_service import field_comparison_service
from app.services.storage_service import storage_service

logger = get_logger(__name__)

router = APIRouter(prefix="/document", tags=[Tags.DOCUMENT])


@router.post(
    "/process_document_submission",
    response_model=DocumentSubmissionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Process document submission",
    description=(
        "Process multiple documents, extract fields using LLM OCR, "
        "and compare field-by-field."
    ),
)
async def process_document_submission(
    payload: DocumentSubmissionRequest,
    background_tasks: BackgroundTasks,
) -> DocumentSubmissionResponse:
    """
    Process document submission with field extraction and comparison.

    Flow:
    1. Load files from MinIO (streaming)
    2. Process each file (Excel parsing or LLM OCR for PDF)
    3. Extract structured fields
    4. Compare fields across documents
    5. Save OCR results to MinIO
    6. Return comparison results

    Args:
        payload: Document submission request containing task_id
        background_tasks: FastAPI background tasks

    Returns:
        DocumentSubmissionResponse with processing results

    Raises:
        HTTPException: If processing fails
    """
    try:
        task_id = payload.task_id

        # Step 1: List files
        files = await storage_service.list_files(task_id)
        if not files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No files found for task_id: {task_id}",
            )

        logger.info(f"Processing {len(files)} files for task {task_id}")

        # Step 2: Process files in parallel (streaming from MinIO)
        processing_tasks = []
        for file_info in files:
            # Skip OCR results file if present
            if file_info["name"].endswith("ocr_results.json"):
                continue

            file_stream = await storage_service.get_file_stream(file_info["name"])
            task = document_processor.process_file(
                file_stream,
                file_info["name"],
            )
            processing_tasks.append(task)

        # Wait for all processing to complete
        document_results = await asyncio.gather(
            *processing_tasks, return_exceptions=True
        )

        # Handle errors
        valid_results = []
        for idx, result in enumerate(document_results):
            if isinstance(result, Exception):
                logger.error(
                    f"Error processing {files[idx]['name']}: {result}",
                    exc_info=result,
                )
                continue
            valid_results.append(result)

        if not valid_results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process any documents",
            )

        # Step 3: Compare fields
        comparison_result = field_comparison_service.compare_documents(
            valid_results
        )

        # Step 4: Save OCR results to MinIO
        ocr_results = {
            "task_id": task_id,
            "document_results": valid_results,
            "comparison_result": comparison_result,
            "processed_at": datetime.utcnow().isoformat(),
        }

        # Save in background
        background_tasks.add_task(
            storage_service.save_ocr_result,
            task_id,
            ocr_results,
        )

        # Return results
        return DocumentSubmissionResponse(
            status="processed",
            result={
                "task_id": task_id,
                "documents_processed": len(valid_results),
                "comparison": comparison_result,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in process_document_submission: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}",
        )


@router.post(
    "/compare_document_contents",
    response_model=CompareDocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare document contents",
    description=(
        "Compare Excel and PDF documents using LLM OCR "
        "and extract field differences."
    ),
)
async def compare_document_contents(
    payload: CompareDocumentRequest,
) -> CompareDocumentResponse:
    """
    Compare Excel and PDF documents using LLM OCR.

    Flow:
    1. Load files from MinIO (streaming)
    2. Process Excel (parse) and PDF (LLM OCR)
    3. Extract fields from both
    4. Compare field-by-field
    5. Save OCR results
    6. Return detailed differences

    Args:
        payload: Compare document request containing task_id and file names

    Returns:
        CompareDocumentResponse with comparison results

    Raises:
        HTTPException: If comparison fails
    """
    try:
        task_id = payload.task_id.strip()
        excel_file_name = payload.excel_file_name.strip()
        pdf_file_name = payload.pdf_file_name.strip()

        logger.info(
            f"Comparing documents - task_id: {task_id}, "
            f"excel: {excel_file_name}, pdf: {pdf_file_name}"
        )

        # Step 1: Load files (streaming)
        excel_object_name = f"{task_id}/{excel_file_name}"
        pdf_object_name = f"{task_id}/{pdf_file_name}"

        excel_stream = await storage_service.get_file_stream(excel_object_name)
        pdf_stream = await storage_service.get_file_stream(pdf_object_name)

        # Step 2: Process files in parallel
        excel_result, pdf_result = await asyncio.gather(
            document_processor.process_file(excel_stream, excel_file_name, "excel"),
            document_processor.process_file(pdf_stream, pdf_file_name, "pdf"),
        )

        # Step 3: Compare
        comparison = field_comparison_service.compare_documents([
            excel_result,
            pdf_result,
        ])

        # Step 4: Save OCR results
        ocr_results = {
            "task_id": task_id,
            "excel_result": excel_result,
            "pdf_result": pdf_result,
            "comparison": comparison,
            "processed_at": datetime.utcnow().isoformat(),
        }

        await storage_service.save_ocr_result(task_id, ocr_results)

        return CompareDocumentResponse(
            status="compared",
            result=comparison,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error in compare_document_contents: {e}",
            exc_info=e,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document comparison failed: {str(e)}",
        )
