"""Energy level calculation for tracks."""

from dataclasses import dataclass

import librosa
import numpy as np
from numpy.typing import NDArray


@dataclass
class EnergyResult:
    """Result of energy calculation."""

    energy: int  # 1-10 scale
    rms_db: float
    spectral_centroid_hz: float
    spectral_rolloff_hz: float
    raw_score: float


def calculate_energy(
    y: NDArray[np.floating],
    sr: int = 22050,
) -> EnergyResult:
    """Calculate energy level on 1-10 scale.

    Energy is computed from multiple audio features:
    - RMS (loudness/power)
    - Spectral centroid (brightness)
    - Spectral rolloff (frequency distribution)
    - Zero crossing rate (noisiness/percussiveness)

    Args:
        y: Audio time series (mono)
        sr: Sample rate

    Returns:
        EnergyResult with energy level and component features
    """
    # RMS energy (loudness)
    rms = librosa.feature.rms(y=y)[0]
    rms_mean = float(np.mean(rms))
    rms_db = float(librosa.amplitude_to_db([rms_mean])[0])

    # Spectral centroid (brightness - higher = more energy feel)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    centroid_mean = float(np.mean(spectral_centroid))

    # Spectral rolloff (frequency below which 85% of energy is contained)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)[0]
    rolloff_mean = float(np.mean(spectral_rolloff))

    # Zero crossing rate (percussiveness indicator)
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_mean = float(np.mean(zcr))

    # Normalize features to 0-1 range based on typical music values
    # RMS dB typically -60 to 0
    rms_norm = np.clip((rms_db + 60) / 60, 0, 1)

    # Spectral centroid typically 500-8000 Hz for music
    centroid_norm = np.clip((centroid_mean - 500) / 7500, 0, 1)

    # Rolloff typically 1000-15000 Hz
    rolloff_norm = np.clip((rolloff_mean - 1000) / 14000, 0, 1)

    # ZCR typically 0.02-0.15 for music
    zcr_norm = np.clip((zcr_mean - 0.02) / 0.13, 0, 1)

    # Weighted combination
    # RMS is most important, then spectral features
    raw_score = 0.4 * rms_norm + 0.25 * centroid_norm + 0.20 * rolloff_norm + 0.15 * zcr_norm

    # Convert to 1-10 scale
    energy = int(np.clip(raw_score * 9 + 1, 1, 10))

    return EnergyResult(
        energy=energy,
        rms_db=round(rms_db, 1),
        spectral_centroid_hz=round(centroid_mean, 1),
        spectral_rolloff_hz=round(rolloff_mean, 1),
        raw_score=round(float(raw_score), 3),
    )


def calculate_energy_from_file(
    file_path: str,
    *,
    duration: float | None = None,
    offset: float = 0.0,
) -> EnergyResult:
    """Calculate energy from audio file.

    Args:
        file_path: Path to audio file
        duration: Duration to analyze in seconds (None for full track)
        offset: Start offset in seconds

    Returns:
        EnergyResult with energy level
    """
    y, sr = librosa.load(file_path, duration=duration, offset=offset, mono=True)
    return calculate_energy(y, int(sr))
