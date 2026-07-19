from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import csv
from statistics import mean, stdev

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

@dataclass
class RecommendationScore:
    """
    Extended recommendation with confidence and reliability scoring.
    """
    song: Song
    base_score: float
    confidence: float
    reliability_rating: str
    consistency_score: float
    critique_feedback: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    score_history: List[float] = field(default_factory=list)
    original_base_score: float = field(default=0.0)

    def overall_rank_score(self) -> float:
        """Combines base score with confidence weighting."""
        return self.base_score * (0.7 + 0.3 * self.confidence)

    def get_consistency_details(self) -> str:
        """Return human-readable explanation of consistency score."""
        if len(self.score_history) < 2:
            return f"Only 1 invocation recorded, consistency not yet measurable"

        min_score = min(self.score_history)
        max_score = max(self.score_history)
        avg_score = mean(self.score_history)
        score_range = max_score - min_score

        if score_range == 0:
            return f"Perfectly stable: base scores were {[f'{s:.2f}' for s in self.score_history]} (variance: 0.00)"
        else:
            return f"Base scores ranged from {min_score:.2f} to {max_score:.2f} (avg: {avg_score:.2f}, range: {score_range:.2f})"

class Recommender:
    """
    OOP implementation of the recommendation logic with reliability scoring.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs
        self.consistency_history: Dict[int, List[float]] = {}

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

    def recommend_with_reliability(self, user: UserProfile, k: int = 5, use_self_critique: bool = True) -> List[RecommendationScore]:
        """
        Generate recommendations with confidence scoring and optional self-critique.
        This is the primary recommendation method when reliability matters.
        """
        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        scored_recs = []

        for song in self.songs:
            score, reasons = score_song(user_prefs, {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "acousticness": song.acousticness,
                "title": song.title,
            })
            confidence = calculate_confidence(user_prefs, song)
            consistency, score_history = self._get_consistency_score(song.id, score)
            reliability = _rate_reliability(confidence, consistency)

            rec_score = RecommendationScore(
                song=song,
                base_score=score,
                confidence=confidence,
                consistency_score=consistency,
                reliability_rating=reliability,
                reasons=reasons,
                score_history=score_history,
                original_base_score=score
            )
            scored_recs.append(rec_score)

        if use_self_critique:
            scored_recs = self._apply_self_critique(scored_recs, user_prefs)

        scored_recs.sort(key=lambda r: r.overall_rank_score(), reverse=True)
        return scored_recs[:k]

    def _get_consistency_score(self, song_id: int, current_score: float) -> Tuple[float, List[float]]:
        """
        Track consistency of song scores across multiple invocations.
        Returns (consistency_score, score_history)
        """
        if song_id not in self.consistency_history:
            self.consistency_history[song_id] = []

        self.consistency_history[song_id].append(current_score)
        history = self.consistency_history[song_id]

        if len(history) < 2:
            return 1.0, history

        avg_score = mean(history)
        variance = stdev(history) if len(history) > 1 else 0
        consistency = max(0, 1.0 - (variance / (avg_score + 1)))
        return min(1.0, consistency), history

    def _apply_self_critique(self, scored_recs: List[RecommendationScore], user_prefs: Dict) -> List[RecommendationScore]:
        """
        Self-critique loop: re-evaluate top recommendations and adjust scores.
        Checks if there are better alternatives in the catalog before penalizing.
        """
        critiqued = []
        confidence_threshold = 0.5

        # Calculate catalog statistics for context
        all_scores = [self._score_song_internal(user_prefs, song) for song in self.songs]
        high_confidence_songs = sum(1 for score, _ in all_scores if score >= 5.0)
        moderate_confidence_songs = sum(1 for score, _ in all_scores if 3.0 <= score < 5.0)

        for rec in scored_recs:
            critique = []
            adjusted_score = rec.base_score

            is_confident = rec.confidence >= confidence_threshold
            is_consistent = rec.consistency_score >= 0.6

            # Critique 1: Check if there are better alternatives available
            has_better_alternatives = high_confidence_songs > 3
            if rec.base_score < 4.0 and has_better_alternatives:
                critique.append(f"Low base score ({rec.base_score:.2f}) - catalog has {high_confidence_songs} better-matching songs available")
                adjusted_score *= 0.70

            # Critique 2: Low confidence despite being recommended
            if not is_confident and rec.base_score < 3.0:
                critique.append(f"Very low confidence match (confidence: {rec.confidence:.2f})")
                adjusted_score *= 0.85

            # Critique 3: Inconsistent scoring
            if not is_consistent and len(self.consistency_history.get(rec.song.id, [])) > 2:
                critique.append(f"Inconsistent scoring across calls (consistency: {rec.consistency_score:.2f})")
                adjusted_score *= 0.90

            # Positive critique: High-confidence, consistent recommendation
            if rec.base_score >= 5.0 and rec.consistency_score >= 0.75:
                critique.append("High-confidence, consistent recommendation")

            # Info: Catalog context for moderate matches
            if rec.base_score >= 3.0 and rec.base_score < 5.0:
                critique.append(f"Moderate match - {moderate_confidence_songs} other songs also available in this range")

            # Info: Catalog context for weak matches
            if rec.base_score < 3.0 and not has_better_alternatives:
                critique.append(f"Weak match, but limited alternatives in catalog ({high_confidence_songs} high-confidence songs available)")

            rec.critique_feedback = critique
            rec.base_score = adjusted_score
            critiqued.append(rec)

        return critiqued

    def _score_song_internal(self, user_prefs: Dict, song: Song) -> Tuple[float, List[str]]:
        """Internal helper to score a song for critique analysis."""
        return score_song(user_prefs, {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "acousticness": song.acousticness,
            "title": song.title,
        })

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

def calculate_confidence(user_prefs: Dict, song: Song) -> float:
    """
    Calculate confidence score (0-1) based on how well song matches user profile.
    Higher score = higher confidence in the recommendation.
    """
    confidence_factors = []

    genre_match = user_prefs.get("favorite_genre") == song.genre
    confidence_factors.append(1.0 if genre_match else 0.3)

    mood_match = user_prefs.get("favorite_mood") == song.mood
    confidence_factors.append(1.0 if mood_match else 0.4)

    target_energy = user_prefs.get("target_energy", 0.5)
    energy_diff = abs(song.energy - target_energy)
    energy_confidence = max(0.2, 1.0 - energy_diff)
    confidence_factors.append(energy_confidence)

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    acoustic_match = (likes_acoustic and song.acousticness >= 0.5) or (not likes_acoustic and song.acousticness < 0.5)
    confidence_factors.append(1.0 if acoustic_match else 0.3)

    return mean(confidence_factors)


def _rate_reliability(confidence: float, consistency: float) -> str:
    """Rate recommendation reliability as a categorical label."""
    combined_score = (confidence + consistency) / 2
    if combined_score >= 0.85:
        return "EXCELLENT"
    elif combined_score >= 0.70:
        return "GOOD"
    elif combined_score >= 0.55:
        return "FAIR"
    else:
        return "LOW"


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
    if energy_score >= 0.8:
        energy_match_text = "high match"
    elif energy_score >= 0.5:
        energy_match_text = "moderate match"
    else:
        energy_match_text = "low match"
    reasons.append(
        f"Energy score: {energy_score:.2f} ({energy_match_text}) based on proximity to your target energy"
    )

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
