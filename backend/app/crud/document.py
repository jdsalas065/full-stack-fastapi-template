"""
CRUD operations for document management.

Database operations for creating, reading, updating, and deleting documents.
This would typically use SQLAlchemy/SQLModel for database interactions.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.core.logging import get_logger
from app.models.document import Document, DocumentComparison, DocumentStatus

logger = get_logger(__name__)

# In-memory storage for demonstration
# In production, this would use a database
_documents_store: dict[str, Document] = {}
_comparisons_store: dict[str, DocumentComparison] = {}


class DocumentCRUD:
    """
    CRUD operations for documents.
    
    This is a template implementation using in-memory storage.
    In production, replace with actual database operations.
    """

    async def create(self, document: Document) -> Document:
        """
        Create a new document record.
        
        Args:
            document: Document object to create
            
        Returns:
            Created document with assigned ID
        """
        document.id = str(uuid4())
        document.uploaded_at = datetime.now()
        
        _documents_store[document.id] = document
        logger.info(f"Created document: {document.id}")
        
        return document

    async def get(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        document = _documents_store.get(document_id)
        if document:
            logger.info(f"Retrieved document: {document_id}")
        else:
            logger.warning(f"Document not found: {document_id}")
        
        return document

    async def update(self, document_id: str, **kwargs) -> Optional[Document]:
        """
        Update a document.
        
        Args:
            document_id: Document ID
            **kwargs: Fields to update
            
        Returns:
            Updated document if found, None otherwise
        """
        document = _documents_store.get(document_id)
        if not document:
            logger.warning(f"Cannot update, document not found: {document_id}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(document, key):
                setattr(document, key, value)
        
        logger.info(f"Updated document: {document_id}")
        return document

    async def delete(self, document_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted, False if not found
        """
        if document_id in _documents_store:
            del _documents_store[document_id]
            logger.info(f"Deleted document: {document_id}")
            return True
        
        logger.warning(f"Cannot delete, document not found: {document_id}")
        return False

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[DocumentStatus] = None,
    ) -> list[Document]:
        """
        List documents with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter
            
        Returns:
            List of documents
        """
        documents = list(_documents_store.values())
        
        if status:
            documents = [d for d in documents if d.status == status]
        
        documents.sort(key=lambda x: x.uploaded_at, reverse=True)
        
        return documents[skip : skip + limit]


class ComparisonCRUD:
    """
    CRUD operations for document comparisons.
    
    This is a template implementation using in-memory storage.
    """

    async def create(self, comparison: DocumentComparison) -> DocumentComparison:
        """
        Create a new comparison record.
        
        Args:
            comparison: Comparison object to create
            
        Returns:
            Created comparison with assigned ID
        """
        comparison.id = str(uuid4())
        comparison.comparison_date = datetime.now()
        
        _comparisons_store[comparison.id] = comparison
        logger.info(f"Created comparison: {comparison.id}")
        
        return comparison

    async def get(self, comparison_id: str) -> Optional[DocumentComparison]:
        """
        Retrieve a comparison by ID.
        
        Args:
            comparison_id: Comparison ID
            
        Returns:
            Comparison if found, None otherwise
        """
        return _comparisons_store.get(comparison_id)

    async def list_by_document(
        self,
        document_id: str,
        limit: int = 50,
    ) -> list[DocumentComparison]:
        """
        List comparisons involving a specific document.
        
        Args:
            document_id: Document ID
            limit: Maximum number of records to return
            
        Returns:
            List of comparisons
        """
        comparisons = [
            c
            for c in _comparisons_store.values()
            if c.document_1_id == document_id or c.document_2_id == document_id
        ]
        
        comparisons.sort(key=lambda x: x.comparison_date, reverse=True)
        
        return comparisons[:limit]


# Singleton instances
document_crud = DocumentCRUD()
comparison_crud = ComparisonCRUD()
