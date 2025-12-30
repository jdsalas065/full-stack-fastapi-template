"""
Field comparison service.

Compares extracted fields from multiple documents and identifies differences.
"""

from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class FieldComparisonService:
    """Compare extracted fields from multiple documents."""

    def compare_documents(
        self,
        document_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Compare multiple documents and identify field differences.

        Args:
            document_results: List of document extraction results

        Returns:
            Comparison results with:
            - field_comparisons: Field-by-field comparison
            - differences: List of differences
            - matches: List of matching fields
        """
        if len(document_results) < 2:
            return {
                "error": "Need at least 2 documents to compare",
                "field_comparisons": {},
                "differences": [],
                "matches": [],
            }

        # Extract all unique field names
        all_field_names = set()
        for doc in document_results:
            all_field_names.update(doc.get("fields", {}).keys())

        # Compare each field
        field_comparisons = {}
        differences = []
        matches = []

        for field_name in all_field_names:
            field_values = []
            for doc in document_results:
                field_value = doc.get("fields", {}).get(field_name, [])
                field_values.append(
                    {
                        "file_name": doc["file_name"],
                        "value": field_value,
                    }
                )

            # Compare field values
            comparison = self._compare_field(field_name, field_values)
            field_comparisons[field_name] = comparison

            if comparison["status"] == "match":
                matches.append(
                    {
                        "field": field_name,
                        "values": field_values,
                    }
                )
            else:
                differences.append(
                    {
                        "field": field_name,
                        "values": field_values,
                        "difference_type": comparison["difference_type"],
                    }
                )

        return {
            "field_comparisons": field_comparisons,
            "differences": differences,
            "matches": matches,
            "total_fields": len(all_field_names),
            "matched_fields": len(matches),
            "different_fields": len(differences),
        }

    def _compare_field(
        self,
        field_name: str,
        field_values: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Compare values of a specific field across documents.

        Args:
            field_name: Name of the field
            field_values: List of field values from different documents

        Returns:
            Comparison result dictionary
        """
        # Extract values
        values = [fv["value"] for fv in field_values]

        # Normalize values for comparison
        normalized_values = [self._normalize_value(v) for v in values]

        # Check if all values are the same
        if len({str(v) for v in normalized_values}) == 1:
            return {
                "status": "match",
                "values": field_values,
                "difference_type": None,
            }

        # Values are different
        return {
            "status": "different",
            "values": field_values,
            "difference_type": self._identify_difference_type(normalized_values),
        }

    def _normalize_value(self, value: Any) -> Any:
        """
        Normalize value for comparison.

        Args:
            value: Value to normalize

        Returns:
            Normalized value
        """
        if isinstance(value, list):
            return sorted([self._normalize_value(v) for v in value])
        elif isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            return value.strip().lower()
        else:
            return value

    def _identify_difference_type(self, values: list[Any]) -> str:
        """
        Identify type of difference.

        Args:
            values: List of values to compare

        Returns:
            Difference type string
        """
        # Check if numeric difference
        try:
            numeric_values = [
                float(v) for v in values if isinstance(v, (int, float, str))
            ]
            if len(numeric_values) == len(values):
                return "numeric_difference"
        except (ValueError, TypeError):
            pass

        # Check if missing in some documents
        if any(v is None or v == [] for v in values):
            return "missing_value"

        # Text difference
        return "text_difference"


# Singleton instance
field_comparison_service = FieldComparisonService()
