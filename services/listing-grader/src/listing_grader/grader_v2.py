"""
Listing Grader v2 - Airbnb Algorithm Aligned
Uses scorer_v2 with 2025 ranking factors
"""

import asyncio
import logging
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

from airbnb_scraper import AirbnbScraper, ListingDetails

from .scorer_v2 import (
    ListingData,
    calculate_airbnb_score,
    score_to_grade,
    ALGORITHM_WEIGHTS,
)

logger = logging.getLogger(__name__)


@dataclass
class GradeResultV2:
    """Complete grading result - Airbnb Algorithm Aligned"""
    listing_id: str
    listing_url: str
    listing_name: str
    
    # Overall
    overall_score: int
    grade: str
    
    # Category scores (Airbnb algorithm weights)
    reviews_score: int
    response_score: int
    pricing_score: int
    conversion_score: int
    instant_book_score: int
    cancellation_score: int
    listing_quality_score: int
    availability_score: int
    
    # Category weights for reference
    category_weights: Dict[str, str] = field(default_factory=dict)
    
    # Badges
    is_superhost: bool = False
    is_guest_favorite: bool = False
    guest_favorites_eligible: bool = False
    
    # Bonuses applied
    superhost_bonus: int = 0
    guest_favorites_bonus: int = 0
    
    # Key metrics
    rating: float = 0
    reviews_count: int = 0
    response_rate: int = 0
    response_time_hours: float = 0
    instant_bookable: bool = False
    cancellation_rate: float = 0
    
    # Recommendations (priority sorted)
    recommendations: List[str] = field(default_factory=list)
    
    # Market comparison
    market_percentile: int = 50
    competitors_analyzed: int = 0
    market_avg_price: float = 0
    
    # Metadata
    graded_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    algorithm_version: str = "v2-airbnb-2025"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "listing_id": self.listing_id,
            "listing_url": self.listing_url,
            "listing_name": self.listing_name,
            "overall_score": self.overall_score,
            "grade": self.grade,
            "category_scores": {
                "reviews": {"score": self.reviews_score, "weight": "25%"},
                "response": {"score": self.response_score, "weight": "15%"},
                "pricing": {"score": self.pricing_score, "weight": "15%"},
                "conversion": {"score": self.conversion_score, "weight": "12%"},
                "instant_book": {"score": self.instant_book_score, "weight": "10%"},
                "cancellation": {"score": self.cancellation_score, "weight": "8%"},
                "listing_quality": {"score": self.listing_quality_score, "weight": "8%"},
                "availability": {"score": self.availability_score, "weight": "7%"},
            },
            "badges": {
                "superhost": self.is_superhost,
                "guest_favorite": self.is_guest_favorite,
                "guest_favorites_eligible": self.guest_favorites_eligible,
            },
            "bonuses": {
                "superhost": self.superhost_bonus,
                "guest_favorites": self.guest_favorites_bonus,
            },
            "key_metrics": {
                "rating": self.rating,
                "reviews_count": self.reviews_count,
                "response_rate": self.response_rate,
                "response_time_hours": self.response_time_hours,
                "instant_bookable": self.instant_bookable,
                "cancellation_rate": self.cancellation_rate,
            },
            "recommendations": self.recommendations,
            "market_comparison": {
                "percentile": self.market_percentile,
                "competitors_analyzed": self.competitors_analyzed,
                "market_avg_price": self.market_avg_price,
            } if self.competitors_analyzed > 0 else None,
            "graded_at": self.graded_at,
            "algorithm_version": self.algorithm_version,
        }


