"""
Data models for Listing Grader
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class ListingData:
    """Raw listing data from Airbnb"""
    listing_id: str
    name: str = ""
    description: str = ""
    url: str = ""
    
    # Pricing
    price_per_night: float = 0
    cleaning_fee: float = 0
    service_fee: float = 0
    currency: str = "EUR"
    
    # Property details
    property_type: str = ""
    room_type: str = ""
    bedrooms: int = 0
    beds: int = 0
    bathrooms: float = 0
    max_guests: int = 0
    
    # Location
    city: str = ""
    neighborhood: str = ""
    latitude: float = 0
    longitude: float = 0
    
    # Reviews
    rating: float = 0
    reviews_count: int = 0
    
    # Host
    host_id: str = ""
    host_name: str = ""
    is_superhost: bool = False
    
    # Features
    instant_bookable: bool = False
    is_new: bool = False
    
    # Media
    images: List[str] = field(default_factory=list)
    amenities: List[str] = field(default_factory=list)
    amenity_ids: List[int] = field(default_factory=list)
    
    # Metadata
    scraped_at: str = ""


@dataclass
class CategoryScore:
    """Score for a single category"""
    score: int  # 0-100
    weight: float  # 0-1
    details: str = ""
    recommendations: List[str] = field(default_factory=list)


@dataclass
class GradeResult:
    """Complete grading result"""
    listing_id: str
    listing_url: str
    listing_name: str
    
    # Overall
    overall_score: int  # 0-100
    grade: str  # A+, A, B+, B, C+, C, D, F
    
    # Category scores (0-100)
    title_score: int
    description_score: int
    photos_score: int
    pricing_score: int
    amenities_score: int
    reviews_score: int
    
    # Insights
    recommendations: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    
    # Bonus points applied
    superhost_bonus: int = 0
    instant_book_bonus: int = 0
    
    # Market comparison (optional)
    market_percentile: int = 0
    competitor_avg_score: Optional[int] = None
    competitors_analyzed: int = 0
    
    # Metadata
    graded_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "listing_id": self.listing_id,
            "listing_url": self.listing_url,
            "listing_name": self.listing_name,
            "overall_score": self.overall_score,
            "grade": self.grade,
            "category_scores": {
                "title": self.title_score,
                "description": self.description_score,
                "photos": self.photos_score,
                "pricing": self.pricing_score,
                "amenities": self.amenities_score,
                "reviews": self.reviews_score,
            },
            "recommendations": self.recommendations,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "bonuses": {
                "superhost": self.superhost_bonus,
                "instant_book": self.instant_book_bonus,
            },
            "market_comparison": {
                "percentile": self.market_percentile,
                "competitor_avg": self.competitor_avg_score,
                "competitors_analyzed": self.competitors_analyzed,
            } if self.competitor_avg_score else None,
            "graded_at": self.graded_at,
        }


# Score thresholds for grades
GRADE_THRESHOLDS = {
    95: "A+",
    90: "A",
    85: "A-",
    80: "B+",
    75: "B",
    70: "B-",
    65: "C+",
    60: "C",
    55: "C-",
    50: "D+",
    45: "D",
    40: "D-",
    0: "F",
}


def score_to_grade(score: int) -> str:
    """Convert numeric score to letter grade"""
    for threshold, grade in sorted(GRADE_THRESHOLDS.items(), reverse=True):
        if score >= threshold:
            return grade
    return "F"
