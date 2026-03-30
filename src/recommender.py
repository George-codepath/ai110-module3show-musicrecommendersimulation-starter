import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass

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
        """Return the top-k songs sorted by recommendation score."""
        scored_songs = sorted(
            self.songs,
            key=lambda song: score_song_from_profile(user, song)[0],
            reverse=True,
        )
        return scored_songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a short explanation of why a song was recommended."""
        score, reasons = score_song_from_profile(user, song)
        reason_text = ", ".join(reasons)
        return f"Score {score:.2f} based on {reason_text}."


def score_song_from_profile(user: UserProfile, song: Song) -> Tuple[float, List[str]]:
    """Score one Song against a UserProfile and return reasons."""
    score = 0.0
    reasons: List[str] = []

    if song.genre == user.favorite_genre:
        score += 2.0
        reasons.append("genre match (+2.0)")

    if song.mood == user.favorite_mood:
        score += 1.0
        reasons.append("mood match (+1.0)")

    energy_similarity = 1 - abs(song.energy - user.target_energy)
    energy_points = max(0.0, energy_similarity) * 1.5
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    acoustic_match = (
        user.likes_acoustic and song.acousticness >= 0.5
    ) or (
        not user.likes_acoustic and song.acousticness < 0.5
    )
    if acoustic_match:
        score += 0.75
        reasons.append("acoustic preference match (+0.75)")

    return score, reasons

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from CSV into dictionaries with numeric fields converted."""
    songs: List[Dict] = []
    int_fields = {"id"}
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}

    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            song: Dict = {}
            for key, value in row.items():
                if key in int_fields:
                    song[key] = int(value)
                elif key in float_fields:
                    song[key] = float(value)
                else:
                    song[key] = value
            songs.append(song)

    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song dictionary against the user's preferences."""
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs["genre"]:
        score += 2.0
        reasons.append("genre match (+2.0)")

    if song["mood"] == user_prefs["mood"]:
        score += 1.0
        reasons.append("mood match (+1.0)")

    target_energy = float(user_prefs["energy"])
    energy_similarity = 1 - abs(song["energy"] - target_energy)
    energy_points = max(0.0, energy_similarity) * 1.5
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        acoustic_match = (
            likes_acoustic and song["acousticness"] >= 0.5
        ) or (
            not likes_acoustic and song["acousticness"] < 0.5
        )
        if acoustic_match:
            score += 0.75
            reasons.append("acoustic preference match (+0.75)")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Return the top-k song dictionaries sorted by descending score."""
    scored_songs = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored_songs.append((song, score, explanation))

    ranked_songs = sorted(scored_songs, key=lambda item: item[1], reverse=True)
    return ranked_songs[:k]
