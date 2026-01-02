"""
Listing Grader - Airbnb Visibility Score
Aligned with Airbnb's 2025 ranking algorithm
"""

__version__ = "2.0.0"

# v2 - Airbnb Algorithm Aligned (recommended)
from .grader_v2 import ListingGraderV2, GradeResultV2
from .scorer_v2 import (
    ListingData,
    CategoryScore,
    calculate_airbnb_score,
    score_to_grade,
    ALGORITHM_WEIGHTS,
    score_reviews,
    score_response,
    score_pricing,
    score_conversion,
    score_instant_book,
    score_cancellation,
    score_listing_quality,
    score_availability,
)

# Aliases for convenience
ListingGrader = ListingGraderV2
GradeResult = GradeResultV2

# v1 - Legacy (kept for backward compatibility)
from .grader import ListingGrader as ListingGraderV1

__all__ = [
    # v2 - Recommended
    "ListingGraderV2",
    "GradeResultV2",
    "ListingData",
    "CategoryScore",
    "calculate_airbnb_score",
    "score_to_grade",
    "ALGORITHM_WEIGHTS",
    
    # Scoring functions
    "score_reviews",
    "score_response", 
    "score_pricing",
    "score_conversion",
    "score_instant_book",
    "score_cancellation",
    "score_listing_quality",
    "score_availability",
    
    # Aliases
    "ListingGrader",
    "GradeResult",
    
    # v1 Legacy
    "ListingGraderV1",
]
