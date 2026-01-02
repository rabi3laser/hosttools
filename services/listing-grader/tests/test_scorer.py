"""
Tests for Listing Grader scoring algorithms
"""

import pytest
from listing_grader.models import ListingData, GradeResult, score_to_grade
from listing_grader.scorer import (
    score_title,
    score_description,
    score_photos,
    score_pricing,
    score_amenities,
    score_reviews,
    calculate_overall_score,
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def excellent_listing():
    """A well-optimized listing"""
    return ListingData(
        listing_id="123456",
        name="Cozy Modern Apartment in Central Paris - Stunning Views",
        description="""
        Welcome to our beautiful apartment in the heart of Paris!
        
        Located in the vibrant Marais district, this modern flat offers everything 
        you need for a perfect stay. The apartment features a fully equipped kitchen,
        high-speed wifi, and a comfortable queen bed with premium linens.
        
        The neighborhood is full of amazing restaurants, cafes, and boutiques.
        The metro station is just 2 minutes walk, giving you easy access to all
        major attractions. Charles de Gaulle airport is 45 minutes by train.
        
        Check-in is flexible with our self check-in system. Please note this is
        a quiet building - no parties or loud music after 10pm.
        """,
        images=["img1.jpg"] * 18,
        amenities=[
            "Wifi", "Kitchen", "Air conditioning", "Heating", "Washer", "Dryer",
            "TV", "Hot water", "Essentials", "Bed linens", "Dedicated workspace",
            "Self check-in", "Smoke detector", "Carbon monoxide detector",
        ],
        rating=4.92,
        reviews_count=87,
        is_superhost=True,
        instant_bookable=True,
        price_per_night=150,
        city="Paris",
    )


@pytest.fixture
def poor_listing():
    """A poorly optimized listing"""
    return ListingData(
        listing_id="789",
        name="Room",
        description="Nice room. Good location.",
        images=["img1.jpg", "img2.jpg"],
        amenities=["Wifi"],
        rating=3.8,
        reviews_count=3,
        is_superhost=False,
        instant_bookable=False,
        price_per_night=50,
    )


@pytest.fixture
def average_listing():
    """An average listing"""
    return ListingData(
        listing_id="456",
        name="Nice apartment near downtown",
        description="""
        Comfortable apartment with all basics. Kitchen available.
        Good location near restaurants and shops.
        """,
        images=["img.jpg"] * 8,
        amenities=["Wifi", "Kitchen", "TV", "Heating", "Hot water"],
        rating=4.5,
        reviews_count=25,
        is_superhost=False,
        instant_bookable=True,
        price_per_night=80,
    )


# ============================================
# TITLE SCORING TESTS
# ============================================

class TestTitleScoring:
    
    def test_excellent_title(self, excellent_listing):
        result = score_title(excellent_listing)
        assert result.score >= 70
        assert len(result.recommendations) == 0 or len(result.recommendations) <= 1
    
    def test_poor_title_too_short(self, poor_listing):
        result = score_title(poor_listing)
        assert result.score < 50
        assert any("short" in r.lower() for r in result.recommendations)
    
    def test_title_with_all_caps(self):
        listing = ListingData(listing_id="1", name="AMAZING APARTMENT IN PARIS!!!")
        result = score_title(listing)
        assert result.score < 60
        assert any("caps" in r.lower() for r in result.recommendations)
    
    def test_title_optimal_length(self):
        listing = ListingData(
            listing_id="1",
            name="Cozy Studio in Central London - Perfect for Couples",
            city="London"
        )
        result = score_title(listing)
        assert result.score >= 70
    
    def test_title_with_location(self):
        listing = ListingData(
            listing_id="1",
            name="Beautiful apartment in Barcelona center",
            city="Barcelona"
        )
        result = score_title(listing)
        # Should get bonus for including city
        assert result.score >= 60


# ============================================
# DESCRIPTION SCORING TESTS
# ============================================

class TestDescriptionScoring:
    
    def test_excellent_description(self, excellent_listing):
        result = score_description(excellent_listing)
        assert result.score >= 70
    
    def test_poor_description_too_short(self, poor_listing):
        result = score_description(poor_listing)
        assert result.score < 50
        assert any("short" in r.lower() or "detail" in r.lower() for r in result.recommendations)
    
    def test_description_with_all_topics(self):
        listing = ListingData(
            listing_id="1",
            description="""
            Located in the heart of downtown, this apartment is perfect for travelers.
            
            The neighborhood has great restaurants and cafes. The metro station is 
            5 minutes walk away, and the airport is easily accessible by train.
            
            The kitchen is fully equipped with all essentials. High-speed wifi
            is available throughout. Fresh towels and bed linens provided.
            
            Check-in is at 3pm, checkout at 11am. Please note this is a no smoking
            property. Quiet hours after 10pm.
            """
        )
        result = score_description(listing)
        assert result.score >= 75  # Should cover all topics


# ============================================
# PHOTOS SCORING TESTS
# ============================================

class TestPhotosScoring:
    
    def test_excellent_photos(self, excellent_listing):
        result = score_photos(excellent_listing)
        assert result.score >= 80
    
    def test_poor_photos_too_few(self, poor_listing):
        result = score_photos(poor_listing)
        assert result.score < 50
        assert any("photo" in r.lower() for r in result.recommendations)
    
    def test_no_photos(self):
        listing = ListingData(listing_id="1", images=[])
        result = score_photos(listing)
        assert result.score == 0
        assert any("critical" in r.lower() or "no photo" in r.lower() for r in result.recommendations)
    
    def test_optimal_photo_count(self):
        listing = ListingData(listing_id="1", images=["img.jpg"] * 20)
        result = score_photos(listing)
        assert result.score >= 80
    
    def test_too_many_photos(self):
        listing = ListingData(listing_id="1", images=["img.jpg"] * 60)
        result = score_photos(listing)
        # Should still be good but might have recommendation
        assert result.score >= 60


# ============================================
# PRICING SCORING TESTS
# ============================================

class TestPricingScoring:
    
    def test_pricing_without_market_data(self, excellent_listing):
        result = score_pricing(excellent_listing)
        assert result.score >= 60  # Neutral without comparison
    
    def test_pricing_at_market_average(self, excellent_listing):
        result = score_pricing(excellent_listing, market_avg=150)
        assert result.score >= 75
    
    def test_pricing_below_market(self, excellent_listing):
        result = score_pricing(excellent_listing, market_avg=200)
        assert result.score >= 80  # Good value
    
    def test_pricing_above_market(self, excellent_listing):
        result = score_pricing(excellent_listing, market_avg=100)
        assert result.score < 70
        assert len(result.recommendations) > 0
    
    def test_no_price(self):
        listing = ListingData(listing_id="1", price_per_night=0)
        result = score_pricing(listing)
        assert result.score == 0


# ============================================
# AMENITIES SCORING TESTS
# ============================================

class TestAmenitiesScoring:
    
    def test_excellent_amenities(self, excellent_listing):
        result = score_amenities(excellent_listing)
        assert result.score >= 70
    
    def test_poor_amenities(self, poor_listing):
        result = score_amenities(poor_listing)
        assert result.score < 50
        assert len(result.recommendations) > 0
    
    def test_essential_amenities_only(self):
        listing = ListingData(
            listing_id="1",
            amenities=["Wifi", "Kitchen", "Heating", "Hot water", "Essentials"]
        )
        result = score_amenities(listing)
        assert result.score >= 50  # Basic coverage
    
    def test_premium_amenities_bonus(self):
        basic = ListingData(
            listing_id="1",
            amenities=["Wifi", "Kitchen", "Heating"]
        )
        premium = ListingData(
            listing_id="2",
            amenities=["Wifi", "Kitchen", "Heating", "Pool", "Hot tub", "Gym"]
        )
        basic_result = score_amenities(basic)
        premium_result = score_amenities(premium)
        assert premium_result.score > basic_result.score


# ============================================
# REVIEWS SCORING TESTS
# ============================================

class TestReviewsScoring:
    
    def test_excellent_reviews(self, excellent_listing):
        result = score_reviews(excellent_listing)
        assert result.score >= 80
    
    def test_poor_reviews(self, poor_listing):
        result = score_reviews(poor_listing)
        assert result.score < 50
    
    def test_new_listing_no_reviews(self):
        listing = ListingData(listing_id="1", rating=0, reviews_count=0, is_new=True)
        result = score_reviews(listing)
        # New listing should get some leniency
        assert result.score >= 20
    
    def test_high_rating_few_reviews(self):
        listing = ListingData(listing_id="1", rating=5.0, reviews_count=3)
        result = score_reviews(listing)
        # Good rating but few reviews
        assert 40 <= result.score <= 70
    
    def test_perfect_reviews(self):
        listing = ListingData(listing_id="1", rating=5.0, reviews_count=150)
        result = score_reviews(listing)
        assert result.score >= 90


# ============================================
# OVERALL SCORING TESTS
# ============================================

class TestOverallScoring:
    
    def test_calculate_overall_excellent(self, excellent_listing):
        title = score_title(excellent_listing)
        desc = score_description(excellent_listing)
        photos = score_photos(excellent_listing)
        pricing = score_pricing(excellent_listing, market_avg=150)
        amenities = score_amenities(excellent_listing)
        reviews = score_reviews(excellent_listing)
        
        overall, superhost, instant = calculate_overall_score(
            title, desc, photos, pricing, amenities, reviews,
            is_superhost=True, instant_bookable=True
        )
        
        assert overall >= 75
        assert superhost == 5
        assert instant == 3
    
    def test_calculate_overall_poor(self, poor_listing):
        title = score_title(poor_listing)
        desc = score_description(poor_listing)
        photos = score_photos(poor_listing)
        pricing = score_pricing(poor_listing)
        amenities = score_amenities(poor_listing)
        reviews = score_reviews(poor_listing)
        
        overall, superhost, instant = calculate_overall_score(
            title, desc, photos, pricing, amenities, reviews,
            is_superhost=False, instant_bookable=False
        )
        
        assert overall < 50
        assert superhost == 0
        assert instant == 0


# ============================================
# GRADE CONVERSION TESTS
# ============================================

class TestGradeConversion:
    
    def test_grade_a_plus(self):
        assert score_to_grade(95) == "A+"
        assert score_to_grade(100) == "A+"
    
    def test_grade_a(self):
        assert score_to_grade(90) == "A"
        assert score_to_grade(94) == "A"
    
    def test_grade_b(self):
        assert score_to_grade(75) == "B"
        assert score_to_grade(79) == "B"
    
    def test_grade_c(self):
        assert score_to_grade(60) == "C"
        assert score_to_grade(64) == "C"
    
    def test_grade_f(self):
        assert score_to_grade(0) == "F"
        assert score_to_grade(39) == "F"


# ============================================
# INTEGRATION TESTS
# ============================================

class TestIntegration:
    
    def test_grade_result_to_dict(self, excellent_listing):
        result = GradeResult(
            listing_id="123",
            listing_url="https://airbnb.com/rooms/123",
            listing_name="Test Listing",
            overall_score=85,
            grade="A-",
            title_score=80,
            description_score=75,
            photos_score=90,
            pricing_score=80,
            amenities_score=85,
            reviews_score=88,
            recommendations=["Add more photos"],
            strengths=["Great reviews"],
            weaknesses=["Short description"],
        )
        
        d = result.to_dict()
        
        assert d["overall_score"] == 85
        assert d["grade"] == "A-"
        assert d["category_scores"]["photos"] == 90
        assert "Add more photos" in d["recommendations"]
