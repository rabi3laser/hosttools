# Listing Grader 📊

Score your Airbnb listing 0-100 with actionable recommendations.

## Installation

```bash
pip install git+https://github.com/rabi3laser/hosttools.git#subdirectory=services/listing-grader
```

## Quick Start

```python
from listing_grader import ListingGrader

# Initialize grader
grader = ListingGrader()

# Grade a listing by URL
result = await grader.grade("https://www.airbnb.com/rooms/12345678")

print(f"Overall Score: {result.overall_score}/100")
print(f"Recommendations: {result.recommendations}")
```

## CLI Usage

```bash
# Grade a single listing
listing-grader https://www.airbnb.com/rooms/12345678

# Grade with market comparison
listing-grader https://www.airbnb.com/rooms/12345678 --compare-market

# Output as JSON
listing-grader https://www.airbnb.com/rooms/12345678 --json
```

## Scoring Algorithm

| Category | Weight | What We Analyze |
|----------|--------|-----------------|
| Title | 15% | Length, keywords, emoji usage |
| Description | 15% | Length, completeness, keywords |
| Photos | 20% | Count, quality indicators |
| Pricing | 15% | Market comparison, value |
| Amenities | 15% | Essential vs premium amenities |
| Reviews | 20% | Rating, count, recency |

### Bonus Points
- Superhost status: +5 points
- Instant Book: +3 points
- Response rate: +2 points

## API Response

```python
@dataclass
class GradeResult:
    listing_id: str
    overall_score: int          # 0-100
    
    # Category scores
    title_score: int            # 0-100
    description_score: int      # 0-100
    photos_score: int           # 0-100
    pricing_score: int          # 0-100
    amenities_score: int        # 0-100
    reviews_score: int          # 0-100
    
    # Insights
    recommendations: List[str]  # Actionable tips
    strengths: List[str]        # What's working well
    weaknesses: List[str]       # Areas to improve
    
    # Market context
    market_percentile: int      # Your rank vs competitors
    competitor_avg_score: int   # Average score in your area
```

## Examples

### Basic Grading

```python
import asyncio
from listing_grader import ListingGrader

async def main():
    grader = ListingGrader()
    
    result = await grader.grade("https://www.airbnb.com/rooms/12345678")
    
    print(f"🏠 {result.listing_id}")
    print(f"📊 Overall: {result.overall_score}/100")
    print(f"📝 Title: {result.title_score}/100")
    print(f"📸 Photos: {result.photos_score}/100")
    print(f"⭐ Reviews: {result.reviews_score}/100")
    
    print("\n💡 Recommendations:")
    for rec in result.recommendations:
        print(f"  • {rec}")

asyncio.run(main())
```

### With Market Comparison

```python
async def compare_to_market():
    grader = ListingGrader()
    
    # Grade with market context
    result = await grader.grade(
        "https://www.airbnb.com/rooms/12345678",
        compare_market=True,
        market_radius_km=5
    )
    
    print(f"Your Score: {result.overall_score}/100")
    print(f"Market Average: {result.competitor_avg_score}/100")
    print(f"Your Percentile: Top {100 - result.market_percentile}%")

asyncio.run(compare_to_market())
```

### Batch Processing

```python
async def grade_multiple():
    grader = ListingGrader()
    
    urls = [
        "https://www.airbnb.com/rooms/111111",
        "https://www.airbnb.com/rooms/222222",
        "https://www.airbnb.com/rooms/333333",
    ]
    
    results = await grader.grade_batch(urls)
    
    for result in results:
        print(f"{result.listing_id}: {result.overall_score}/100")

asyncio.run(grade_multiple())
```

## Scoring Details

### Title Score (15%)
- Length: 30-60 chars optimal
- Keywords: Location, type, unique features
- Emojis: 1-2 acceptable, more penalized
- ALL CAPS: Penalized

### Description Score (15%)
- Length: 500-1500 chars optimal
- Sections: House rules, check-in, neighborhood
- Keywords: Amenities, attractions, transport

### Photos Score (20%)
- Count: 15+ photos optimal
- Cover photo quality
- Variety: Interior, exterior, amenities

### Pricing Score (15%)
- Market comparison (if enabled)
- Price-to-quality ratio
- Seasonal adjustment

### Amenities Score (15%)
- Essential: Wifi, Kitchen, AC/Heating
- Premium: Pool, Hot tub, Workspace
- Safety: Smoke detector, First aid

### Reviews Score (20%)
- Rating: 4.8+ excellent
- Count: 50+ reviews optimal
- Recency: Recent reviews weighted higher

## License

MIT
