"""
Shared data models for HostTools services
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ListingInput(BaseModel):
    """Input for listing analysis"""
    url: str = Field(..., description="Airbnb listing URL")
    
    @property
    def listing_id(self) -> str:
        """Extract listing ID from URL"""
        import re
        match = re.search(r'/rooms/(\d+)', self.url)
        return match.group(1) if match else ""


class ListingScore(BaseModel):
    """Listing score result"""
    listing_id: str
    overall_score: int = Field(..., ge=0, le=100)
    
    # Category scores
    title_score: int = Field(..., ge=0, le=100)
    description_score: int = Field(..., ge=0, le=100)
    photos_score: int = Field(..., ge=0, le=100)
    pricing_score: int = Field(..., ge=0, le=100)
    amenities_score: int = Field(..., ge=0, le=100)
    reviews_score: int = Field(..., ge=0, le=100)
    
    # Details
    recommendations: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    
    # Comparison
    market_percentile: int = Field(0, ge=0, le=100)
    competitor_avg_score: Optional[int] = None
    
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class Competitor(BaseModel):
    """Competitor listing"""
    listing_id: str
    name: str
    url: str
    price_per_night: float
    rating: float
    reviews_count: int
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class CompetitorAlert(BaseModel):
    """Alert when competitor changes"""
    competitor_id: str
    change_type: str  # price_drop, price_increase, availability
    old_value: Any
    new_value: Any
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewAnalysis(BaseModel):
    """Review sentiment analysis"""
    listing_id: str
    total_reviews: int
    average_sentiment: float = Field(..., ge=-1, le=1)
    themes: Dict[str, float] = Field(default_factory=dict)
    issues: List[str] = Field(default_factory=list)
    highlights: List[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class CalendarGap(BaseModel):
    """Orphan night / gap in calendar"""
    listing_id: str
    start_date: datetime
    end_date: datetime
    nights: int
    potential_revenue_loss: float
    recommendation: str
