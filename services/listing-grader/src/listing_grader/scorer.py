"""
Scoring algorithms for each listing category
"""

import re
from typing import List, Tuple
from .models import ListingData, CategoryScore


# ============================================
# ESSENTIAL AMENITIES
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

# High-value keywords for titles
TITLE_KEYWORDS = [
    "cozy", "modern", "spacious", "luxury", "charming", "stunning",
    "private", "quiet", "central", "beach", "mountain", "view",
    "downtown", "historic", "garden", "terrace", "pool",
]


# ============================================
# TITLE SCORING (15%)
# ============================================

def score_title(listing: ListingData) -> CategoryScore:
    """
    Score the listing title.
    
    Optimal: 40-60 characters
    Keywords: Location, property type, unique features
    Penalties: ALL CAPS, too many emojis, generic titles
    """
    title = listing.name
    score = 50  # Base score
    recommendations = []
    
    # Length scoring
    length = len(title)
    if 40 <= length <= 60:
        score += 20  # Perfect length
    elif 30 <= length < 40 or 60 < length <= 80:
        score += 10  # Acceptable
    elif length < 20:
        score -= 20
        recommendations.append(f"Title too short ({length} chars). Aim for 40-60 characters.")
    elif length > 100:
        score -= 15
        recommendations.append(f"Title too long ({length} chars). Keep under 80 characters.")
    
    # Keyword analysis
    title_lower = title.lower()
    keywords_found = sum(1 for kw in TITLE_KEYWORDS if kw in title_lower)
    if keywords_found >= 3:
        score += 15
    elif keywords_found >= 2:
        score += 10
    elif keywords_found >= 1:
        score += 5
    else:
        recommendations.append("Add descriptive keywords (cozy, modern, central, etc.)")
    
    # Location mention
    if listing.city and listing.city.lower() in title_lower:
        score += 5
    elif listing.neighborhood and listing.neighborhood.lower() in title_lower:
        score += 5
    else:
        recommendations.append(f"Consider adding location ({listing.city or 'your area'}) to title")
    
    # Penalties
    # ALL CAPS check
    caps_ratio = sum(1 for c in title if c.isupper()) / max(len(title), 1)
    if caps_ratio > 0.5:
        score -= 15
        recommendations.append("Avoid ALL CAPS - it looks spammy")
    
    # Emoji check
    emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF]')
    emoji_count = len(emoji_pattern.findall(title))
    if emoji_count > 3:
        score -= 10
        recommendations.append("Too many emojis. Use 1-2 max.")
    elif emoji_count == 0:
        pass  # Neutral
    
    # Generic title penalty
    generic_titles = ["apartment", "room", "house", "flat", "studio"]
    if title_lower.strip() in generic_titles:
        score -= 20
        recommendations.append("Title too generic. Add unique features.")
    
    return CategoryScore(
        score=max(0, min(100, score)),
        weight=0.15,
        details=f"Length: {length}, Keywords: {keywords_found}",
        recommendations=recommendations,
    )


# ============================================
# DESCRIPTION SCORING (15%)
# ============================================

def score_description(listing: ListingData) -> CategoryScore:
    """
    Score the listing description.
    
    Optimal: 800-1500 characters
    Should include: Amenities, neighborhood, transport, rules
    """
    desc = listing.description
    score = 50
    recommendations = []
    
    # Length scoring
    length = len(desc)
    if 800 <= length <= 1500:
        score += 25
    elif 500 <= length < 800 or 1500 < length <= 2000:
        score += 15
    elif 300 <= length < 500:
        score += 5
        recommendations.append("Description could be longer (aim for 800-1500 chars)")
    elif length < 300:
        score -= 20
        recommendations.append(f"Description too short ({length} chars). Add more details.")
    elif length > 3000:
        score -= 10
        recommendations.append("Description very long. Consider being more concise.")
    
    desc_lower = desc.lower()
    
    # Section/topic coverage
    topics = {
        "neighborhood": ["neighborhood", "area", "district", "located", "walk to", "minutes from"],
        "transport": ["metro", "subway", "bus", "station", "airport", "parking", "train"],
        "amenities": ["kitchen", "wifi", "bed", "bathroom", "towels", "equipped"],
        "rules": ["check-in", "checkout", "no smoking", "quiet", "please", "note"],
    }
    
    topics_covered = 0
    for topic, keywords in topics.items():
        if any(kw in desc_lower for kw in keywords):
            topics_covered += 1
    
    if topics_covered >= 4:
        score += 15
    elif topics_covered >= 3:
        score += 10
    elif topics_covered >= 2:
        score += 5
    else:
        missing = []
        for topic, keywords in topics.items():
            if not any(kw in desc_lower for kw in keywords):
                missing.append(topic)
        recommendations.append(f"Add info about: {', '.join(missing)}")
    
    # Formatting check (paragraphs)
    paragraphs = len([p for p in desc.split('\n\n') if p.strip()])
    if paragraphs >= 3:
        score += 5
    elif paragraphs == 1 and length > 500:
        score -= 5
        recommendations.append("Break description into paragraphs for readability")
    
    return CategoryScore(
        score=max(0, min(100, score)),
        weight=0.15,
        details=f"Length: {length}, Topics: {topics_covered}/4",
        recommendations=recommendations,
    )


