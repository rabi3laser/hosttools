# Listing Grader 📊

**Airbnb Visibility Score** - Aligned with Airbnb's 2025 ranking algorithm.

Score your listing 0-100 and get actionable recommendations to improve your search ranking.

## Installation

```bash
pip install git+https://github.com/rabi3laser/hosttools.git#subdirectory=services/listing-grader
```

## Quick Start

```python
from listing_grader import ListingGrader

grader = ListingGrader()
result = await grader.grade("https://www.airbnb.com/rooms/12345678")

print(f"Visibility Score: {result.overall_score}/100")
print(f"Guest Favorites Eligible: {result.guest_favorites_eligible}")
```

## CLI Usage

```bash
# Grade a single listing
listing-grader https://www.airbnb.com/rooms/12345678

# With market comparison
listing-grader https://www.airbnb.com/rooms/12345678 --compare-market

# Output JSON
listing-grader https://www.airbnb.com/rooms/12345678 --json
```

## 🎯 Airbnb Algorithm Alignment (2025)

Our scoring mirrors **Airbnb's actual ranking factors**:

| Factor | Weight | What Airbnb Measures |
|--------|--------|---------------------|
| **Reviews / Guest Favorites** | 25% | Rating 4.9+, 6 sub-categories |
| **Response Rate & Time** | 15% | < 1h ideal, 90%+ rate |
| **Pricing** | 15% | Competitiveness vs local market |
| **Conversion Signals** | 12% | Photos, title, description quality |
| **Instant Book** | 10% | Enabled = +10-15% ranking boost |
| **Cancellation Rate** | 8% | < 1% for Guest Favorites |
| **Listing Quality** | 8% | Amenities, completeness |
| **Calendar Availability** | 7% | Updated, open availability |

### Guest Favorites Criteria

To earn Airbnb's **Guest Favorites badge** (gold heart):

- ⭐ Overall rating ≥ **4.9**
- 📝 At least **5 reviews** in past 4 years
- ✅ Recent review in past 2 years
- 🚫 Cancellation rate < **1%**
- 📊 High scores in all 6 sub-categories:
  - Cleanliness, Accuracy, Check-in
  - Communication, Location, Value

## Example Output

```
============================================================
🏠 AIRBNB VISIBILITY SCORE - Algorithm Aligned (2025)
============================================================
📍 Stunning Modern Loft in Le Marais - Eiffel Tower Views
📍 Paris
============================================================

🏆 VISIBILITY SCORE: 92/100 (Grade: A)
   [██████████████████░░]

   🏅 GUEST FAVORITES ELIGIBLE ✓

📊 RANKING FACTORS:
   Factor               Score   Weight    Impact
   ------------------------------------------------
   Reviews              95/100     25%    23.8pts
   Response Time       100/100     15%    15.0pts
   Pricing              85/100     15%    12.8pts
   Conversion           90/100     12%    10.8pts
   Instant Book        100/100     10%    10.0pts
   Cancellations       100/100      8%     8.0pts
   Listing Quality      88/100      8%     7.0pts
   Availability         90/100      7%     6.3pts

🎁 BADGES & BONUSES:
   ✓ Superhost: +5 points
   ✓ Guest Favorites: +10 points

💡 TOP ACTIONS TO IMPROVE RANKING:
   1. Enable market comparison for pricing optimization
   2. ✅ Instant Book enabled - good for ranking
```

## API Response

```python
{
    "overall_score": 92,
    "grade": "A",
    "category_scores": {
        "reviews": {"score": 95, "weight": "25%"},
        "response": {"score": 100, "weight": "15%"},
        "pricing": {"score": 85, "weight": "15%"},
        "conversion": {"score": 90, "weight": "12%"},
        "instant_book": {"score": 100, "weight": "10%"},
        "cancellation": {"score": 100, "weight": "8%"},
        "listing_quality": {"score": 88, "weight": "8%"},
        "availability": {"score": 90, "weight": "7%"},
    },
    "bonuses": {
        "superhost": 5,
        "guest_favorites": 10
    },
    "recommendations": [
        "Enable market comparison for pricing optimization",
        "Add more photos (20+ recommended)"
    ],
    "guest_favorites_eligible": True
}
```

## Key Recommendations by Priority

### 🔴 CRITICAL (Fix immediately)
- Rating below 4.5
- No reviews
- High cancellation rate
- Response rate below 80%

### 🟡 HIGH IMPACT
- Rating below 4.8 (hurts visibility)
- Instant Book disabled
- Response time over 1 hour
- Less than 10 photos

### 📊 MEDIUM
- Missing essential amenities
- Short description
- Limited calendar availability

## Versions

### v2 (Current) - Airbnb Algorithm Aligned
- 8 ranking factors based on Airbnb 2025 algorithm
- Guest Favorites eligibility check
- Response rate/time scoring
- Cancellation rate impact
- Priority-based recommendations

### v1 (Legacy)
- 6 category scoring (title, description, photos, pricing, amenities, reviews)
- Basic weighted scoring
- Still available in `scorer.py`

## Sources

Scoring based on:
- [Airbnb Help Center - How search results work](https://www.airbnb.com/help/article/39)
- [Airbnb Resource Center - Guest Favorites](https://www.airbnb.com/resources/hosting-homes/a/understanding-guest-favorites-642)
- AirDNA research on ranking factors
- Rental Scale-Up algorithm analysis (2025)

## License

MIT
