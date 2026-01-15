#!/usr/bin/env python3
"""
Key Detection используя librosa chroma features
Алгоритм Krumhansl-Schmuckler для определения тональности
"""

import librosa
import numpy as np

# Krumhansl-Schmuckler key profiles
# Профили для major и minor тональностей (корреляционные веса)
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

# Mapping chroma index to note names
CHROMA_NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Camelot Wheel mapping
CAMELOT_WHEEL = {
    "C": "8B",
    "Cm": "5A",
    "C#": "3B",
    "C#m": "12A",
    "D": "10B",
    "Dm": "7A",
    "D#": "5B",
    "D#m": "2A",
    "E": "12B",
    "Em": "9A",
    "F": "7B",
    "Fm": "4A",
    "F#": "2B",
    "F#m": "11A",
    "G": "9B",
    "Gm": "6A",
    "G#": "4B",
    "G#m": "1A",
    "A": "11B",
    "Am": "8A",
    "A#": "6B",
    "A#m": "3A",
    "B": "1B",
    "Bm": "10A",
}


def detect_key(audio_path, duration=180):
    """
    Определение тональности трека

    Args:
        audio_path: путь к аудиофайлу
        duration: длительность анализа в секундах (180 = 3 минуты)

    Returns:
        tuple: (key, camelot, confidence)
            - key: тональность (например 'Cm', 'G')
            - camelot: Camelot код (например '5A', '9B')
            - confidence: уверенность 0-1
    """
    try:
        # Загрузка аудио
        y, sr = librosa.load(audio_path, duration=duration)

        # Извлечение chroma features (12-мерный вектор энергии питчей)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

        # Усреднение по времени для получения общего профиля
        chroma_mean = np.mean(chroma, axis=1)

        # Нормализация
        chroma_mean = chroma_mean / np.sum(chroma_mean)

        # Корреляция с каждым ключом (24 варианта: 12 major + 12 minor)
        correlations = []

        for i in range(12):  # 12 тональностей
            # Rotate profile для каждого ключа
            rotated_major = np.roll(MAJOR_PROFILE, i)
            rotated_minor = np.roll(MINOR_PROFILE, i)

            # Нормализация профилей
            rotated_major = rotated_major / np.sum(rotated_major)
            rotated_minor = rotated_minor / np.sum(rotated_minor)

            # Корреляция Пирсона
            corr_major = np.corrcoef(chroma_mean, rotated_major)[0, 1]
            corr_minor = np.corrcoef(chroma_mean, rotated_minor)[0, 1]

            correlations.append(
                {"note": CHROMA_NOTES[i], "scale": "major", "correlation": corr_major}
            )
            correlations.append(
                {"note": CHROMA_NOTES[i], "scale": "minor", "correlation": corr_minor}
            )

        # Сортировка по корреляции
        correlations.sort(key=lambda x: x["correlation"], reverse=True)

        # Лучший результат
        best = correlations[0]
        note = best["note"]
        scale = best["scale"]
        confidence = best["correlation"]

        # Форматирование ключа
        if scale == "minor":
            key = f"{note}m"
        else:
            key = note

        # Camelot код
        camelot = CAMELOT_WHEEL.get(key, "Unknown")

        return key, camelot, round(confidence, 2)

    except Exception as e:
        print(f"Error detecting key: {e}")
        return None, None, None


def detect_key_simple(audio_path):
    """Упрощенная версия для быстрого вызова"""
    return detect_key(audio_path, duration=180)


if __name__ == "__main__":
    # Тест на одном треке
    import sys

    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        key, camelot, conf = detect_key(audio_file)
        print(f"Key: {key} ({camelot}) - Confidence: {conf}")
