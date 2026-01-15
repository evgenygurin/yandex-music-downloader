"""Tests for audio analysis module."""

from unittest.mock import patch

import numpy as np
import pytest


class TestBPMDetection:
    """Tests for BPM detection."""

    @pytest.fixture
    def mock_audio(self):
        """Create mock audio signal."""
        # 1 second of audio at 22050 Hz
        return np.random.randn(22050).astype(np.float32)

    @patch("librosa.beat.beat_track")
    @patch("librosa.frames_to_time")
    def test_detect_bpm_returns_result(self, mock_frames_to_time, mock_beat_track, mock_audio):
        """detect_bpm returns BPMResult with expected fields."""
        from dj_ai_studio.analysis.bpm import detect_bpm

        mock_beat_track.return_value = (np.array([128.0]), np.array([0, 22, 44, 66]))
        mock_frames_to_time.return_value = np.array([0.0, 0.5, 1.0, 1.5])

        result = detect_bpm(mock_audio, 22050)

        assert result.bpm == 128.0
        assert 0 <= result.confidence <= 1
        assert len(result.beat_frames) == 4

    @patch("librosa.beat.beat_track")
    @patch("librosa.frames_to_time")
    def test_detect_bpm_low_confidence_few_beats(
        self, mock_frames_to_time, mock_beat_track, mock_audio
    ):
        """Low confidence when few beats detected."""
        from dj_ai_studio.analysis.bpm import detect_bpm

        mock_beat_track.return_value = (np.array([120.0]), np.array([0]))
        mock_frames_to_time.return_value = np.array([0.0])

        result = detect_bpm(mock_audio, 22050)

        assert result.bpm == 120.0
        assert result.confidence == 0.0


class TestKeyDetection:
    """Tests for key detection."""

    @pytest.fixture
    def mock_audio(self):
        """Create mock audio signal."""
        return np.random.randn(22050).astype(np.float32)

    @patch("librosa.feature.chroma_cqt")
    def test_detect_key_returns_result(self, mock_chroma, mock_audio):
        """detect_key returns KeyResult with expected fields."""
        from dj_ai_studio.analysis.key import detect_key

        # Mock chroma with strong C major signal
        chroma = np.zeros((12, 10))
        chroma[0, :] = 1.0  # Strong C
        chroma[4, :] = 0.8  # Strong E
        chroma[7, :] = 0.8  # Strong G
        mock_chroma.return_value = chroma

        result = detect_key(mock_audio, 22050)

        assert result.key in ["C", "Am"]  # C major or relative minor
        assert result.camelot in ["8B", "8A"]
        assert isinstance(result.is_minor, bool)
        assert 0 <= result.confidence <= 1

    @patch("librosa.feature.chroma_cqt")
    def test_detect_key_minor(self, mock_chroma, mock_audio):
        """detect_key detects minor keys."""
        from dj_ai_studio.analysis.key import detect_key

        # Mock chroma with strong A minor signal
        chroma = np.zeros((12, 10))
        chroma[9, :] = 1.0  # Strong A
        chroma[0, :] = 0.8  # Strong C
        chroma[4, :] = 0.7  # Strong E
        mock_chroma.return_value = chroma

        result = detect_key(mock_audio, 22050)

        # Should detect A minor or C major (relative keys)
        assert result.key in ["Am", "C", "A", "Cm"]


