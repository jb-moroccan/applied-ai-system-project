from src.recommender import Song, UserProfile, Recommender, score_song, calculate_confidence, RecommendationScore
from src.reliability import (
    analyze_recommendation_reliability,
    run_consistency_validation,
    filter_low_confidence_recommendations,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
        Song(
            id=3,
            title="Intense Rock Anthem",
            artist="Test Artist",
            genre="rock",
            mood="intense",
            energy=0.95,
            tempo_bpm=140,
            valence=0.5,
            danceability=0.6,
            acousticness=0.1,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_score_song_prefers_intense_rock_over_chill_lofi():
    user_prefs = {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.9,
        "likes_acoustic": False,
    }

    intense_rock = {
        "title": "Storm Runner",
        "genre": "rock",
        "mood": "intense",
        "energy": 0.91,
        "acousticness": 0.10,
    }
    chill_lofi = {
        "title": "Midnight Coding",
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.42,
        "acousticness": 0.71,
    }

    rock_score, rock_reasons = score_song(user_prefs, intense_rock)
    lofi_score, lofi_reasons = score_song(user_prefs, chill_lofi)

    assert rock_score > lofi_score
    assert any("genre" in reason.lower() or "mood" in reason.lower() for reason in rock_reasons)
    assert any("acoustic" in reason.lower() for reason in rock_reasons)


def test_confidence_scoring_high_for_perfect_match():
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
    }
    song = Song(
        id=1,
        title="Perfect Pop Match",
        artist="Test Artist",
        genre="pop",
        mood="happy",
        energy=0.8,
        tempo_bpm=120,
        valence=0.9,
        danceability=0.8,
        acousticness=0.1,
    )

    confidence = calculate_confidence(user_prefs, song)
    assert confidence > 0.85, f"Expected high confidence, got {confidence}"


def test_confidence_scoring_low_for_mismatched_song():
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
    }
    song = Song(
        id=2,
        title="Mismatched Track",
        artist="Test Artist",
        genre="metal",
        mood="sad",
        energy=0.1,
        tempo_bpm=60,
        valence=0.2,
        danceability=0.2,
        acousticness=0.8,
    )

    confidence = calculate_confidence(user_prefs, song)
    assert confidence < 0.5, f"Expected low confidence, got {confidence}"


def test_recommend_with_reliability_returns_extended_scores():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend_with_reliability(user, k=2, use_self_critique=False)

    assert len(results) == 2
    assert all(isinstance(r, RecommendationScore) for r in results)
    assert all(hasattr(r, "confidence") for r in results)
    assert all(hasattr(r, "consistency_score") for r in results)
    assert all(hasattr(r, "reliability_rating") for r in results)


def test_self_critique_adjusts_low_confidence_scores():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()

    without_critique = rec.recommend_with_reliability(user, k=3, use_self_critique=False)
    with_critique = rec.recommend_with_reliability(user, k=3, use_self_critique=True)

    assert len(with_critique) > 0
    for crit_rec in with_critique:
        if crit_rec.confidence < 0.5:
            assert len(crit_rec.critique_feedback) > 0


def test_consistency_tracking_across_invocations():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()

    rec.recommend_with_reliability(user, k=2, use_self_critique=False)
    rec.recommend_with_reliability(user, k=2, use_self_critique=False)
    rec.recommend_with_reliability(user, k=2, use_self_critique=False)

    assert len(rec.consistency_history) > 0
    for song_id, scores in rec.consistency_history.items():
        assert len(scores) >= 1


def test_filter_low_confidence_recommendations():
    rec_list = [
        RecommendationScore(
            song=Song(1, "High Conf", "Artist", "pop", "happy", 0.8, 120, 0.9, 0.8, 0.2),
            base_score=8.0,
            confidence=0.9,
            reliability_rating="EXCELLENT",
            consistency_score=0.95,
        ),
        RecommendationScore(
            song=Song(2, "Low Conf", "Artist", "metal", "sad", 0.1, 60, 0.2, 0.2, 0.8),
            base_score=1.0,
            confidence=0.3,
            reliability_rating="LOW",
            consistency_score=0.4,
        ),
    ]

    high_conf, low_conf = filter_low_confidence_recommendations(rec_list, confidence_threshold=0.5)

    assert len(high_conf) == 1
    assert len(low_conf) == 1
    assert high_conf[0].confidence >= 0.5
    assert low_conf[0].confidence < 0.5


def test_consistency_validation_detects_unstable_rankings():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()

    validation = run_consistency_validation(rec, user, num_runs=3)

    assert validation["num_runs"] == 3
    assert "ranking_stability" in validation
    assert "average_position_variance" in validation
    assert validation["average_position_variance"] >= 0


def test_reliability_report_analysis():
    rec_list = [
        RecommendationScore(
            song=Song(1, "Song A", "Artist", "pop", "happy", 0.8, 120, 0.9, 0.8, 0.2),
            base_score=8.0,
            confidence=0.95,
            reliability_rating="EXCELLENT",
            consistency_score=0.92,
        ),
        RecommendationScore(
            song=Song(2, "Song B", "Artist", "rock", "intense", 0.9, 140, 0.5, 0.6, 0.1),
            base_score=7.0,
            confidence=0.85,
            reliability_rating="GOOD",
            consistency_score=0.88,
        ),
    ]

    report = analyze_recommendation_reliability(rec_list)

    assert report.total_recommendations == 2
    assert report.average_confidence > 0.8
    assert report.high_confidence_count >= 1
    assert report.average_consistency > 0.8


def test_overall_rank_score_combines_base_and_confidence():
    rec = RecommendationScore(
        song=Song(1, "Test", "Artist", "pop", "happy", 0.8, 120, 0.9, 0.8, 0.2),
        base_score=8.0,
        confidence=0.8,
        reliability_rating="GOOD",
        consistency_score=0.9,
    )

    rank_score = rec.overall_rank_score()
    assert rank_score == 8.0 * (0.7 + 0.3 * 0.8)
    assert rank_score > 0
