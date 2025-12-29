"""
LLM-based OCR service using GPT-4 Vision.

Uses OpenAI's GPT-4 Vision model to extract text and structured data
from document images with high accuracy.
"""

import asyncio
import base64
import json
from io import BytesIO
from typing import Any

from openai import AsyncOpenAI
from PIL import Image

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMOCRService:
    """LLM-based OCR using GPT-4 Vision."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def _encode_image(self, image: Image.Image) -> str:
        """
        Encode PIL Image to base64.

        Args:
            image: PIL Image object

        Returns:
            Base64 encoded string
        """
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    async def extract_text_from_image(
        self,
        image: Image.Image,
        extract_fields: bool = True,
    ) -> dict[str, Any]:
        """
        Extract text and structured data from image using LLM.

        Args:
            image: PIL Image object
            extract_fields: If True, extract structured fields (amounts, dates, etc.)

        Returns:
            Dictionary with:
            - text: Raw extracted text
            - fields: Structured fields (if extract_fields=True)
            - confidence: Not applicable for LLM, but included for compatibility
        """
        try:
            # Encode image
            base64_image = self._encode_image(image)

            # Prepare prompt
            if extract_fields:
                prompt = """
                Analyze this document image and extract:
                1. All text content (preserve structure)
                2. Structured fields:
                   - Amounts (numbers with currency)
                   - Dates
                   - Names/Companies
                   - Line items (if table format)
                   - Reference numbers
                   - Any other important fields

                Return as JSON with structure:
                {
                    "text": "full text content",
                    "fields": {
                        "amounts": [...],
                        "dates": [...],
                        "line_items": [...],
                        ...
                    }
                }
                """
            else:
                prompt = (
                    "Extract all text from this image. "
                    "Preserve the structure and formatting."
                )

            # Call GPT-4 Vision
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert at extracting text and structured data "
                            "from document images. Always return valid JSON."
                        ),
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high",  # High detail for better OCR
                                },
                            },
                        ],
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for consistent extraction
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)

            # Ensure structure
            if extract_fields:
                return {
                    "text": result.get("text", ""),
                    "fields": result.get("fields", {}),
                    "confidence": 1.0,  # LLM doesn't provide confidence score
                    "raw_response": result,
                }
            else:
                return {
                    "text": result.get("text", ""),
                    "fields": {},
                    "confidence": 1.0,
                }

        except Exception as e:
            logger.error(f"Error in LLM OCR: {e}")
            raise

    async def extract_from_images(
        self,
        images: list[Image.Image],
        extract_fields: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Extract text from multiple images (parallel processing).

        Args:
            images: List of PIL Image objects
            extract_fields: If True, extract structured fields

        Returns:
            List of extraction results, one per image
        """
        tasks = [
            self.extract_text_from_image(img, extract_fields) for img in images
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle errors
        extracted_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error extracting from image {idx}: {result}")
                extracted_results.append({
                    "page_num": idx,
                    "text": "",
                    "fields": {},
                    "confidence": 0.0,
                    "error": str(result),
                })
            else:
                result["page_num"] = idx
                extracted_results.append(result)

        return extracted_results


# Singleton instance
llm_ocr_service = LLMOCRService()