class TestEnergyCalculation:
    """Tests for energy calculation."""

    @pytest.fixture
    def mock_audio(self):
        """Create mock audio signal."""
        return np.random.randn(22050).astype(np.float32)

    @patch("librosa.feature.rms")
    @patch("librosa.feature.spectral_centroid")
    @patch("librosa.feature.spectral_rolloff")
    @patch("librosa.feature.zero_crossing_rate")
    @patch("librosa.amplitude_to_db")
    def test_calculate_energy_returns_result(
        self,
        mock_db,
        mock_zcr,
        mock_rolloff,
        mock_centroid,
        mock_rms,
        mock_audio,
    ):
        """calculate_energy returns EnergyResult with expected fields."""
        from dj_ai_studio.analysis.energy import calculate_energy

        mock_rms.return_value = np.array([[0.1]])
        mock_db.return_value = np.array([-20.0])
        mock_centroid.return_value = np.array([[3000.0]])
        mock_rolloff.return_value = np.array([[8000.0]])
        mock_zcr.return_value = np.array([[0.05]])

        result = calculate_energy(mock_audio, 22050)

        assert 1 <= result.energy <= 10
        assert isinstance(result.rms_db, float)
        assert isinstance(result.spectral_centroid_hz, float)
        assert isinstance(result.spectral_rolloff_hz, float)

    @patch("librosa.feature.rms")
    @patch("librosa.feature.spectral_centroid")
    @patch("librosa.feature.spectral_rolloff")
    @patch("librosa.feature.zero_crossing_rate")
    @patch("librosa.amplitude_to_db")
    def test_calculate_energy_high_energy(
        self,
        mock_db,
        mock_zcr,
        mock_rolloff,
        mock_centroid,
        mock_rms,
        mock_audio,
    ):
        """High RMS and spectral features produce high energy."""
        from dj_ai_studio.analysis.energy import calculate_energy

        mock_rms.return_value = np.array([[0.5]])
        mock_db.return_value = np.array([-6.0])  # Loud
        mock_centroid.return_value = np.array([[6000.0]])  # Bright
        mock_rolloff.return_value = np.array([[12000.0]])  # Wide spectrum
        mock_zcr.return_value = np.array([[0.1]])  # Percussive

        result = calculate_energy(mock_audio, 22050)

        assert result.energy >= 7

    @patch("librosa.feature.rms")
    @patch("librosa.feature.spectral_centroid")
    @patch("librosa.feature.spectral_rolloff")
    @patch("librosa.feature.zero_crossing_rate")
    @patch("librosa.amplitude_to_db")
    def test_calculate_energy_low_energy(
        self,
        mock_db,
        mock_zcr,
        mock_rolloff,
        mock_centroid,
        mock_rms,
        mock_audio,
    ):
        """Low RMS and spectral features produce low energy."""
        from dj_ai_studio.analysis.energy import calculate_energy

        mock_rms.return_value = np.array([[0.01]])
        mock_db.return_value = np.array([-50.0])  # Quiet
        mock_centroid.return_value = np.array([[800.0]])  # Dark
        mock_rolloff.return_value = np.array([[2000.0]])  # Narrow spectrum
        mock_zcr.return_value = np.array([[0.02]])  # Smooth

        result = calculate_energy(mock_audio, 22050)

        assert result.energy <= 3


class TestAudioAnalyzer:
    """Tests for AudioAnalyzer service."""

    @patch("dj_ai_studio.analysis.analyzer.librosa.load")
    @patch("dj_ai_studio.analysis.analyzer.detect_bpm")
    @patch("dj_ai_studio.analysis.analyzer.detect_key")
    @patch("dj_ai_studio.analysis.analyzer.calculate_energy")
    def test_analyze_file(
        self,
        mock_energy,
        mock_key,
        mock_bpm,
        mock_load,
    ):
        """analyze_file returns complete AnalysisResult."""
        from dj_ai_studio.analysis.analyzer import AudioAnalyzer
        from dj_ai_studio.analysis.bpm import BPMResult
        from dj_ai_studio.analysis.energy import EnergyResult
        from dj_ai_studio.analysis.key import KeyResult

        mock_load.return_value = (np.zeros(22050), 22050)
        mock_bpm.return_value = BPMResult(bpm=128.0, confidence=0.9, beat_frames=np.array([]))
        mock_key.return_value = KeyResult(
            key="Am", camelot="8A", is_minor=True, confidence=0.8, all_correlations={}
        )
        mock_energy.return_value = EnergyResult(
            energy=7,
            rms_db=-15.0,
            spectral_centroid_hz=3000,
            spectral_rolloff_hz=8000,
            raw_score=0.7,
        )

        analyzer = AudioAnalyzer()
        result = analyzer.analyze_file("/fake/path.mp3")

        assert result.bpm.bpm == 128.0
        assert result.key.key == "Am"
        assert result.energy.energy == 7
        assert result.duration_seconds == 1.0