# ============================================
# PHOTOS SCORING (20%)
# ============================================

def score_photos(listing: ListingData) -> CategoryScore:
    """
    Score listing photos.
    
    Optimal: 15-25 photos
    Variety: Interior, exterior, amenities, neighborhood
    """
    photos = listing.images
    count = len(photos)
    score = 50
    recommendations = []
    
    # Count scoring
    if 15 <= count <= 25:
        score += 30  # Perfect
    elif 10 <= count < 15:
        score += 20
        recommendations.append(f"Add more photos ({count} now, aim for 15+)")
    elif 25 < count <= 40:
        score += 25
    elif 5 <= count < 10:
        score += 5
        recommendations.append(f"Only {count} photos. Top listings have 15+")
    elif count < 5:
        score -= 20
        recommendations.append(f"Too few photos ({count}). Add at least 10 more.")
    elif count > 50:
        score += 15  # Good but diminishing returns
        recommendations.append("Consider removing duplicate/low-quality photos")
    
    # Quality indicators (heuristics based on URL patterns)
    if photos:
        # Check for high-res indicators
        high_res = sum(1 for p in photos if "large" in p.lower() or "xl" in p.lower() or "1200" in p)
        if high_res > count * 0.5:
            score += 10
    
    # First photo bonus (it's the cover)
    if photos:
        score += 5  # Has at least one photo
    
    # Recommendations based on count
    if count == 0:
        recommendations.append("CRITICAL: No photos! Add at least 10 quality photos.")
        score = 0
    
    return CategoryScore(
        score=max(0, min(100, score)),
        weight=0.20,
        details=f"Photo count: {count}",
        recommendations=recommendations,
    )


# ============================================
# PRICING SCORING (15%)
# ============================================

def score_pricing(
    listing: ListingData,
    market_avg: float = 0,
    market_min: float = 0,
    market_max: float = 0,
) -> CategoryScore:
    """
    Score pricing relative to market.
    
    Without market data: Score based on general heuristics
    With market data: Score based on position in market
    """
    price = listing.price_per_night
    score = 50
    recommendations = []
    
    if price <= 0:
        return CategoryScore(
            score=0,
            weight=0.15,
            details="No price data",
            recommendations=["Price not available"],
        )
    
    # If we have market comparison data
    if market_avg > 0:
        ratio = price / market_avg
        
        if 0.85 <= ratio <= 1.15:
            score = 80  # Well priced
        elif 0.7 <= ratio < 0.85:
            score = 90  # Good value
        elif ratio < 0.7:
            score = 70  # Maybe too cheap?
            recommendations.append("Price significantly below market. Consider if you're leaving money on the table.")
        elif 1.15 < ratio <= 1.3:
            score = 60
            recommendations.append("Priced above market average. Ensure quality justifies premium.")
        elif ratio > 1.3:
            score = 40
            recommendations.append(f"Price {int((ratio-1)*100)}% above market. May reduce bookings.")
    else:
        # No market data - basic scoring
        score = 70  # Neutral without comparison
        recommendations.append("Enable market comparison for pricing insights")
    
    # Bonus for having cleaning fee transparency
    if listing.cleaning_fee > 0:
        score += 5  # Transparent pricing is good
    
    return CategoryScore(
        score=max(0, min(100, score)),
        weight=0.15,
        details=f"Price: {listing.currency} {price:.0f}/night",
        recommendations=recommendations,
    )


# ============================================
# AMENITIES SCORING (15%)
# ============================================

