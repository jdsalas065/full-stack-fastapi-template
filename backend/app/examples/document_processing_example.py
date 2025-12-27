"""
Example usage of the Document Processing System.

This script demonstrates how to use the document processing services
in your application.
"""

import asyncio
from pathlib import Path

from app.core.logging import get_logger
from app.crud import document_crud
from app.models.document import Document, DocumentStatus, DocumentType
from app.services import comparison_service, ocr_service, openai_service

logger = get_logger(__name__)


async def example_upload_and_process():
    """Example: Upload and process a document with OCR."""
    logger.info("=== Example 1: Upload and Process Document ===")
    
    # Create a document record (simulating an upload)
    document = Document(
        filename="example_contract.pdf",
        file_path="/path/to/documents/example_contract.pdf",
        file_type=DocumentType.PDF,
        mime_type="application/pdf",
        size_bytes=245680,
        status=DocumentStatus.UPLOADED,
    )
    
    # Save to database
    document = await document_crud.create(document)
    logger.info(f"Document created with ID: {document.id}")
    
    # Process with OCR
    ocr_result = await ocr_service.extract_text(
        document.file_path,
        document.mime_type,
        language="vie+eng",
    )
    
    # Update document with OCR results
    await document_crud.update(
        document.id or "",
        ocr_text=ocr_result.text,
        ocr_confidence=ocr_result.confidence,
        status=DocumentStatus.COMPLETED,
    )
    
    logger.info(f"OCR completed with confidence: {ocr_result.confidence}")
    return document


async def example_compare_documents():
    """Example: Compare two documents for consistency."""
    logger.info("=== Example 2: Compare Documents ===")
    
    # Create two sample documents
    doc1 = Document(
        id="doc-1",
        filename="contract_v1.pdf",
        file_path="/path/to/contract_v1.pdf",
        file_type=DocumentType.PDF,
        mime_type="application/pdf",
        size_bytes=200000,
        status=DocumentStatus.COMPLETED,
        ocr_text="This is the first contract version with standard terms...",
        ocr_confidence=0.95,
    )
    
    doc2 = Document(
        id="doc-2",
        filename="contract_v2.pdf",
        file_path="/path/to/contract_v2.pdf",
        file_type=DocumentType.PDF,
        mime_type="application/pdf",
        size_bytes=205000,
        status=DocumentStatus.COMPLETED,
        ocr_text="This is the second contract version with standard terms and additional clauses...",
        ocr_confidence=0.96,
    )
    
    # Compare documents
    result = await comparison_service.compare_documents(
        doc1,
        doc2,
        use_ai_analysis=True,
    )
    
    logger.info(f"Similarity Score: {result.similarity_score}")
    logger.info(f"Is Consistent: {result.is_consistent}")
    logger.info(f"Differences: {result.differences}")
    
    if result.ai_analysis:
        logger.info(f"AI Analysis: {result.ai_analysis}")
    
    return result


async def example_ai_analysis():
    """Example: Use OpenAI for document analysis."""
    logger.info("=== Example 3: AI Document Analysis ===")
    
    document_text = """
    HỢP ĐỒNG MUA BÁN
    
    Bên A: Công ty ABC
    Bên B: Công ty XYZ
    
    Điều 1: Mục đích hợp đồng
    Bên A đồng ý bán và Bên B đồng ý mua sản phẩm theo các điều khoản sau...
    """
    
    # Analyze document
    analysis = await openai_service.analyze_document(
        document_text,
        analysis_prompt="Tóm tắt các điểm chính của hợp đồng này",
    )
    
    logger.info(f"Document Analysis:\n{analysis}")
    
    # Extract structured data
    structured_data = await openai_service.extract_structured_data(
        document_text,
        schema_description="Extract: parties (Bên A, Bên B), type of contract, main terms",
    )
    
    logger.info(f"Structured Data: {structured_data}")
    
    return analysis


async def example_batch_processing():
    """Example: Process multiple documents in batch."""
    logger.info("=== Example 4: Batch Document Processing ===")
    
    # Simulate multiple document uploads
    documents = []
    for i in range(3):
        doc = Document(
            filename=f"document_{i+1}.pdf",
            file_path=f"/path/to/document_{i+1}.pdf",
            file_type=DocumentType.PDF,
            mime_type="application/pdf",
            size_bytes=200000 + (i * 10000),
            status=DocumentStatus.UPLOADED,
        )
        doc = await document_crud.create(doc)
        documents.append(doc)
    
    # Process all documents
    for doc in documents:
        ocr_result = await ocr_service.extract_text(
            doc.file_path,
            doc.mime_type,
        )
        
        await document_crud.update(
            doc.id or "",
            ocr_text=ocr_result.text,
            ocr_confidence=ocr_result.confidence,
            status=DocumentStatus.COMPLETED,
        )
        
        logger.info(f"Processed: {doc.filename}")
    
    # List all documents
    all_docs = await document_crud.list(limit=10)
    logger.info(f"Total documents processed: {len(all_docs)}")
    
    return all_docs


async def main():
    """Run all examples."""
    try:
        # Example 1: Upload and process
        await example_upload_and_process()
        
        # Example 2: Compare documents
        await example_compare_documents()
        
        # Example 3: AI analysis
        await example_ai_analysis()
        
        # Example 4: Batch processing
        await example_batch_processing()
        
        logger.info("=== All examples completed successfully! ===")
        
    except Exception as e:
        logger.error(f"Error in examples: {e}", exc_info=True)


if __name__ == "__main__":
    # Note: This example uses placeholder implementations
    # To run with real data:
    # 1. Configure OpenAI API key in .env
    # 2. Install OCR dependencies (pytesseract, etc.)
    # 3. Update services with actual implementations
    
    asyncio.run(main())
