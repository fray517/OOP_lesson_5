"""Сохранение и загрузка рекордов (high score)."""

from __future__ import annotations

import json
import os
from typing import Optional


_HIGHSCORE_FILE = "highscore.json"


def _get_path() -> str:
    """Путь к файлу рекордов рядом с игрой."""
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, _HIGHSCORE_FILE)


def load_high_score() -> int:
    """Загрузить лучший результат из файла.

    Если файл отсутствует или повреждён — вернуть 0.
    """
    path = _get_path()
    if not os.path.exists(path):
        return 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0

    score = data.get("high_score", 0)
    if isinstance(score, int) and score >= 0:
        return score
    return 0


def save_high_score(score: int) -> None:
    """Сохранить лучший результат в файл.

    Ничего не делает при ошибке записи.
    """
    if score < 0:
        score = 0
    path = _get_path()
    data = {"high_score": int(score)}
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        return
