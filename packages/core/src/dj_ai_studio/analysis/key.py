"""Musical key detection using chroma features."""

from dataclasses import dataclass

import librosa
import numpy as np
from numpy.typing import NDArray

# Krumhansl-Schmuckler key profiles
# Major key profile (C major as reference)
MAJOR_PROFILE = np.array(
    [
        6.35,
        2.23,
        3.48,
        2.33,
        4.38,
        4.09,
        2.52,
        5.19,
        2.39,
        3.66,
        2.29,
        2.88,
    ]
)

# Minor key profile (C minor as reference)
MINOR_PROFILE = np.array(
    [
        6.33,
        2.68,
        3.52,
        5.38,
        2.60,
        3.53,
        2.54,
        4.75,
        3.98,
        2.69,
        3.34,
        3.17,
    ]
)

# Note names for key output
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Camelot wheel mapping
CAMELOT_MAJOR = {
    0: "8B",  # C
    1: "3B",  # C#/Db
    2: "10B",  # D
    3: "5B",  # D#/Eb
    4: "12B",  # E
    5: "7B",  # F
    6: "2B",  # F#/Gb
    7: "9B",  # G
    8: "4B",  # G#/Ab
    9: "11B",  # A
    10: "6B",  # A#/Bb
    11: "1B",  # B
}

CAMELOT_MINOR = {
    0: "5A",  # Cm
    1: "12A",  # C#m
    2: "7A",  # Dm
    3: "2A",  # D#m
    4: "9A",  # Em
    5: "4A",  # Fm
    6: "11A",  # F#m
    7: "6A",  # Gm
    8: "1A",  # G#m
    9: "8A",  # Am
    10: "3A",  # A#m
    11: "10A",  # Bm
}


@dataclass
class KeyResult:
    """Result of key detection."""

    key: str
    camelot: str
    is_minor: bool
    confidence: float
    all_correlations: dict[str, float]


def detect_key(
    y: NDArray[np.floating],
    sr: int = 22050,
) -> KeyResult:
    """Detect musical key using Krumhansl-Schmuckler algorithm.

    Computes chroma features and correlates with major/minor
    key profiles to find best matching key.

    Args:
        y: Audio time series (mono)
        sr: Sample rate

    Returns:
        KeyResult with detected key, Camelot notation, and confidence
    """
    # Compute chroma features (12 pitch classes)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    # Average chroma over time to get pitch class distribution
    chroma_avg = np.mean(chroma, axis=1)

    # Normalize
    chroma_avg = chroma_avg / (np.linalg.norm(chroma_avg) + 1e-6)

    # Correlate with all major and minor keys
    correlations: dict[str, float] = {}

    best_correlation = -1.0
    best_key = "C"
    best_is_minor = False
    best_pitch_class = 0

    for pitch_class in range(12):
        # Rotate profiles to match each key
        major_rotated = np.roll(MAJOR_PROFILE, pitch_class)
        minor_rotated = np.roll(MINOR_PROFILE, pitch_class)

        # Normalize profiles
        major_norm = major_rotated / np.linalg.norm(major_rotated)
        minor_norm = minor_rotated / np.linalg.norm(minor_rotated)

        # Compute correlations
        major_corr = float(np.dot(chroma_avg, major_norm))
        minor_corr = float(np.dot(chroma_avg, minor_norm))

        note = NOTE_NAMES[pitch_class]
        correlations[note] = major_corr
        correlations[f"{note}m"] = minor_corr

        if major_corr > best_correlation:
            best_correlation = major_corr
            best_key = note
            best_is_minor = False
            best_pitch_class = pitch_class

        if minor_corr > best_correlation:
            best_correlation = minor_corr
            best_key = f"{note}m"
            best_is_minor = True
            best_pitch_class = pitch_class

    # Get Camelot notation
    if best_is_minor:
        camelot = CAMELOT_MINOR[best_pitch_class]
    else:
        camelot = CAMELOT_MAJOR[best_pitch_class]

    # Confidence based on how much better the best match is
    sorted_corrs = sorted(correlations.values(), reverse=True)
    if len(sorted_corrs) >= 2:
        confidence = (sorted_corrs[0] - sorted_corrs[1]) / (sorted_corrs[0] + 1e-6)
        confidence = min(1.0, max(0.0, confidence * 2))  # Scale to 0-1
    else:
        confidence = 0.0

    return KeyResult(
        key=best_key,
        camelot=camelot,
        is_minor=best_is_minor,
        confidence=round(confidence, 2),
        all_correlations=correlations,
    )


def detect_key_from_file(
    file_path: str,
    *,
    duration: float | None = 60.0,
    offset: float = 0.0,
) -> KeyResult:
    """Detect key from audio file.

    Args:
        file_path: Path to audio file
        duration: Duration to analyze in seconds (None for full track)
        offset: Start offset in seconds

    Returns:
        KeyResult with detected key
    """
    y, sr = librosa.load(file_path, duration=duration, offset=offset, mono=True)
    return detect_key(y, sr)
