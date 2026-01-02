# HostTools - Microservices Suite for Airbnb Hosts

A collection of independent, revenue-generating microservices designed to help Airbnb hosts optimize their listings, monitor competition, and maximize revenue.

## Vision

In 2025, Airbnb market saturation means hosts must differentiate or die. HostTools provides the competitive edge:

- **42%** of hosts feel disadvantaged by Airbnb's algorithm
- **31%** cite algorithmic unpredictability as top stressor
- Average host loses **$2,000+/year** to suboptimal pricing

## Microservices

| Service | Status | Description | Pricing |
|---------|--------|-------------|---------|
| **Listing Grader** | 🚧 Building | Score your listing 0-100 with recommendations | $9-19/mo |
| **CompSet Spy** | 📋 Planned | Monitor competitors' prices in real-time | $19-49/mo |
| **Price Alert** | 📋 Planned | Get notified when market prices change | $9-29/mo |
| **Event Radar** | 📋 Planned | Detect local events to optimize pricing | $29-79/mo |
| **Review Analyzer** | 📋 Planned | Sentiment analysis of your reviews | $15-35/mo |
| **Gap Filler** | 📋 Planned | Optimize orphan nights and minimum stays | $19-39/mo |

## Architecture

```
hosttools/
├── services/
│   ├── listing-grader/      # Service 1 - MVP
│   ├── compset-spy/         # Service 2
│   ├── price-alert/         # Service 3
│   └── ...
├── shared/
│   ├── config.py            # Shared configuration
│   └── models.py            # Shared data models
└── frontend/
    └── dashboard/           # Unified dashboard
```

## Dependencies

- **airbnb-scraper**: High-performance Airbnb scraping library
  ```bash
  pip install git+https://github.com/rabi3laser/airbnb-scraper.git
  ```

## Tech Stack

- **Backend**: Python, FastAPI
- **Database**: Supabase (PostgreSQL)
- **Scraping**: airbnb-scraper package
- **Frontend**: Next.js, Tailwind CSS
- **Payments**: Stripe

## Revenue Projections

| Scenario | Users | ARPU | MRR | ARR |
|----------|-------|------|-----|-----|
| Pessimistic | 500 | $25 | $12,500 | $150K |
| Realistic | 2,000 | $35 | $70,000 | $840K |
| Optimistic | 5,000 | $45 | $225,000 | $2.7M |

## License

MIT
