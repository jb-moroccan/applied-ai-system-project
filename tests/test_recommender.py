from src.recommender import Song, UserProfile, Recommender, score_song

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
