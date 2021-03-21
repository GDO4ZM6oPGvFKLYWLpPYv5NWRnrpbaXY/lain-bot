from __future__ import annotations
from typing import Callable

class Status:
    CURRENT = 'current'
    REPEATING = 'repeating'
    COMPLETED = 'completed'
    DROPPED = 'dropped'
    PAUSED = 'paused'
    PLANNING = 'planning'
    UNKNOWN = 'unknown'

class ChangeKind:
    PROGRESS = 'progress'
    STATUS = 'status'
    SCORE = 'score'

class Format(str):
    __slots__ = ['formatted_score', 'normalized_score']

def _format(tag: str, format_fn: Callable, normal_fn: Callable) -> Format:
    f = Format(tag)
    f.formatted_score = format_fn
    f.normalized_score = normal_fn
    return f

def emoji_fn(score):
    if score == 0:
        return '-'
    elif 0 < score < 1.5:
        return '🙁'
    elif 1.5 <= score < 2.5:
        return '😐'
    elif 2.5 <= score <= 3:
        return '🙂'
    else:
        return score

def emoji_normal(score):
    # normalization numbers from https://anilist.co/forum/thread/15758
    if score == 0:
        return None
    elif 0 < score < 1.5:
        return 35
    elif 1.5 <= score < 2.5:
        return 60
    elif 2.5 <= score <= 3:
        return 85
    else:
        return None

class ScoreFormat:
    _BASE               = _format('_base', lambda: 'XX', lambda: None)
    POINT_10            = _format('POINT_10', lambda score: f"{score if score else '-'}/10", lambda score: score*10)
    POINT_10_DECIMAL    = _format('POINT_10_DECIMAL', lambda score: f"{score if score else '-'}/10.0", lambda score: score*10)
    POINT_100           = _format('POINT_100', lambda score: f"{score if score else '-'}/100", lambda score: score)
    POINT_5             = _format('POINT_5', lambda score: f"{score if score else '-'}/5", lambda score: score*20)
    EMOJI               = _format('EMOJI', emoji_fn, emoji_normal)
    STAR                = _format('STAR', lambda score: f"{score}", lambda: None)

    def __new__(cls, score_format: str):
        if score_format == ScoreFormat.POINT_10:
            return ScoreFormat.POINT_10
        elif score_format == ScoreFormat.POINT_100:
            return ScoreFormat.POINT_100
        elif score_format == ScoreFormat.POINT_10_DECIMAL:
            return ScoreFormat.POINT_10_DECIMAL
        elif score_format == ScoreFormat.POINT_5:
            return ScoreFormat.POINT_5
        elif score_format == ScoreFormat.EMOJI:
            return ScoreFormat.EMOJI
        elif score_format == ScoreFormat.STAR:
            return ScoreFormat.STAR
        else:
            return ScoreFormat._BASE