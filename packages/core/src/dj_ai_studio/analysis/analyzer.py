"""Main audio analyzer service."""

import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

import librosa
import numpy as np
from numpy.typing import NDArray

from dj_ai_studio.analysis.bpm import BPMResult, detect_bpm
from dj_ai_studio.analysis.energy import EnergyResult, calculate_energy
from dj_ai_studio.analysis.key import KeyResult, detect_key


@dataclass
class AnalysisResult:
    """Complete analysis result for a track."""

    bpm: BPMResult
    key: KeyResult
    energy: EnergyResult
    duration_seconds: float
    sample_rate: int


class AudioAnalyzer:
    """Service for analyzing audio tracks.

    Provides both sync and async interfaces for analyzing
    audio files or raw audio data.
    """

    def __init__(
        self,
        *,
        analysis_duration: float | None = 60.0,
        sample_rate: int = 22050,
    ) -> None:
        """Initialize analyzer.

        Args:
            analysis_duration: Duration in seconds to analyze (None for full track)
            sample_rate: Target sample rate for analysis
        """
        self.analysis_duration = analysis_duration
        self.sample_rate = sample_rate

    def analyze_file(self, file_path: str | Path) -> AnalysisResult:
        """Analyze audio file synchronously.

        Args:
            file_path: Path to audio file (mp3, flac, wav, etc.)

        Returns:
            Complete analysis result
        """
        y, sr = librosa.load(
            str(file_path),
            sr=self.sample_rate,
            duration=self.analysis_duration,
            mono=True,
        )
        return self._analyze_signal(y, sr)

    def analyze_bytes(
        self,
        audio_data: bytes,
        file_format: str = "mp3",
    ) -> AnalysisResult:
        """Analyze audio from bytes.

        Args:
            audio_data: Raw audio file bytes
            file_format: File format extension (mp3, flac, etc.)

        Returns:
            Complete analysis result
        """
        with tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=True) as f:
            f.write(audio_data)
            f.flush()
            return self.analyze_file(f.name)

    def analyze_stream(
        self,
        stream: BinaryIO,
        file_format: str = "mp3",
    ) -> AnalysisResult:
        """Analyze audio from file-like object.

        Args:
            stream: File-like object with audio data
            file_format: File format extension

        Returns:
            Complete analysis result
        """
        return self.analyze_bytes(stream.read(), file_format)

    async def analyze_file_async(self, file_path: str | Path) -> AnalysisResult:
        """Analyze audio file asynchronously.

        Runs analysis in thread pool to avoid blocking.

        Args:
            file_path: Path to audio file

        Returns:
            Complete analysis result
        """
        return await asyncio.to_thread(self.analyze_file, file_path)

    async def analyze_bytes_async(
        self,
        audio_data: bytes,
        file_format: str = "mp3",
    ) -> AnalysisResult:
        """Analyze audio bytes asynchronously.

        Args:
            audio_data: Raw audio file bytes
            file_format: File format extension

        Returns:
            Complete analysis result
        """
        return await asyncio.to_thread(self.analyze_bytes, audio_data, file_format)

    def _analyze_signal(
        self,
        y: NDArray[np.floating],
        sr: int,
    ) -> AnalysisResult:
        """Analyze audio signal.

        Args:
            y: Audio time series (mono)
            sr: Sample rate

        Returns:
            Complete analysis result
        """
        duration = float(len(y) / sr)

        bpm_result = detect_bpm(y, sr)
        key_result = detect_key(y, sr)
        energy_result = calculate_energy(y, sr)

        return AnalysisResult(
            bpm=bpm_result,
            key=key_result,
            energy=energy_result,
            duration_seconds=round(duration, 2),
            sample_rate=sr,
        )
