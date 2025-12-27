"""
Document Comparison Service.

Handles comparison and verification of two documents for consistency.
Combines OCR results with AI analysis for comprehensive comparison.
"""

import time
from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.core.logging import get_logger
from app.models.document import Document, DocumentComparison
from app.schemas.document import DocumentComparisonResponse
from app.services.ocr_service import ocr_service
from app.services.openai_service import openai_service

logger = get_logger(__name__)


class DocumentComparisonService:
    """
    Service for comparing documents and verifying consistency.
    
    This service:
    1. Retrieves documents and their OCR text
    2. Performs text-based similarity comparison
    3. Uses AI (ChatGPT) for semantic analysis
    4. Returns comprehensive comparison results
    """

    async def compare_documents(
        self,
        document_1: Document,
        document_2: Document,
        use_ai_analysis: bool = True,
        comparison_prompt: Optional[str] = None,
    ) -> DocumentComparisonResponse:
        """
        Compare two documents for consistency.
        
        Args:
            document_1: First document to compare
            document_2: Second document to compare
            use_ai_analysis: Whether to use AI for detailed analysis
            comparison_prompt: Custom prompt for AI comparison
            
        Returns:
            DocumentComparisonResponse with comparison results
            
        Example:
            >>> comparison_service = DocumentComparisonService()
            >>> result = await comparison_service.compare_documents(doc1, doc2)
            >>> print(f"Similarity: {result.similarity_score}")
        """
        start_time = time.time()
        
        logger.info(
            f"Comparing documents: {document_1.id} and {document_2.id}"
        )
        
        # Ensure both documents have been processed with OCR
        if not document_1.ocr_text or not document_2.ocr_text:
            raise ValueError("Both documents must have OCR text extracted")
        
        # Calculate basic text similarity
        similarity_score = self._calculate_text_similarity(
            document_1.ocr_text,
            document_2.ocr_text,
        )
        
        # Use AI for detailed analysis if requested
        ai_analysis = None
        differences = []
        comparison_method = "text_similarity"
        
        if use_ai_analysis:
            try:
                ai_result = await openai_service.compare_documents(
                    document_1.ocr_text,
                    document_2.ocr_text,
                    comparison_prompt,
                )
                ai_analysis = ai_result["analysis"]
                differences = ai_result["key_differences"]
                comparison_method = "ai_assisted"
                
                # Adjust similarity based on AI analysis
                if ai_result["similarity_assessment"] == "High":
                    similarity_score = max(similarity_score, 0.8)
                elif ai_result["similarity_assessment"] == "Low":
                    similarity_score = min(similarity_score, 0.5)
                    
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                # Fall back to basic comparison
                differences = self._extract_basic_differences(
                    document_1.ocr_text,
                    document_2.ocr_text,
                )
        else:
            differences = self._extract_basic_differences(
                document_1.ocr_text,
                document_2.ocr_text,
            )
        
        # Determine if documents are consistent
        is_consistent = similarity_score >= 0.75 and len(differences) <= 3
        
        processing_time = time.time() - start_time
        
        comparison_id = str(uuid4())
        
        return DocumentComparisonResponse(
            comparison_id=comparison_id,
            document_1_id=document_1.id or "",
            document_2_id=document_2.id or "",
            similarity_score=similarity_score,
            is_consistent=is_consistent,
            differences=differences,
            ai_analysis=ai_analysis,
            comparison_method=comparison_method,
            processing_time_seconds=round(processing_time, 2),
            comparison_date=datetime.now(),
        )

    def _calculate_text_similarity(
        self,
        text1: str,
        text2: str,
    ) -> float:
        """
        Calculate similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # TODO: Implement proper text similarity algorithm
        # Options:
        # 1. Levenshtein distance
        # 2. Cosine similarity with TF-IDF
        # 3. Sentence embeddings (e.g., Sentence-BERT)
        # 4. difflib.SequenceMatcher
        
        # Simple placeholder using difflib
        from difflib import SequenceMatcher
        
        similarity = SequenceMatcher(None, text1, text2).ratio()
        return round(similarity, 2)

    def _extract_basic_differences(
        self,
        text1: str,
        text2: str,
    ) -> list[str]:
        """
        Extract basic differences between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            List of identified differences
        """
        # TODO: Implement proper diff algorithm
        # Could use:
        # - difflib for line-by-line comparison
        # - Longest Common Subsequence (LCS)
        # - Custom domain-specific logic
        
        differences = []
        
        # Simple word count difference
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        unique_to_1 = words1 - words2
        unique_to_2 = words2 - words1
        
        if unique_to_1:
            differences.append(
                f"Document 1 contains {len(unique_to_1)} unique terms"
            )
        
        if unique_to_2:
            differences.append(
                f"Document 2 contains {len(unique_to_2)} unique terms"
            )
        
        # Length difference
        len_diff = abs(len(text1) - len(text2))
        if len_diff > 100:
            differences.append(
                f"Documents differ in length by {len_diff} characters"
            )
        
        return differences[:5]  # Return top 5 differences


# Singleton instance
comparison_service = DocumentComparisonService()
