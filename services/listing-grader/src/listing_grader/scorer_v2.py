"""
Airbnb Algorithm-Aligned Scoring System v2
Based on Airbnb's 2025 ranking factors

REAL AIRBNB RANKING FACTORS (2025):
1. Guest Favorites / Reviews (~25%) - Rating 4.9+, 6 sub-categories
2. Response Rate & Time (~15%) - <1h ideal, 90%+ rate
3. Pricing Competitiveness (~15%) - vs local market
4. Booking Conversion (~12%) - Click-to-book rate  
5. Instant Book (~10%) - Instant booking enabled
6. Cancellation Rate (~8%) - <1% host cancellations
7. Listing Quality (~8%) - Photos, description, amenities
8. Calendar Availability (~7%) - Extended availability

Guest Favorites Sub-Categories (each weighted equally):
- Cleanliness, Accuracy, Check-in, Communication, Location, Value
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass, field


# ============================================
# AIRBNB ALGORITHM WEIGHTS (2025)
# ============================================

ALGORITHM_WEIGHTS = {
    "reviews": 0.25,        # Guest Favorites / Reviews - HIGHEST
    "response": 0.15,       # Response Rate & Time
    "pricing": 0.15,        # Pricing Competitiveness
    "conversion": 0.12,     # Booking Conversion (estimated from listing quality)
    "instant_book": 0.10,   # Instant Book enabled
    "cancellation": 0.08,   # Cancellation Rate
    "listing_quality": 0.08, # Photos, description, amenities
    "availability": 0.07,   # Calendar Availability
}


# ============================================
# AMENITIES LISTS
# ============================================

ESSENTIAL_AMENITIES = [
    "wifi", "kitchen", "air conditioning", "heating", "washer", "dryer",
    "free parking", "tv", "hot water", "essentials", "bed linens",
]

PREMIUM_AMENITIES = [
    "pool", "hot tub", "gym", "ev charger", "dedicated workspace",
    "self check-in", "patio", "balcony", "bbq", "fireplace",
]

SAFETY_AMENITIES = [
    "smoke detector", "carbon monoxide detector", "fire extinguisher", 
    "first aid kit", "lock on bedroom door",
]

TITLE_KEYWORDS = [
    "cozy", "modern", "spacious", "luxury", "charming", "stunning",
    "private", "quiet", "central", "beach", "mountain", "view",
    "downtown", "historic", "garden", "terrace", "pool",
]


# ============================================
# DATA MODELS
# ============================================

@dataclass
class ListingData:
    """Listing data for scoring"""
    listing_id: str
    name: str = ""
    description: str = ""
    url: str = ""
    
    # Pricing
    price_per_night: float = 0
    cleaning_fee: float = 0
    service_fee: float = 0
    total_price: float = 0
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
    
    # Reviews - CRITICAL for Airbnb ranking
    rating: float = 0
    reviews_count: int = 0
    
    # 6 Sub-category ratings (Guest Favorites criteria)
    rating_cleanliness: float = 0
    rating_accuracy: float = 0
    rating_checkin: float = 0
    rating_communication: float = 0
    rating_location: float = 0
    rating_value: float = 0
    
    # Recent reviews
    reviews_last_year: int = 0
    recent_rating: float = 0
    
    # Host metrics
    host_id: str = ""
    host_name: str = ""
    is_superhost: bool = False
    is_guest_favorite: bool = False
    guest_favorite_percentile: int = 0
    
    # Response metrics - HIGH IMPACT
    response_rate: int = 100
    response_time_hours: float = 1
    acceptance_rate: int = 100
    
    # Booking settings - HIGH IMPACT
    instant_bookable: bool = False
    cancellation_rate: float = 0
    
    # Calendar
    calendar_updated: bool = True
    availability_days_30: int = 30
    availability_days_90: int = 90
    min_nights: int = 1
    max_nights: int = 365
    
    # Listing quality
    is_new: bool = False
    images: List[str] = field(default_factory=list)
    amenities: List[str] = field(default_factory=list)
    amenity_ids: List[int] = field(default_factory=list)
    
    # Engagement
    wishlist_count: int = 0
    views_last_30_days: int = 0
    booking_rate: float = 0
    
    scraped_at: str = ""


@dataclass 
class CategoryScore:
    """Score for a single category"""
    score: int
    weight: float
    details: str = ""
    recommendations: List[str] = field(default_factory=list)
    priority: str = "medium"


# ============================================
# 1. REVIEWS SCORING (25%)
# ============================================

def score_reviews(listing: ListingData) -> CategoryScore:
    """Score reviews - THE MOST IMPORTANT FACTOR"""
    score = 0
    recommendations = []
    priority = "critical"
    
    rating = listing.rating
    count = listing.reviews_count
    
    # Overall Rating (40 points)
    if rating >= 4.95:
        score += 40
    elif rating >= 4.9:
        score += 38
    elif rating >= 4.85:
        score += 35
    elif rating >= 4.8:
        score += 32
    elif rating >= 4.7:
        score += 28
    elif rating >= 4.5:
        score += 20
        recommendations.append("🔴 CRITICAL: Rating below 4.8 hurts visibility significantly")
    elif rating >= 4.0:
        score += 10
        recommendations.append("🔴 URGENT: Rating below 4.5 severely limits search ranking")
    elif rating > 0:
        score += 5
        recommendations.append("🔴 EMERGENCY: Low rating is killing your visibility")
    else:
        recommendations.append("No reviews yet - focus on getting first 5 reviews ASAP")
    
    # Review Count (30 points)
    if count >= 100:
        score += 30
    elif count >= 50:
        score += 25
    elif count >= 20:
        score += 20
    elif count >= 10:
        score += 15
    elif count >= 5:
        score += 10
        recommendations.append("Aim for 10+ reviews for better ranking")
    elif count >= 3:
        score += 5
        recommendations.append("Need at least 5 reviews for Guest Favorites eligibility")
    elif count > 0:
        score += 2
        recommendations.append("Focus on getting your first 5 reviews - offer discounts")
    else:
        recommendations.append("🔴 No reviews = invisible in search. Priority #1!")
    
    # Sub-category ratings (30 points)
    sub_scores = []
    sub_categories = [
        ("cleanliness", listing.rating_cleanliness, "Cleanliness"),
        ("accuracy", listing.rating_accuracy, "Accuracy"),
        ("checkin", listing.rating_checkin, "Check-in"),
        ("communication", listing.rating_communication, "Communication"),
        ("location", listing.rating_location, "Location"),
        ("value", listing.rating_value, "Value"),
    ]
    
    for key, sub_rating, name in sub_categories:
        if sub_rating >= 4.9:
            sub_scores.append(5)
        elif sub_rating >= 4.8:
            sub_scores.append(4)
        elif sub_rating >= 4.5:
            sub_scores.append(3)
        elif sub_rating > 0:
            sub_scores.append(1)
            if sub_rating < 4.5:
                recommendations.append(f"Improve {name} rating ({sub_rating}) - impacts ranking")
    
    if sub_scores:
        score += sum(sub_scores)
    else:
        if rating >= 4.9:
            score += 25
        elif rating >= 4.8:
            score += 20
        elif rating >= 4.5:
            score += 15
        elif rating > 0:
            score += 10
    
    # Guest Favorites status
    if listing.is_guest_favorite:
        score += 10
        if listing.guest_favorite_percentile == 1:
            score += 5
    
    # Recent reviews bonus
    if listing.reviews_last_year >= 10:
        score += 5
    elif listing.reviews_last_year >= 5:
        score += 3
    elif listing.reviews_last_year == 0 and count > 5:
        recommendations.append("No recent reviews - algorithm favors recent activity")
    
    # New listing
    if listing.is_new and count < 5:
        score += 10
        recommendations.append("New listing: Focus on excellent first 5 reviews")
    
    return CategoryScore(
        score=min(100, score),
        weight=ALGORITHM_WEIGHTS["reviews"],
        details=f"Rating: {rating}★, Reviews: {count}, Guest Favorite: {'Yes' if listing.is_guest_favorite else 'No'}",
        recommendations=recommendations,
        priority=priority,
    )


# ============================================
# 2. RESPONSE RATE & TIME (15%)
# ============================================

def score_response(listing: ListingData) -> CategoryScore:
    """Score response metrics"""
    score = 50
    recommendations = []
    priority = "high"
    
    response_rate = listing.response_rate
    response_time = listing.response_time_hours
    acceptance_rate = listing.acceptance_rate
    
    # Response Rate (40 points)
    if response_rate >= 98:
        score += 40
    elif response_rate >= 95:
        score += 35
    elif response_rate >= 90:
        score += 30
    elif response_rate >= 80:
        score += 20
        recommendations.append("🟡 Response rate below 90% - hurts Superhost status")
    elif response_rate >= 70:
        score += 10
        recommendations.append("🔴 Response rate below 80% - significantly hurts ranking")
    else:
        recommendations.append("🔴 CRITICAL: Low response rate severely impacts visibility")
    
    # Response Time (40 points)
    if response_time <= 0.5:
        score += 40
    elif response_time <= 1:
        score += 35
    elif response_time <= 2:
        score += 30
    elif response_time <= 6:
        score += 20
    elif response_time <= 12:
        score += 10
        recommendations.append("🟡 Respond within 1 hour for best ranking")
    elif response_time <= 24:
        score += 5
        recommendations.append("🔴 Response time over 12h hurts ranking")
    else:
        recommendations.append("🔴 CRITICAL: Response time over 24h tanks your visibility")
    
    # Acceptance Rate (20 points)
    if acceptance_rate >= 95:
        score += 10
    elif acceptance_rate >= 90:
        score += 8
    elif acceptance_rate >= 80:
        score += 5
    elif acceptance_rate < 70:
        recommendations.append("Low acceptance rate may hurt ranking")
    
    return CategoryScore(
        score=min(100, score),
        weight=ALGORITHM_WEIGHTS["response"],
        details=f"Response rate: {response_rate}%, Time: {response_time}h, Accept: {acceptance_rate}%",
        recommendations=recommendations,
        priority=priority,
    )


# ============================================
# 3. PRICING COMPETITIVENESS (15%)
# ============================================

def score_pricing(listing: ListingData, market_avg: float = 0) -> CategoryScore:
    """Score pricing relative to market"""
    score = 50
    recommendations = []
    priority = "high"
    
    price = listing.price_per_night
    
    if price <= 0:
        return CategoryScore(
            score=50,
            weight=ALGORITHM_WEIGHTS["pricing"],
            details="No price data",
            recommendations=["Price not available for analysis"],
            priority="medium",
        )
    
    if market_avg > 0:
        ratio = price / market_avg
        
        if 0.85 <= ratio <= 1.0:
            score = 90
            recommendations.append("✅ Great pricing - competitive for your market")
        elif 0.75 <= ratio < 0.85:
            score = 85
        elif 1.0 < ratio <= 1.10:
            score = 75
        elif 1.10 < ratio <= 1.20:
            score = 65
            recommendations.append("🟡 10-20% above market - ensure quality justifies premium")
        elif 1.20 < ratio <= 1.35:
            score = 50
            recommendations.append("🔴 20%+ above market - may reduce bookings")
        elif ratio > 1.35:
            score = 35
            recommendations.append("🔴 Significantly overpriced vs competition")
        elif ratio < 0.75:
            score = 70
            recommendations.append("🟡 Very low price - you may be leaving money on the table")
    else:
        score = 70
        recommendations.append("Enable market comparison for pricing optimization")
    
    if listing.cleaning_fee > 0:
        fee_ratio = listing.cleaning_fee / price
        if fee_ratio > 0.5:
            score -= 10
            recommendations.append("🟡 High cleaning fee ratio - guests see total price first now")
    
    if not recommendations or len(recommendations) == 1:
        recommendations.append("💡 Use Smart Pricing or dynamic pricing for best results")
    
    return CategoryScore(
        score=max(0, min(100, score)),
        weight=ALGORITHM_WEIGHTS["pricing"],
        details=f"Price: {listing.currency} {price}/night",
        recommendations=recommendations,
        priority=priority,
    )


# ============================================
# 4. BOOKING CONVERSION (12%)
# ============================================

def score_conversion(listing: ListingData) -> CategoryScore:
    """Estimate conversion potential from listing quality"""
    score = 50
    recommendations = []
    priority = "medium"
    
    # Photos
    photo_count = len(listing.images)
    if photo_count >= 20:
        score += 20
    elif photo_count >= 15:
        score += 18
    elif photo_count >= 10:
        score += 15
    elif photo_count >= 5:
        score += 10
        recommendations.append("🟡 Add more photos (15-25 optimal for conversion)")
    else:
        recommendations.append("🔴 CRITICAL: Need more photos - top factor for clicks")
    
    # Title Quality
    title = listing.name.lower()
    title_length = len(listing.name)
    
    if 40 <= title_length <= 60:
        score += 10
    elif title_length < 30:
        score -= 5
        recommendations.append("Title too short - add descriptive keywords")
    
    keywords_found = sum(1 for kw in TITLE_KEYWORDS if kw in title)
    if keywords_found >= 2:
        score += 10
    elif keywords_found == 0:
        recommendations.append("Add appealing keywords to title (cozy, modern, central)")
    
    # Description
    desc_length = len(listing.description)
    if desc_length >= 1000:
        score += 10
    elif desc_length >= 500:
        score += 5
    elif desc_length < 300:
        recommendations.append("🟡 Expand description - helps conversion")
    
    # Wishlist saves
    if listing.wishlist_count >= 50:
        score += 10
    elif listing.wishlist_count >= 20:
        score += 5
    
    return CategoryScore(
        score=min(100, score),
        weight=ALGORITHM_WEIGHTS["conversion"],
        details=f"Photos: {photo_count}, Title length: {title_length}",
        recommendations=recommendations,
        priority=priority,
    )


# ============================================
# 5. INSTANT BOOK (10%)
# ============================================

def score_instant_book(listing: ListingData) -> CategoryScore:
    """Score Instant Book setting"""
    if listing.instant_bookable:
        return CategoryScore(
            score=100,
            weight=ALGORITHM_WEIGHTS["instant_book"],
            details="Instant Book: Enabled ✅",
            recommendations=["✅ Instant Book enabled - good for ranking"],
            priority="low",
        )
    else:
        return CategoryScore(
            score=30,
            weight=ALGORITHM_WEIGHTS["instant_book"],
            details="Instant Book: Disabled ❌",
            recommendations=[
                "🔴 Enable Instant Book for +10-15% ranking boost",
                "Instant Book listings get more visibility and bookings"
            ],
            priority="high",
        )


# ============================================
# 6. CANCELLATION RATE (8%)
# ============================================

def score_cancellation(listing: ListingData) -> CategoryScore:
    """Score cancellation rate"""
    rate = listing.cancellation_rate
    
    if rate == 0:
        return CategoryScore(
            score=100,
            weight=ALGORITHM_WEIGHTS["cancellation"],
            details="Cancellation rate: 0% ✅",
            recommendations=["✅ Perfect cancellation record"],
            priority="low",
        )
    elif rate < 1:
        return CategoryScore(
            score=90,
            weight=ALGORITHM_WEIGHTS["cancellation"],
            details=f"Cancellation rate: {rate}%",
            recommendations=["Keep cancellation rate under 1% for Guest Favorites"],
            priority="medium",
        )
    elif rate < 3:
        return CategoryScore(
            score=60,
            weight=ALGORITHM_WEIGHTS["cancellation"],
            details=f"Cancellation rate: {rate}%",
            recommendations=["🟡 Cancellation rate above 1% may block Guest Favorites badge"],
            priority="high",
        )
    else:
        return CategoryScore(
            score=30,
            weight=ALGORITHM_WEIGHTS["cancellation"],
            details=f"Cancellation rate: {rate}%",
            recommendations=["🔴 High cancellation rate severely hurts ranking and badges"],
            priority="critical",
        )


# ============================================
# 7. LISTING QUALITY (8%)
# ============================================

def score_listing_quality(listing: ListingData) -> CategoryScore:
    """Score listing completeness and quality"""
    score = 30
    recommendations = []
    priority = "medium"
    
    # Photos (35 points)
    photo_count = len(listing.images)
    if photo_count >= 25:
        score += 35
    elif photo_count >= 20:
        score += 30
    elif photo_count >= 15:
        score += 25
    elif photo_count >= 10:
        score += 20
        recommendations.append("Add more photos (20+ recommended)")
    elif photo_count >= 5:
        score += 10
        recommendations.append("🟡 Need more photos (15+ for good ranking)")
    else:
        recommendations.append("🔴 CRITICAL: Add at least 10 quality photos")
    
    # Description (20 points)
    desc = listing.description.lower()
    desc_length = len(listing.description)
    
    if desc_length >= 1200:
        score += 15
    elif desc_length >= 800:
        score += 12
    elif desc_length >= 500:
        score += 8
    elif desc_length >= 200:
        score += 4
    else:
        recommendations.append("🔴 Description too short - add details")
    
    # Topics
    topics_found = 0
    if any(w in desc for w in ["neighborhood", "area", "located", "walk"]):
        topics_found += 1
    if any(w in desc for w in ["metro", "bus", "parking", "airport", "station"]):
        topics_found += 1
    if any(w in desc for w in ["kitchen", "wifi", "amenities", "bedroom"]):
        topics_found += 1
    if any(w in desc for w in ["check-in", "checkout", "rules", "quiet"]):
        topics_found += 1
    
    if topics_found >= 3:
        score += 5
    elif topics_found < 2:
        recommendations.append("Add info about: neighborhood, transport, amenities, house rules")
    
    # Amenities (35 points)
    amenities = [a.lower() for a in listing.amenities]
    amenity_count = len(amenities)
    
    if amenity_count >= 20:
        score += 25
    elif amenity_count >= 15:
        score += 22
    elif amenity_count >= 10:
        score += 18
    elif amenity_count >= 8:
        score += 15
    elif amenity_count >= 5:
        score += 10
    else:
        recommendations.append("🔴 Add more amenities (8-9 minimum for ranking)")
    
    # Essential amenities
    essential_found = sum(1 for a in ESSENTIAL_AMENITIES if any(a in am for am in amenities))
    if essential_found < 5:
        missing = [a for a in ESSENTIAL_AMENITIES[:6] if not any(a in am for am in amenities)]
        if missing:
            recommendations.append(f"Add essential amenities: {', '.join(missing[:3])}")
    
    # Safety
    safety_found = sum(1 for a in SAFETY_AMENITIES if any(a in am for am in amenities))
    if safety_found < 2:
        recommendations.append("Add safety amenities (smoke detector, CO detector)")
    
    return CategoryScore(
        score=min(100, score),
        weight=ALGORITHM_WEIGHTS["listing_quality"],
        details=f"Photos: {photo_count}, Amenities: {amenity_count}, Desc: {desc_length} chars",
        recommendations=recommendations,
        priority=priority,
    )


# ============================================
# 8. CALENDAR AVAILABILITY (7%)
# ============================================

def score_availability(listing: ListingData) -> CategoryScore:
    """Score calendar availability"""
    score = 50
    recommendations = []
    priority = "low"
    
    if listing.calendar_updated:
        score += 20
    else:
        score -= 20
        recommendations.append("🔴 Update your calendar - stale calendars hurt ranking")
    
    avail_30 = listing.availability_days_30
    if avail_30 >= 25:
        score += 15
    elif avail_30 >= 15:
        score += 10
    elif avail_30 >= 7:
        score += 5
    else:
        recommendations.append("Open more dates in the next 30 days")
    
    avail_90 = listing.availability_days_90
    if avail_90 >= 60:
        score += 15
    elif avail_90 >= 30:
        score += 10
    
    min_nights = listing.min_nights
    if min_nights == 1:
        score += 10
    elif min_nights == 2:
        score += 8
    elif min_nights <= 3:
        score += 5
    elif min_nights > 7:
        recommendations.append("🟡 High minimum nights limits search visibility")
    
    return CategoryScore(
        score=min(100, score),
        weight=ALGORITHM_WEIGHTS["availability"],
        details=f"Available: {avail_30}/30 days, Min nights: {min_nights}",
        recommendations=recommendations,
        priority=priority,
    )


# ============================================
# AGGREGATE SCORING
# ============================================

def calculate_airbnb_score(listing: ListingData, market_avg: float = 0) -> dict:
    """Calculate overall Airbnb-aligned score"""
    
    reviews = score_reviews(listing)
    response = score_response(listing)
    pricing = score_pricing(listing, market_avg=market_avg)
    conversion = score_conversion(listing)
    instant = score_instant_book(listing)
    cancellation = score_cancellation(listing)
    quality = score_listing_quality(listing)
    availability = score_availability(listing)
    
    weighted_score = (
        reviews.score * reviews.weight +
        response.score * response.weight +
        pricing.score * pricing.weight +
        conversion.score * conversion.weight +
        instant.score * instant.weight +
        cancellation.score * cancellation.weight +
        quality.score * quality.weight +
        availability.score * availability.weight
    )
    
    superhost_bonus = 5 if listing.is_superhost else 0
    
    gf_bonus = 0
    if listing.is_guest_favorite:
        gf_bonus = 8
        if listing.guest_favorite_percentile == 1:
            gf_bonus = 12
        elif listing.guest_favorite_percentile == 5:
            gf_bonus = 10
    
    total_score = min(100, int(weighted_score + superhost_bonus + gf_bonus))
    
    all_recs = []
    for cat in [reviews, response, pricing, conversion, instant, cancellation, quality, availability]:
        for rec in cat.recommendations:
            all_recs.append((cat.priority, rec))
    
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_recs.sort(key=lambda x: priority_order.get(x[0], 4))
    
    return {
        "overall_score": total_score,
        "grade": score_to_grade(total_score),
        "category_scores": {
            "reviews": {"score": reviews.score, "weight": "25%", "details": reviews.details},
            "response": {"score": response.score, "weight": "15%", "details": response.details},
            "pricing": {"score": pricing.score, "weight": "15%", "details": pricing.details},
            "conversion": {"score": conversion.score, "weight": "12%", "details": conversion.details},
            "instant_book": {"score": instant.score, "weight": "10%", "details": instant.details},
            "cancellation": {"score": cancellation.score, "weight": "8%", "details": cancellation.details},
            "listing_quality": {"score": quality.score, "weight": "8%", "details": quality.details},
            "availability": {"score": availability.score, "weight": "7%", "details": availability.details},
        },
        "bonuses": {
            "superhost": superhost_bonus,
            "guest_favorites": gf_bonus,
        },
        "recommendations": [rec for _, rec in all_recs[:10]],
        "guest_favorites_eligible": listing.rating >= 4.9 and listing.reviews_count >= 5 and listing.cancellation_rate < 1,
    }


def score_to_grade(score: int) -> str:
    """Convert score to letter grade"""
    if score >= 95: return "A+"
    if score >= 90: return "A"
    if score >= 85: return "A-"
    if score >= 80: return "B+"
    if score >= 75: return "B"
    if score >= 70: return "B-"
    if score >= 65: return "C+"
    if score >= 60: return "C"
    if score >= 55: return "C-"
    if score >= 50: return "D+"
    if score >= 45: return "D"
    if score >= 40: return "D-"
    return "F"
