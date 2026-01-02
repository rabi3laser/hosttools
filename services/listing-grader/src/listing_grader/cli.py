"""
Listing Grader CLI v2
Command line interface - Airbnb Algorithm Aligned
"""

import argparse
import asyncio
import json
import sys
from typing import Optional

from .grader_v2 import ListingGraderV2, GradeResultV2


def print_grade_report(result: GradeResultV2, verbose: bool = False):
    """Pretty print Airbnb-aligned grade report"""
    
    grade_emoji = {
        "A+": "🏆", "A": "⭐", "A-": "⭐",
        "B+": "👍", "B": "👍", "B-": "👍",
        "C+": "📊", "C": "📊", "C-": "📊",
        "D+": "⚠️", "D": "⚠️", "D-": "⚠️",
        "F": "❌"
    }
    
    emoji = grade_emoji.get(result.grade, "📊")
    
    print(f"\n{'='*65}")
    print(f"🏠 AIRBNB VISIBILITY SCORE - Algorithm Aligned (2025)")
    print(f"{'='*65}")
    
    name = result.listing_name[:55] + "..." if len(result.listing_name) > 55 else result.listing_name
    print(f"📍 {name}")
    print(f"🔗 {result.listing_url}")
    print(f"{'='*65}")
    
    # Overall score
    print(f"\n{emoji} VISIBILITY SCORE: {result.overall_score}/100 (Grade: {result.grade})")
    
    filled = int(result.overall_score / 5)
    bar = "█" * filled + "░" * (20 - filled)
    print(f"   [{bar}]")
    
    # Guest Favorites eligibility
    if result.guest_favorites_eligible:
        print(f"\n   🏅 GUEST FAVORITES ELIGIBLE ✓")
    elif result.is_guest_favorite:
        print(f"\n   🏅 GUEST FAVORITES BADGE ✓")
    else:
        print(f"\n   ⚪ Not yet eligible for Guest Favorites")
    
    # Category breakdown
    print(f"\n📊 RANKING FACTORS (Airbnb Algorithm Weights):")
    print(f"   {'Factor':<20} {'Score':>6} {'Weight':>8} {'Impact':>10}")
    print(f"   {'-'*48}")
    
    categories = [
        ("Reviews", result.reviews_score, 25),
        ("Response Time", result.response_score, 15),
        ("Pricing", result.pricing_score, 15),
        ("Conversion", result.conversion_score, 12),
        ("Instant Book", result.instant_book_score, 10),
        ("Cancellations", result.cancellation_score, 8),
        ("Listing Quality", result.listing_quality_score, 8),
        ("Availability", result.availability_score, 7),
    ]
    
    for name, score, weight in categories:
        impact = score * weight / 100
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        print(f"   {name:<20} {score:>3}/100 {weight:>7}% {impact:>8.1f}pts")
    
    # Bonuses
    if result.superhost_bonus or result.guest_favorites_bonus:
        print(f"\n🎁 BADGES & BONUSES:")
        if result.superhost_bonus:
            print(f"   ✓ Superhost: +{result.superhost_bonus} points")
        if result.guest_favorites_bonus:
            print(f"   ✓ Guest Favorites: +{result.guest_favorites_bonus} points")
    
    # Key metrics
    print(f"\n📋 KEY METRICS:")
    print(f"   Rating: {result.rating}★ ({result.reviews_count} reviews)")
    print(f"   Response: {result.response_rate}% rate, {result.response_time_hours}h avg")
    print(f"   Instant Book: {'✓ Enabled' if result.instant_bookable else '✗ Disabled'}")
    print(f"   Cancellation Rate: {result.cancellation_rate}%")
    
    # Market comparison
    if result.competitors_analyzed > 0:
        print(f"\n📈 MARKET COMPARISON:")
        print(f"   Market Avg Price: {result.market_avg_price:.0f}/night")
        print(f"   Competitors Analyzed: {result.competitors_analyzed}")
    
    # Recommendations
    if result.recommendations:
        print(f"\n💡 TOP ACTIONS TO IMPROVE RANKING:")
        for i, rec in enumerate(result.recommendations[:8], 1):
            print(f"   {i}. {rec}")
    
    print(f"\n{'='*65}")
    print(f"Algorithm: {result.algorithm_version}")
    print(f"{'='*65}\n")


async def grade_listing(
    url: str,
    compare_market: bool = False,
    output_json: bool = False,
    verbose: bool = False,
    currency: str = "EUR",
):
    """Grade a single listing"""
    async with ListingGraderV2(currency=currency) as grader:
        try:
            result = await grader.grade(
                url,
                compare_market=compare_market,
            )
            
            if output_json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                print_grade_report(result, verbose=verbose)
            
            return 0
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error grading listing: {e}", file=sys.stderr)
            if verbose:
                import traceback
                traceback.print_exc()
            return 1


async def grade_batch(
    urls: list,
    compare_market: bool = False,
    output_json: bool = False,
    currency: str = "EUR",
):
    """Grade multiple listings"""
    async with ListingGraderV2(currency=currency) as grader:
        results = await grader.grade_batch(urls, compare_market=compare_market)
        
        if output_json:
            output = [r.to_dict() for r in results]
            print(json.dumps(output, indent=2))
        else:
            for result in results:
                print_grade_report(result)
            
            # Summary
            print(f"\n{'='*65}")
            print(f"📊 SUMMARY")
            print(f"{'='*65}")
            print(f"{'Listing':<40} {'Score':>8} {'Grade':>6} {'GF?':>5}")
            print(f"{'-'*62}")
            for r in results:
                name = r.listing_name[:35] + "..." if len(r.listing_name) > 35 else r.listing_name
                gf = "✓" if r.guest_favorites_eligible else "✗"
                print(f"{name:<40} {r.overall_score:>5}/100 {r.grade:>6} {gf:>5}")
        
        return 0


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Airbnb Visibility Score - Algorithm Aligned (2025)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Grade a single listing
  listing-grader https://www.airbnb.com/rooms/12345678
  
  # Grade with market comparison
  listing-grader https://www.airbnb.com/rooms/12345678 --compare-market
  
  # Output as JSON
  listing-grader https://www.airbnb.com/rooms/12345678 --json
  
  # Grade multiple listings
  listing-grader url1 url2 url3

Algorithm Weights (Airbnb 2025):
  Reviews/Guest Favorites  25%
  Response Rate & Time     15%
  Pricing                  15%
  Conversion Signals       12%
  Instant Book             10%
  Cancellation Rate         8%
  Listing Quality           8%
  Calendar Availability     7%
        """
    )
    
    parser.add_argument(
        "urls",
        nargs="+",
        help="Airbnb listing URL(s) or ID(s)"
    )
    
    parser.add_argument(
        "--compare-market", "-m",
        action="store_true",
        help="Compare with nearby listings for pricing insights"
    )
    
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output with debug info"
    )
    
    parser.add_argument(
        "--currency", "-c",
        default="EUR",
        help="Currency for pricing (default: EUR)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="listing-grader 2.0.0 (Airbnb Algorithm Aligned)"
    )
    
    args = parser.parse_args()
    
    # Run async
    if len(args.urls) == 1:
        exit_code = asyncio.run(grade_listing(
            args.urls[0],
            compare_market=args.compare_market,
            output_json=args.json,
            verbose=args.verbose,
            currency=args.currency,
        ))
    else:
        exit_code = asyncio.run(grade_batch(
            args.urls,
            compare_market=args.compare_market,
            output_json=args.json,
            currency=args.currency,
        ))
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
