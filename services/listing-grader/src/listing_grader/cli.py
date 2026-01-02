"""
Listing Grader CLI
Command line interface for grading Airbnb listings
"""

import argparse
import asyncio
import json
import sys
from typing import Optional

from .grader import ListingGrader


def print_grade_result(result, verbose: bool = False):
    """Pretty print grade result"""
    # Grade emoji mapping
    grade_emoji = {
        "A+": "🏆", "A": "⭐", "A-": "⭐",
        "B+": "👍", "B": "👍", "B-": "👍",
        "C+": "📊", "C": "📊", "C-": "📊",
        "D+": "⚠️", "D": "⚠️", "D-": "⚠️",
        "F": "❌"
    }
    
    emoji = grade_emoji.get(result.grade, "📊")
    
    print(f"\n{'='*60}")
    print(f"🏠 LISTING GRADE REPORT")
    print(f"{'='*60}")
    print(f"📍 {result.listing_name[:50]}..." if len(result.listing_name) > 50 else f"📍 {result.listing_name}")
    print(f"🔗 {result.listing_url}")
    print(f"{'='*60}")
    
    # Overall score
    print(f"\n{emoji} OVERALL SCORE: {result.overall_score}/100 (Grade: {result.grade})")
    
    # Score bar
    filled = int(result.overall_score / 5)
    bar = "█" * filled + "░" * (20 - filled)
    print(f"   [{bar}]")
    
    # Category breakdown
    print(f"\n📊 CATEGORY SCORES:")
    print(f"   {'Title:':<15} {result.title_score:>3}/100 {'█' * (result.title_score // 10)}{'░' * (10 - result.title_score // 10)}")
    print(f"   {'Description:':<15} {result.description_score:>3}/100 {'█' * (result.description_score // 10)}{'░' * (10 - result.description_score // 10)}")
    print(f"   {'Photos:':<15} {result.photos_score:>3}/100 {'█' * (result.photos_score // 10)}{'░' * (10 - result.photos_score // 10)}")
    print(f"   {'Pricing:':<15} {result.pricing_score:>3}/100 {'█' * (result.pricing_score // 10)}{'░' * (10 - result.pricing_score // 10)}")
    print(f"   {'Amenities:':<15} {result.amenities_score:>3}/100 {'█' * (result.amenities_score // 10)}{'░' * (10 - result.amenities_score // 10)}")
    print(f"   {'Reviews:':<15} {result.reviews_score:>3}/100 {'█' * (result.reviews_score // 10)}{'░' * (10 - result.reviews_score // 10)}")
    
    # Bonuses
    if result.superhost_bonus or result.instant_book_bonus:
        print(f"\n🎁 BONUSES:")
        if result.superhost_bonus:
            print(f"   ✓ Superhost: +{result.superhost_bonus} points")
        if result.instant_book_bonus:
            print(f"   ✓ Instant Book: +{result.instant_book_bonus} points")
    
    # Market comparison
    if result.competitor_avg_score:
        print(f"\n📈 MARKET COMPARISON:")
        print(f"   Your Score: {result.overall_score}/100")
        print(f"   Market Avg: {result.competitor_avg_score}/100")
        print(f"   Percentile: Top {100 - result.market_percentile}%")
        print(f"   Competitors Analyzed: {result.competitors_analyzed}")
    
    # Strengths
    if result.strengths:
        print(f"\n✅ STRENGTHS:")
        for s in result.strengths:
            print(f"   • {s}")
    
    # Weaknesses
    if result.weaknesses:
        print(f"\n⚠️ AREAS TO IMPROVE:")
        for w in result.weaknesses:
            print(f"   • {w}")
    
    # Recommendations
    if result.recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(result.recommendations[:7], 1):
            print(f"   {i}. {rec}")
    
    print(f"\n{'='*60}")
    print(f"Graded at: {result.graded_at}")
    print(f"{'='*60}\n")


async def grade_listing(
    url: str,
    compare_market: bool = False,
    output_json: bool = False,
    verbose: bool = False,
    currency: str = "EUR",
):
    """Grade a single listing"""
    async with ListingGrader(currency=currency) as grader:
        try:
            result = await grader.grade(
                url,
                compare_market=compare_market,
            )
            
            if output_json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                print_grade_result(result, verbose=verbose)
            
            return 0
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error grading listing: {e}", file=sys.stderr)
            return 1


async def grade_batch(
    urls: list,
    compare_market: bool = False,
    output_json: bool = False,
    currency: str = "EUR",
):
    """Grade multiple listings"""
    async with ListingGrader(currency=currency) as grader:
        results = await grader.grade_batch(urls, compare_market=compare_market)
        
        if output_json:
            output = [r.to_dict() for r in results]
            print(json.dumps(output, indent=2))
        else:
            for result in results:
                print_grade_result(result)
        
        return 0


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Grade your Airbnb listing 0-100 with actionable recommendations",
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
  
  # Use different currency
  listing-grader https://www.airbnb.com/rooms/12345678 --currency USD
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
        help="Verbose output"
    )
    
    parser.add_argument(
        "--currency", "-c",
        default="EUR",
        help="Currency for pricing (default: EUR)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="listing-grader 1.0.0"
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
