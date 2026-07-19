"""
Command line runner for the Music Recommender Simulation with Reliability Scoring.
Demonstrates integrated confidence scoring and self-critique mechanisms.
"""
from pathlib import Path

try:
    from src.recommender import load_songs, recommend_songs, Song, UserProfile, Recommender
except ImportError:
    from recommender import load_songs, recommend_songs, Song, UserProfile, Recommender


def analyze_score_variance(user_profile, song, iterations=3):
    """
    Analyze why a song's score varies across multiple recommendation runs.
    Shows how genre, mood, energy, and acousticness contribution varies.
    """
    from src.recommender import score_song

    user_prefs = {
        "favorite_genre": user_profile.favorite_genre,
        "favorite_mood": user_profile.favorite_mood,
        "target_energy": user_profile.target_energy,
        "likes_acoustic": user_profile.likes_acoustic,
    }

    scores_breakdown = []

    for _ in range(iterations):
        score, reasons = score_song(user_prefs, {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "acousticness": song.acousticness,
            "title": song.title,
        })
        scores_breakdown.append((score, reasons))

    return scores_breakdown


def songs_dict_to_objects(songs_data):
    """Convert dictionary songs from CSV to Song objects."""
    return [Song(
        id=int(song['id']),
        title=song['title'],
        artist=song['artist'],
        genre=song['genre'],
        mood=song['mood'],
        energy=float(song['energy']),
        tempo_bpm=float(song['tempo_bpm']),
        valence=float(song['valence']),
        danceability=float(song['danceability']),
        acousticness=float(song['acousticness']),
    ) for song in songs_data]


def print_reliability_analysis(recommendations):
    """Pretty print recommendations with reliability metrics."""
    print(f"\n{'='*80}")
    print(f"{'Title':<30} {'Base Score':<12} {'Confidence':<15} {'Consistency':<15} {'Rating':<12}")
    print(f"{'='*80}")

    for rec in recommendations:
        score_display = f"{rec.base_score:.2f}"
        if rec.original_base_score != rec.base_score:
            score_display += f"*"

        print(f"{rec.song.title:<30} {score_display:<12} {rec.confidence:.2%}        {rec.consistency_score:.2%}        {rec.reliability_rating:<12}")

        if rec.reasons:
            for reason in rec.reasons[:2]:
                print(f"  - {reason}")

        if rec.critique_feedback:
            for feedback in rec.critique_feedback:
                print(f"  ! {feedback}")

        consistency_detail = rec.get_consistency_details()
        if len(rec.score_history) > 1:
            print(f"  Consistency: {consistency_detail}")

        if rec.original_base_score != rec.base_score:
            print(f"  * Adjusted by self-critique: {rec.original_base_score:.2f} -> {rec.base_score:.2f}")
        print()


def demo_consistency_testing(recommender, user_profile, iterations=3):
    """
    Demonstrate consistency testing by running the same recommendation multiple times.
    Shows how scores stabilize and confidence improves.
    """
    print(f"\n{'-'*80}")
    print(f"CONSISTENCY TEST: {iterations} iterations of the same user profile")
    print(f"{'-'*80}")

    all_scores = []

    for iteration in range(iterations):
        print(f"\n[Iteration {iteration + 1}]")
        recs = recommender.recommend_with_reliability(user_profile, k=3, use_self_critique=True)
        print_reliability_analysis(recs)
        all_scores.append(recs)

    print(f"\nCONSISTENCY BREAKDOWN BY SONG:")
    print(f"-"*80 + "\n")

    if len(all_scores) > 1:
        first_iter = all_scores[0]

        for rec in first_iter:
            song_title = rec.song.title
            song_id = rec.song.id
            all_history = recommender.consistency_history.get(song_id, [])

            print(f"{song_title}")
            print(f"  Base Score History: {[f'{s:.2f}' for s in all_history]}")

            if len(all_history) > 1:
                min_score = min(all_history)
                max_score = max(all_history)
                score_range = max_score - min_score
                print(f"  Range: {min_score:.2f} to {max_score:.2f} (delta: {score_range:.2f})")
                print(f"  Consistency Rating: {rec.consistency_score:.2%}")
            else:
                print(f"  Only 1 invocation - consistency not yet measurable")
            print()


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    songs_path = project_root / "data" / "songs.csv"
    songs_data = load_songs(str(songs_path))
    songs_objects = songs_dict_to_objects(songs_data)
    print(f"[OK] Loaded {len(songs_objects)} songs")

    user_profiles = [
        UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.8,
            likes_acoustic=False,
        ),
        UserProfile(
            favorite_genre="rock",
            favorite_mood="intense",
            target_energy=0.9,
            likes_acoustic=False,
        ),
        UserProfile(
            favorite_genre="lofi",
            favorite_mood="chill",
            target_energy=0.4,
            likes_acoustic=True,
        ),
    ]

    profile_names = ["High Energy Pop", "Deep Intense Rock", "Chill Lofi"]

    for user_profile, profile_names in zip(user_profiles, profile_names):
        recommender = Recommender(songs_objects)

        print(f"\n{'='*80}")
        print(f"PROFILE: {profile_names}")
        acoustic_pref = "Likes acoustics" if user_profile.likes_acoustic else "Doesn't like acoustics"
        print(f"Genre: {user_profile.favorite_genre}, Mood: {user_profile.favorite_mood}, Energy: {user_profile.target_energy}, Preference: {acoustic_pref}")
        print(f"{'='*80}")

        demo_consistency_testing(recommender, user_profile, iterations=2)


if __name__ == "__main__":
    main()
