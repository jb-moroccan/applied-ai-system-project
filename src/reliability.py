"""
Reliability testing and validation module.
Integrated into the recommendation workflow to measure and improve recommendation quality.
"""
from typing import List, Dict, Tuple
from dataclasses import dataclass
from statistics import mean, stdev
from src.recommender import Recommender, UserProfile, RecommendationScore


@dataclass
class ReliabilityReport:
    """Summarizes reliability metrics across a set of recommendations."""
    average_confidence: float
    average_consistency: float
    high_confidence_count: int
    low_confidence_count: int
    total_recommendations: int
    confidence_variance: float
    recommendations_needing_review: List[str]

    def print_summary(self):
        """Print a human-readable summary."""
        print(f"\n{'─'*70}")
        print("RELIABILITY REPORT")
        print(f"{'─'*70}")
        print(f"Total Recommendations Analyzed: {self.total_recommendations}")
        print(f"Average Confidence Score: {self.average_confidence:.2%}")
        print(f"Average Consistency Score: {self.average_consistency:.2%}")
        print(f"Confidence Variance: {self.confidence_variance:.4f}")
        print(f"High-Confidence Matches (≥80%): {self.high_confidence_count}")
        print(f"Low-Confidence Matches (<50%): {self.low_confidence_count}")

        if self.recommendations_needing_review:
            print(f"\n⚠ Recommendations Needing Review:")
            for rec in self.recommendations_needing_review:
                print(f"  • {rec}")
        else:
            print(f"\n✓ All recommendations meet quality thresholds")
        print(f"{'─'*70}")


def analyze_recommendation_reliability(
    recommendations: List[RecommendationScore],
) -> ReliabilityReport:
    """
    Analyze a set of recommendations and generate a reliability report.
    Provides metrics on confidence, consistency, and quality flags.
    """
    if not recommendations:
        return ReliabilityReport(
            average_confidence=0.0,
            average_consistency=0.0,
            high_confidence_count=0,
            low_confidence_count=0,
            total_recommendations=0,
            confidence_variance=0.0,
            recommendations_needing_review=[]
        )

    confidences = [r.confidence for r in recommendations]
    consistencies = [r.consistency_score for r in recommendations]

    needs_review = []
    high_conf_count = sum(1 for r in recommendations if r.confidence >= 0.8)
    low_conf_count = sum(1 for r in recommendations if r.confidence < 0.5)

    for rec in recommendations:
        if rec.confidence < 0.5 and rec.base_score < 3.0:
            needs_review.append(
                f"{rec.song.title} (confidence: {rec.confidence:.2%}, score: {rec.base_score:.2f})"
            )
        elif rec.consistency_score < 0.6:
            needs_review.append(
                f"{rec.song.title} (inconsistent scoring: {rec.consistency_score:.2%})"
            )

    conf_variance = stdev(confidences) if len(confidences) > 1 else 0.0

    return ReliabilityReport(
        average_confidence=mean(confidences),
        average_consistency=mean(consistencies),
        high_confidence_count=high_conf_count,
        low_confidence_count=low_conf_count,
        total_recommendations=len(recommendations),
        confidence_variance=conf_variance,
        recommendations_needing_review=needs_review
    )


def run_consistency_validation(
    recommender: Recommender,
    user_profile: UserProfile,
    num_runs: int = 5
) -> Dict:
    """
    Validate recommendation consistency across multiple runs.
    Returns statistics on ranking stability and confidence convergence.
    """
    all_runs = []
    ranking_positions = {}

    for _ in range(num_runs):
        recs = recommender.recommend_with_reliability(user_profile, k=5, use_self_critique=True)
        all_runs.append(recs)

        for position, rec in enumerate(recs):
            song_id = rec.song.id
            if song_id not in ranking_positions:
                ranking_positions[song_id] = []
            ranking_positions[song_id].append(position)

    position_variances = {
        song_id: stdev(positions) if len(positions) > 1 else 0
        for song_id, positions in ranking_positions.items()
    }

    confidence_deltas = {}
    if len(all_runs) > 1:
        first_run = all_runs[0]
        last_run = all_runs[-1]

        for i, rec in enumerate(first_run):
            if i < len(last_run):
                song_id = rec.song.id
                delta = abs(rec.confidence - last_run[i].confidence)
                confidence_deltas[rec.song.title] = delta

    most_stable = min(position_variances.items(), key=lambda x: x[1])[0] if position_variances else None
    least_stable = max(position_variances.items(), key=lambda x: x[1])[0] if position_variances else None

    return {
        "num_runs": num_runs,
        "ranking_stability": {
            "most_stable_song_id": most_stable,
            "least_stable_song_id": least_stable,
            "variances": position_variances
        },
        "confidence_convergence": confidence_deltas,
        "average_position_variance": mean(position_variances.values()) if position_variances else 0.0
    }


def filter_low_confidence_recommendations(
    recommendations: List[RecommendationScore],
    confidence_threshold: float = 0.5
) -> Tuple[List[RecommendationScore], List[RecommendationScore]]:
    """
    Split recommendations into high and low confidence groups.
    This filtering is integrated into the recommendation flow for quality control.
    """
    high_conf = [r for r in recommendations if r.confidence >= confidence_threshold]
    low_conf = [r for r in recommendations if r.confidence < confidence_threshold]
    return high_conf, low_conf


def get_recommendation_confidence_report(
    recommender: Recommender,
    user_profiles: List[UserProfile],
    profile_names: List[str] = None
) -> Dict:
    """
    Generate a comprehensive confidence report across multiple user profiles.
    Useful for evaluating overall system reliability.
    """
    if profile_names is None:
        profile_names = [f"Profile {i+1}" for i in range(len(user_profiles))]

    report = {}

    for profile, name in zip(user_profiles, profile_names):
        recs = recommender.recommend_with_reliability(profile, k=5, use_self_critique=True)
        reliability = analyze_recommendation_reliability(recs)

        report[name] = {
            "profile": profile,
            "recommendations": recs,
            "reliability_report": reliability,
        }

    return report