class ListingGraderV2:
    """
    Airbnb Listing Grader v2 - Algorithm Aligned
    
    Scores listings based on Airbnb's 2025 ranking factors:
    - Reviews / Guest Favorites (25%)
    - Response Rate & Time (15%)
    - Pricing Competitiveness (15%)
    - Conversion Signals (12%)
    - Instant Book (10%)
    - Cancellation Rate (8%)
    - Listing Quality (8%)
    - Calendar Availability (7%)
    
    Example:
        grader = ListingGraderV2()
        result = await grader.grade("https://www.airbnb.com/rooms/12345678")
        print(f"Visibility Score: {result.overall_score}/100")
        print(f"Guest Favorites Eligible: {result.guest_favorites_eligible}")
    """
    
    def __init__(
        self,
        currency: str = "EUR",
        locale: str = "en",
    ):
        self.currency = currency
        self.locale = locale
        self._scraper: Optional[AirbnbScraper] = None
    
    async def _get_scraper(self) -> AirbnbScraper:
        """Get or create scraper instance"""
        if self._scraper is None:
            self._scraper = AirbnbScraper(
                currency=self.currency,
                locale=self.locale,
            )
        return self._scraper
    
    async def close(self):
        """Close scraper connection"""
        if self._scraper:
            await self._scraper.close()
            self._scraper = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    def _extract_listing_id(self, url_or_id: str) -> str:
        """Extract listing ID from URL or return as-is"""
        if url_or_id.isdigit():
            return url_or_id
        
        patterns = [
            r'/rooms/(\d+)',
            r'airbnb\.[^/]+/rooms/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        
        raise ValueError(f"Invalid Airbnb URL or ID: {url_or_id}")
    
    def _convert_to_listing_data(
        self,
        details: ListingDetails,
        host_stats: Optional[Dict] = None,
    ) -> ListingData:
        """
        Convert scraper output to ListingData for scoring.
        Extracts all Airbnb algorithm-relevant fields.
        """
        # Default host stats if not provided
        host_stats = host_stats or {}
        
        return ListingData(
            listing_id=details.airbnb_id,
            name=details.name,
            description=details.description,
            url=details.url,
            
            # Pricing
            price_per_night=details.price_per_night,
            cleaning_fee=details.cleaning_fee or 0,
            service_fee=details.service_fee or 0,
            total_price=details.total_price or details.price_per_night,
            currency=details.currency,
            
            # Property
            property_type=details.property_type,
            room_type=details.room_type,
            bedrooms=details.bedrooms,
            beds=details.beds,
            bathrooms=details.bathrooms,
            max_guests=details.max_guests,
            
            # Location
            city=details.city,
            neighborhood=getattr(details, 'neighborhood', ''),
            latitude=details.latitude,
            longitude=details.longitude,
            
            # Reviews - CRITICAL
            rating=details.rating,
            reviews_count=details.reviews_count,
            
            # Sub-ratings (if available from scraper)
            rating_cleanliness=getattr(details, 'rating_cleanliness', 0),
            rating_accuracy=getattr(details, 'rating_accuracy', 0),
            rating_checkin=getattr(details, 'rating_checkin', 0),
            rating_communication=getattr(details, 'rating_communication', 0),
            rating_location=getattr(details, 'rating_location', 0),
            rating_value=getattr(details, 'rating_value', 0),
            
            # Host metrics
            host_id=details.host_id,
            host_name=details.host_name,
            is_superhost=details.host_is_superhost,
            is_guest_favorite=getattr(details, 'is_guest_favorite', False),
            
            # Response metrics (from host stats or defaults)
            response_rate=host_stats.get('response_rate', 100),
            response_time_hours=host_stats.get('response_time_hours', 1),
            acceptance_rate=host_stats.get('acceptance_rate', 100),
            
            # Booking settings
            instant_bookable=getattr(details, 'instant_bookable', False),
            cancellation_rate=host_stats.get('cancellation_rate', 0),
            
            # Calendar
            calendar_updated=True,  # Assume updated
            availability_days_30=host_stats.get('availability_30', 20),
            availability_days_90=host_stats.get('availability_90', 60),
            min_nights=getattr(details, 'min_nights', 1),
            max_nights=getattr(details, 'max_nights', 365),
            
            # Content
            is_new=getattr(details, 'is_new', False),
            images=details.images,
            amenities=details.amenities,
            
            # Engagement
            wishlist_count=getattr(details, 'wishlist_count', 0),
            
            scraped_at=details.scraped_at,
        )
    
    async def grade(
        self,
        url_or_id: str,
        compare_market: bool = False,
        market_radius_km: float = 5,
        checkin: Optional[str] = None,
        checkout: Optional[str] = None,
    ) -> GradeResultV2:
        """
        Grade a single listing using Airbnb's 2025 algorithm factors.
        
        Args:
            url_or_id: Airbnb listing URL or ID
            compare_market: Enable market comparison for pricing score
            market_radius_km: Radius for market comparison
            checkin: Check-in date (YYYY-MM-DD)
            checkout: Check-out date (YYYY-MM-DD)
        
        Returns:
            GradeResultV2 with visibility score and recommendations
        """
        listing_id = self._extract_listing_id(url_or_id)
        scraper = await self._get_scraper()
        
        # Fetch listing details
        details = await scraper.get_listing_details(
            listing_id,
            checkin=checkin,
            checkout=checkout,
        )
        
        if not details:
            raise ValueError(f"Could not fetch listing: {listing_id}")
        
        # Try to get host stats (response rate, etc.)
        host_stats = await self._get_host_stats(scraper, details)
        
        # Convert to ListingData
        listing = self._convert_to_listing_data(details, host_stats)
        
        # Market comparison (optional)
        market_avg = 0
        competitors_analyzed = 0
        
        if compare_market and listing.latitude and listing.longitude:
            try:
                market_avg, competitors_analyzed = await self._analyze_market(
                    scraper, listing, market_radius_km
                )
            except Exception as e:
                logger.warning(f"Market comparison failed: {e}")
        
        # Calculate Airbnb-aligned score
        result = calculate_airbnb_score(listing, market_avg=market_avg)
        
        # Build GradeResultV2
        return GradeResultV2(
            listing_id=listing.listing_id,
            listing_url=listing.url or f"https://www.airbnb.com/rooms/{listing.listing_id}",
            listing_name=listing.name,
            
            overall_score=result["overall_score"],
            grade=result["grade"],
            
            # Category scores
            reviews_score=result["category_scores"]["reviews"]["score"],
            response_score=result["category_scores"]["response"]["score"],
            pricing_score=result["category_scores"]["pricing"]["score"],
            conversion_score=result["category_scores"]["conversion"]["score"],
            instant_book_score=result["category_scores"]["instant_book"]["score"],
            cancellation_score=result["category_scores"]["cancellation"]["score"],
            listing_quality_score=result["category_scores"]["listing_quality"]["score"],
            availability_score=result["category_scores"]["availability"]["score"],
            
            category_weights={k: f"{int(v*100)}%" for k, v in ALGORITHM_WEIGHTS.items()},
            
            # Badges
            is_superhost=listing.is_superhost,
            is_guest_favorite=listing.is_guest_favorite,
            guest_favorites_eligible=result.get("guest_favorites_eligible", False),
            
            # Bonuses
            superhost_bonus=result["bonuses"]["superhost"],
            guest_favorites_bonus=result["bonuses"]["guest_favorites"],
            
            # Key metrics
            rating=listing.rating,
            reviews_count=listing.reviews_count,
            response_rate=listing.response_rate,
            response_time_hours=listing.response_time_hours,
            instant_bookable=listing.instant_bookable,
            cancellation_rate=listing.cancellation_rate,
            
            # Recommendations
            recommendations=result["recommendations"],
            
            # Market
            competitors_analyzed=competitors_analyzed,
            market_avg_price=market_avg,
        )
    
    async def _get_host_stats(
        self,
        scraper: AirbnbScraper,
        details: ListingDetails,
    ) -> Dict[str, Any]:
        """
        Try to extract host stats (response rate, cancellation rate).
        These are critical for Airbnb ranking but not always available.
        """
        stats = {
            "response_rate": 100,
            "response_time_hours": 1,
            "acceptance_rate": 100,
            "cancellation_rate": 0,
            "availability_30": 20,
            "availability_90": 60,
        }
        
        # If scraper has host profile method, use it
        if hasattr(scraper, 'get_host_profile'):
            try:
                host = await scraper.get_host_profile(details.host_id)
                if host:
                    stats["response_rate"] = getattr(host, 'response_rate', 100)
                    stats["response_time_hours"] = getattr(host, 'response_time_hours', 1)
                    stats["acceptance_rate"] = getattr(host, 'acceptance_rate', 100)
            except:
                pass
        
        # Superhost implies good stats
        if details.host_is_superhost:
            stats["response_rate"] = max(stats["response_rate"], 90)
            stats["response_time_hours"] = min(stats["response_time_hours"], 1)
            stats["cancellation_rate"] = 0
        
        return stats
    
    async def _analyze_market(
        self,
        scraper: AirbnbScraper,
        listing: ListingData,
        radius_km: float,
    ) -> tuple:
        """Analyze market for pricing comparison"""
        # Convert km to approximate lat/lng delta
        delta = radius_km / 111  # ~111km per degree
        
        competitors = await scraper.search_by_bounds(
            ne_lat=listing.latitude + delta,
            ne_lng=listing.longitude + delta,
            sw_lat=listing.latitude - delta,
            sw_lng=listing.longitude - delta,
            max_listings=30,
        )
        
        if not competitors:
            return 0, 0
        
        # Filter similar properties
        similar = [
            c for c in competitors
            if c.price_per_night > 0
            and c.airbnb_id != listing.listing_id
        ]
        
        if not similar:
            return 0, 0
        
        prices = [c.price_per_night for c in similar]
        market_avg = sum(prices) / len(prices)
        
        return market_avg, len(similar)
    
    async def grade_batch(
        self,
        urls_or_ids: List[str],
        compare_market: bool = False,
        max_concurrent: int = 3,
    ) -> List[GradeResultV2]:
        """Grade multiple listings concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def grade_one(url_or_id: str) -> Optional[GradeResultV2]:
            async with semaphore:
                try:
                    return await self.grade(url_or_id, compare_market=compare_market)
                except Exception as e:
                    logger.error(f"Failed to grade {url_or_id}: {e}")
                    return None
        
        tasks = [grade_one(u) for u in urls_or_ids]
        results = await asyncio.gather(*tasks)
        
        return [r for r in results if r is not None]
    
    def grade_sync(
        self,
        url_or_id: str,
        compare_market: bool = False,
    ) -> GradeResultV2:
        """Synchronous wrapper for grade()"""
        return asyncio.run(self.grade(url_or_id, compare_market=compare_market))


# Alias for backward compatibility
ListingGrader = ListingGraderV2
