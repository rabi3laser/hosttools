"""
Listing Grader - Main grader class
Uses airbnb-scraper package for data extraction
"""

import asyncio
import logging
import re
from typing import Optional, List
from dataclasses import asdict

from airbnb_scraper import AirbnbScraper, ListingBasic, ListingDetails

from .models import ListingData, GradeResult, score_to_grade
from .scorer import (
    score_title,
    score_description,
    score_photos,
    score_pricing,
    score_amenities,
    score_reviews,
    calculate_overall_score,
)

logger = logging.getLogger(__name__)


class ListingGrader:
    """
    Grade Airbnb listings with actionable recommendations.
    
    Uses airbnb-scraper package for data extraction.
    
    Example:
        grader = ListingGrader()
        result = await grader.grade("https://www.airbnb.com/rooms/12345678")
        print(f"Score: {result.overall_score}/100")
    """
    
    def __init__(
        self,
        currency: str = "EUR",
        locale: str = "en",
    ):
        """
        Initialize the grader.
        
        Args:
            currency: Currency for pricing (EUR, USD, etc.)
            locale: Language locale (en, fr, etc.)
        """
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
        basic: Optional[ListingBasic] = None
    ) -> ListingData:
        """Convert scraper output to ListingData"""
        return ListingData(
            listing_id=details.airbnb_id,
            name=details.name,
            description=details.description,
            url=details.url,
            price_per_night=details.price_per_night,
            cleaning_fee=details.cleaning_fee,
            service_fee=details.service_fee,
            currency=details.currency,
            property_type=details.property_type,
            room_type=details.room_type,
            bedrooms=details.bedrooms,
            beds=details.beds,
            bathrooms=details.bathrooms,
            max_guests=details.max_guests,
            city=details.city,
            neighborhood=basic.neighborhood if basic else "",
            latitude=details.latitude,
            longitude=details.longitude,
            rating=details.rating,
            reviews_count=details.reviews_count,
            host_id=details.host_id,
            host_name=details.host_name,
            is_superhost=details.host_is_superhost,
            instant_bookable=basic.instant_bookable if basic else False,
            is_new=basic.is_new if basic else False,
            images=details.images,
            amenities=details.amenities,
            amenity_ids=basic.amenity_ids if basic else [],
            scraped_at=details.scraped_at,
        )
    
    async def grade(
        self,
        url_or_id: str,
        compare_market: bool = False,
        market_radius_km: float = 5,
        checkin: Optional[str] = None,
        checkout: Optional[str] = None,
    ) -> GradeResult:
        """
        Grade a single listing.
        
        Args:
            url_or_id: Airbnb listing URL or ID
            compare_market: Enable market comparison for pricing score
            market_radius_km: Radius for market comparison
            checkin: Check-in date (YYYY-MM-DD)
            checkout: Check-out date (YYYY-MM-DD)
        
        Returns:
            GradeResult with scores and recommendations
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
        
        # Convert to ListingData
        listing = self._convert_to_listing_data(details)
        
        # Market comparison (optional)
        market_avg = 0
        competitors_analyzed = 0
        competitor_scores = []
        
        if compare_market and listing.latitude and listing.longitude:
            try:
                competitors = await scraper.search_by_bounds(
                    ne_lat=listing.latitude + 0.05,
                    ne_lng=listing.longitude + 0.05,
                    sw_lat=listing.latitude - 0.05,
                    sw_lng=listing.longitude - 0.05,
                    max_listings=30,
                )
                
                if competitors:
                    prices = [c.price_per_night for c in competitors if c.price_per_night > 0]
                    if prices:
                        market_avg = sum(prices) / len(prices)
                        competitors_analyzed = len(competitors)
                        
                        # Calculate competitor scores for percentile
                        for comp in competitors:
                            comp_listing = ListingData(
                                listing_id=comp.airbnb_id,
                                name=comp.name,
                                images=comp.images,
                                amenities=comp.amenities,
                                rating=comp.rating,
                                reviews_count=comp.reviews_count,
                                is_superhost=comp.is_superhost,
                            )
                            comp_score = self._quick_score(comp_listing)
                            competitor_scores.append(comp_score)
            except Exception as e:
                logger.warning(f"Market comparison failed: {e}")
        
        # Calculate category scores
        title_result = score_title(listing)
        desc_result = score_description(listing)
        photos_result = score_photos(listing)
        pricing_result = score_pricing(listing, market_avg=market_avg)
        amenities_result = score_amenities(listing)
        reviews_result = score_reviews(listing)
        
        # Calculate overall score
        overall, superhost_bonus, instant_bonus = calculate_overall_score(
            title=title_result,
            description=desc_result,
            photos=photos_result,
            pricing=pricing_result,
            amenities=amenities_result,
            reviews=reviews_result,
            is_superhost=listing.is_superhost,
            instant_bookable=listing.instant_bookable,
        )
        
        # Calculate market percentile
        market_percentile = 50  # Default
        competitor_avg_score = None
        if competitor_scores:
            better_than = sum(1 for s in competitor_scores if overall > s)
            market_percentile = int((better_than / len(competitor_scores)) * 100)
            competitor_avg_score = int(sum(competitor_scores) / len(competitor_scores))
        
        # Aggregate recommendations
        all_recommendations = []
        all_recommendations.extend(title_result.recommendations)
        all_recommendations.extend(desc_result.recommendations)
        all_recommendations.extend(photos_result.recommendations)
        all_recommendations.extend(pricing_result.recommendations)
        all_recommendations.extend(amenities_result.recommendations)
        all_recommendations.extend(reviews_result.recommendations)
        
        # Identify strengths (scores >= 80)
        strengths = []
        if title_result.score >= 80:
            strengths.append("Great title with good keywords")
        if photos_result.score >= 80:
            strengths.append(f"Good photo coverage ({len(listing.images)} photos)")
        if reviews_result.score >= 80:
            strengths.append(f"Strong reviews ({listing.rating}★, {listing.reviews_count} reviews)")
        if amenities_result.score >= 80:
            strengths.append("Excellent amenity coverage")
        if listing.is_superhost:
            strengths.append("Superhost status")
        
        # Identify weaknesses (scores < 60)
        weaknesses = []
        if title_result.score < 60:
            weaknesses.append("Title needs improvement")
        if desc_result.score < 60:
            weaknesses.append("Description lacks detail")
        if photos_result.score < 60:
            weaknesses.append("Need more/better photos")
        if reviews_result.score < 60:
            weaknesses.append("Reviews need attention")
        if amenities_result.score < 60:
            weaknesses.append("Missing key amenities")
        
        return GradeResult(
            listing_id=listing.listing_id,
            listing_url=listing.url,
            listing_name=listing.name,
            overall_score=overall,
            grade=score_to_grade(overall),
            title_score=title_result.score,
            description_score=desc_result.score,
            photos_score=photos_result.score,
            pricing_score=pricing_result.score,
            amenities_score=amenities_result.score,
            reviews_score=reviews_result.score,
            recommendations=all_recommendations[:10],  # Top 10
            strengths=strengths,
            weaknesses=weaknesses,
            superhost_bonus=superhost_bonus,
            instant_book_bonus=instant_bonus,
            market_percentile=market_percentile,
            competitor_avg_score=competitor_avg_score,
            competitors_analyzed=competitors_analyzed,
        )
    
    def _quick_score(self, listing: ListingData) -> int:
        """Quick score calculation for competitor comparison"""
        score = 50
        
        # Photos
        if len(listing.images) >= 15:
            score += 15
        elif len(listing.images) >= 10:
            score += 10
        
        # Reviews
        if listing.rating >= 4.8:
            score += 15
        elif listing.rating >= 4.5:
            score += 10
        
        if listing.reviews_count >= 50:
            score += 10
        elif listing.reviews_count >= 20:
            score += 5
        
        # Superhost
        if listing.is_superhost:
            score += 5
        
        return min(100, score)
    
    async def grade_batch(
        self,
        urls_or_ids: List[str],
        compare_market: bool = False,
        max_concurrent: int = 3,
    ) -> List[GradeResult]:
        """
        Grade multiple listings.
        
        Args:
            urls_or_ids: List of Airbnb URLs or IDs
            compare_market: Enable market comparison
            max_concurrent: Max concurrent requests
        
        Returns:
            List of GradeResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def grade_one(url_or_id: str) -> Optional[GradeResult]:
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
    ) -> GradeResult:
        """
        Synchronous version of grade() for simple use cases.
        
        Args:
            url_or_id: Airbnb listing URL or ID
            compare_market: Enable market comparison
        
        Returns:
            GradeResult with scores and recommendations
        """
        return asyncio.run(self.grade(url_or_id, compare_market=compare_market))
