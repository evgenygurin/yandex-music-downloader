"""Audio analysis module for DJ AI Studio."""

from dj_ai_studio.analysis.analyzer import AnalysisResult, AudioAnalyzer
from dj_ai_studio.analysis.bpm import detect_bpm
from dj_ai_studio.analysis.energy import calculate_energy
from dj_ai_studio.analysis.key import detect_key

__all__ = [
    "AudioAnalyzer",
    "AnalysisResult",
    "detect_bpm",
    "detect_key",
    "calculate_energy",
]