def score_amenities(listing: ListingData) -> CategoryScore:
    """
    Score amenities coverage.
    
    Essential: Wifi, Kitchen, AC/Heating, etc.
    Premium: Pool, Hot tub, Workspace, etc.
    Safety: Smoke detector, First aid, etc.
    """
    amenities = [a.lower() for a in listing.amenities]
    score = 30  # Base
    recommendations = []
    
    # Essential amenities (each worth up to 5 points)
    essential_found = []
    essential_missing = []
    for amenity in ESSENTIAL_AMENITIES:
        if any(amenity in a for a in amenities):
            essential_found.append(amenity)
            score += 4
        else:
            essential_missing.append(amenity)
    
    # Premium amenities (bonus points)
    premium_found = []
    for amenity in PREMIUM_AMENITIES:
        if any(amenity in a for a in amenities):
            premium_found.append(amenity)
            score += 3
    
    # Safety amenities (important!)
    safety_found = []
    safety_missing = []
    for amenity in SAFETY_AMENITIES:
        if any(amenity in a for a in amenities):
            safety_found.append(amenity)
            score += 2
        else:
            safety_missing.append(amenity)
    
    # Recommendations
    if essential_missing:
        top_missing = essential_missing[:3]
        recommendations.append(f"Add essential amenities: {', '.join(top_missing)}")
    
    if safety_missing:
        recommendations.append(f"Add safety features: {', '.join(safety_missing[:2])}")
    
    if not premium_found:
        recommendations.append("Consider premium amenities (workspace, pool) to stand out")
    
    # Total amenity count bonus
    total = len(amenities)
    if total >= 30:
        score += 10
    elif total >= 20:
        score += 5
    elif total < 10:
        score -= 10
        recommendations.append(f"Only {total} amenities listed. Add more to improve visibility.")
    
    return CategoryScore(
        score=max(0, min(100, score)),
        weight=0.15,
        details=f"Total: {len(amenities)}, Essential: {len(essential_found)}, Premium: {len(premium_found)}",
        recommendations=recommendations,
    )


# ============================================
# REVIEWS SCORING (20%)
# ============================================

def score_reviews(listing: ListingData) -> CategoryScore:
    """
    Score based on reviews.
    
    Rating: 4.8+ excellent, 4.5+ good, 4.0+ acceptable
    Count: 50+ great, 20+ good, 10+ okay
    """
    rating = listing.rating
    count = listing.reviews_count
    score = 30  # Base
    recommendations = []
    
    # Rating scoring
    if rating >= 4.9:
        score += 40
    elif rating >= 4.8:
        score += 35
    elif rating >= 4.7:
        score += 30
    elif rating >= 4.5:
        score += 20
    elif rating >= 4.0:
        score += 10
    elif rating >= 3.5:
        score += 0
        recommendations.append("Rating below 4.0. Focus on guest experience improvements.")
    elif rating > 0:
        score -= 10
        recommendations.append("Low rating significantly hurts bookings. Address guest concerns.")
    
    # Count scoring
    if count >= 100:
        score += 25
    elif count >= 50:
        score += 20
    elif count >= 20:
        score += 15
    elif count >= 10:
        score += 10
    elif count >= 5:
        score += 5
        recommendations.append(f"Only {count} reviews. Encourage guests to leave reviews.")
    elif count > 0:
        score += 2
        recommendations.append("Few reviews. New listing? Focus on getting first 10 reviews.")
    else:
        score -= 10
        recommendations.append("No reviews yet. Offer discounts to get first reviews.")
    
    # New listing consideration
    if listing.is_new and count < 5:
        score += 10  # Bonus for new listings
    
    return CategoryScore(
        score=max(0, min(100, score)),
        weight=0.20,
        details=f"Rating: {rating}, Reviews: {count}",
        recommendations=recommendations,
    )


# ============================================
# AGGREGATE SCORING
# ============================================

def calculate_overall_score(
    title: CategoryScore,
    description: CategoryScore,
    photos: CategoryScore,
    pricing: CategoryScore,
    amenities: CategoryScore,
    reviews: CategoryScore,
    is_superhost: bool = False,
    instant_bookable: bool = False,
) -> Tuple[int, int, int]:
    """
    Calculate weighted overall score with bonuses.
    
    Returns: (overall_score, superhost_bonus, instant_book_bonus)
    """
    weighted_score = (
        title.score * title.weight +
        description.score * description.weight +
        photos.score * photos.weight +
        pricing.score * pricing.weight +
        amenities.score * amenities.weight +
        reviews.score * reviews.weight
    )
    
    # Bonuses
    superhost_bonus = 5 if is_superhost else 0
    instant_book_bonus = 3 if instant_bookable else 0
    
    total = weighted_score + superhost_bonus + instant_book_bonus
    
    return (
        max(0, min(100, int(total))),
        superhost_bonus,
        instant_book_bonus,
    )
