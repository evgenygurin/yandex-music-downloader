"""BPM (tempo) detection using librosa."""

from dataclasses import dataclass

import librosa
import numpy as np
from numpy.typing import NDArray


@dataclass
class BPMResult:
    """Result of BPM detection."""

    bpm: float
    confidence: float
    beat_frames: NDArray[np.intp]


def detect_bpm(
    y: NDArray[np.floating],
    sr: int = 22050,
    *,
    start_bpm: float = 120.0,
    std_bpm: float = 1.0,
) -> BPMResult:
    """Detect BPM (tempo) from audio signal.

    Uses librosa's beat tracking with dynamic programming
    for robust tempo estimation.

    Args:
        y: Audio time series (mono)
        sr: Sample rate
        start_bpm: Initial tempo estimate for beat tracker
        std_bpm: Standard deviation for tempo prior

    Returns:
        BPMResult with detected BPM, confidence, and beat frames
    """
    # Get tempo and beat frames
    tempo, beat_frames = librosa.beat.beat_track(
        y=y,
        sr=sr,
        start_bpm=start_bpm,
        units="frames",
    )

    # Handle numpy array return (librosa >= 0.10)
    if isinstance(tempo, np.ndarray):
        tempo = float(tempo[0]) if len(tempo) > 0 else start_bpm

    # Calculate confidence based on beat consistency
    if len(beat_frames) > 1:
        # Get inter-beat intervals
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        intervals = np.diff(beat_times)

        # Expected interval from detected tempo
        expected_interval = 60.0 / tempo

        # Confidence = how consistent beats are with detected tempo
        interval_deviations = np.abs(intervals - expected_interval) / expected_interval
        confidence = float(1.0 - np.clip(np.mean(interval_deviations), 0, 1))
    else:
        confidence = 0.0

    return BPMResult(
        bpm=round(float(tempo), 1),
        confidence=round(confidence, 2),
        beat_frames=beat_frames,
    )


def detect_bpm_from_file(
    file_path: str,
    *,
    duration: float | None = 60.0,
    offset: float = 0.0,
) -> BPMResult:
    """Detect BPM from audio file.

    Args:
        file_path: Path to audio file
        duration: Duration to analyze in seconds (None for full track)
        offset: Start offset in seconds

    Returns:
        BPMResult with detected tempo
    """
    y, sr = librosa.load(file_path, duration=duration, offset=offset, mono=True)
    return detect_bpm(y, int(sr))
