from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        scored = []
        for song in self.songs:
            score, _ = score_song(user_prefs, {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "acousticness": song.acousticness,
                "title": song.title,
            })
            scored.append((score, song))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [song for _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        _, reasons = score_song(user_prefs, {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "acousticness": song.acousticness,
            "title": song.title,
        })
        return "; ".join(reasons) if reasons else "No matching reasons found."

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        songs = []
        for row in reader:
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons: List[str] = []

    favorite_genre = user_prefs.get("favorite_genre")
    favorite_mood = user_prefs.get("favorite_mood")
    target_energy = user_prefs.get("target_energy", 0.0)
    likes_acoustic = user_prefs.get("likes_acoustic", False)

    genre_match = 1 if favorite_genre and song.get("genre") == favorite_genre else 0
    genre_score = genre_match * 4.0
    score += genre_score
    if genre_match:
        reasons.append("Genre matches your favorite genre")
    elif favorite_genre:
        reasons.append("Genre does not match your favorite genre")

    mood_match = 1 if favorite_mood and song.get("mood") == favorite_mood else 0
    mood_score = mood_match * 2.0
    score += mood_score
    if mood_match:
        reasons.append("Mood matches your favorite mood")
    elif favorite_mood:
        reasons.append("Mood does not match your favorite mood")

    energy = song.get("energy", 0.0)
    energy_distance = abs(energy - target_energy)
    energy_score = max(0.0, 1.0 - energy_distance)
    score += energy_score
    reasons.append(f"Energy score: {energy_score:.2f} based on proximity to your target energy")

    acousticness = song.get("acousticness", 0.0)
    acoustic_match = 1 if (likes_acoustic and acousticness >= 0.5) or (not likes_acoustic and acousticness < 0.5) else 0
    score += acoustic_match
    if acoustic_match:
        reasons.append("Acousticness matches your preference")
    else:
        reasons.append("Acousticness does not match your preference")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
