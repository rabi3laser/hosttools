# HostTools - Microservices Suite for Airbnb Hosts

A collection of independent, revenue-generating microservices designed to help Airbnb hosts optimize their listings, monitor competition, and maximize revenue.

## 🚀 Quick Start - Listing Grader

```bash
# Install
pip install git+https://github.com/rabi3laser/hosttools.git#subdirectory=services/listing-grader

# Grade a listing
listing-grader https://www.airbnb.com/rooms/12345678

# Or use in Python
from listing_grader import ListingGrader

grader = ListingGrader()
result = await grader.grade("https://www.airbnb.com/rooms/12345678")
print(f"Score: {result.overall_score}/100")
```

## Vision

In 2025, Airbnb market saturation means hosts must differentiate or die. HostTools provides the competitive edge:

- **42%** of hosts feel disadvantaged by Airbnb's algorithm
- **31%** cite algorithmic unpredictability as top stressor
- Average host loses **$2,000+/year** to suboptimal pricing

## Microservices

| Service | Status | Description | Install |
|---------|--------|-------------|---------|
| **[Listing Grader](services/listing-grader)** | ✅ Ready | Score your listing 0-100 | `pip install git+...#subdirectory=services/listing-grader` |
| **CompSet Spy** | 📋 Planned | Monitor competitors' prices | Coming soon |
| **Price Alert** | 📋 Planned | Market price notifications | Coming soon |
| **Event Radar** | 📋 Planned | Detect local events | Coming soon |
| **Review Analyzer** | 📋 Planned | Sentiment analysis | Coming soon |
| **Gap Filler** | 📋 Planned | Optimize orphan nights | Coming soon |

## Listing Grader Features

### Scoring Algorithm

| Category | Weight | What We Analyze |
|----------|--------|-----------------|
| Title | 15% | Length, keywords, emoji usage |
| Description | 15% | Length, completeness, topics covered |
| Photos | 20% | Count, quality indicators |
| Pricing | 15% | Market comparison |
| Amenities | 15% | Essential, premium, safety |
| Reviews | 20% | Rating, count |

### Bonuses
- Superhost: +5 points
- Instant Book: +3 points

### Example Output

```
============================================================
🏠 LISTING GRADE REPORT
============================================================
📍 Cozy Modern Apartment in Central Paris
🔗 https://www.airbnb.com/rooms/123456
============================================================

🏆 OVERALL SCORE: 87/100 (Grade: A-)
   [█████████████████░░░]

📊 CATEGORY SCORES:
   Title:          85/100 ████████░░
   Description:    78/100 ███████░░░
   Photos:         92/100 █████████░
   Pricing:        80/100 ████████░░
   Amenities:      88/100 ████████░░
   Reviews:        90/100 █████████░

✅ STRENGTHS:
   • Strong reviews (4.92★, 87 reviews)
   • Good photo coverage (18 photos)
   • Superhost status

💡 RECOMMENDATIONS:
   1. Add more details to description
   2. Consider adding 'dedicated workspace'
```

## Architecture

```
hosttools/
├── services/
│   └── listing-grader/     # ✅ Ready
│       ├── src/
│       │   └── listing_grader/
│       │       ├── grader.py    # Main class
│       │       ├── scorer.py    # Scoring algorithms
│       │       ├── models.py    # Data models
│       │       └── cli.py       # CLI interface
│       └── tests/
└── shared/                 # Coming soon
```

## Dependencies

All services use the **airbnb-scraper** package as their data source:

```bash
pip install git+https://github.com/rabi3laser/airbnb-scraper.git
```

## Tech Stack

- **Backend**: Python 3.8+
- **Scraping**: [airbnb-scraper](https://github.com/rabi3laser/airbnb-scraper)
- **Data**: Pydantic models
- **CLI**: argparse

## Revenue Projections

| Scenario | Users | ARPU | MRR | ARR |
|----------|-------|------|-----|-----|
| Pessimistic | 500 | $25 | $12,500 | $150K |
| Realistic | 2,000 | $35 | $70,000 | $840K |
| Optimistic | 5,000 | $45 | $225,000 | $2.7M |

## Development

```bash
# Clone
git clone https://github.com/rabi3laser/hosttools.git
cd hosttools/services/listing-grader

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## License

MIT

## Related Projects

- [airbnb-scraper](https://github.com/rabi3laser/airbnb-scraper) - High-performance Airbnb scraping library
