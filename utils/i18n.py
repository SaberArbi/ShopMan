"""Translation system with RTL + Arabic-shaping helpers.

All user-facing strings live in `locales/<lang>.json`. Screens must call
`t("some.key")` and never hard-code text.
"""
import json
import os
from pathlib import Path

try:
    import arabic_reshaper
    from bidi.algorithm import get_display as _bidi_display
    _HAS_ARABIC_SHAPING = True
except ImportError:
    _HAS_ARABIC_SHAPING = False
    _bidi_display = None
    arabic_reshaper = None


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
_LOCALES_DIR = _ROOT / "locales"
CONFIG_FILE = _ROOT / "settings.json"

LANGUAGES = {
    "en": "English",
    "fr": "Français",
    "ar": "العربية",
}
RTL_LANGUAGES = {"ar"}

_current = "fr"
_CACHE: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# RTL / layout helpers — used by every screen
# ---------------------------------------------------------------------------
def is_rtl() -> bool:
    return _current in RTL_LANGUAGES

def side_start() -> str:  return "right" if is_rtl() else "left"
def side_end()   -> str:  return "left"  if is_rtl() else "right"
def anchor_start() -> str: return "e" if is_rtl() else "w"
def anchor_end()   -> str: return "w" if is_rtl() else "e"
def justify_text() -> str: return "right" if is_rtl() else "left"


# ---------------------------------------------------------------------------
# Font selection
# ---------------------------------------------------------------------------
_ARABIC_FONTS = (
    "Noto Naskh Arabic", "Noto Sans Arabic", "Noto Sans",
    "DejaVu Sans", "FreeSans", "Tahoma", "Segoe UI",
    "Geeza Pro", "Arial Unicode MS", "Arial",
)
_LATIN_FONTS = ("Helvetica", "DejaVu Sans", "Arial")


def _pick_font(candidates):
    try:
        import tkinter.font as tkfont
        available = set(tkfont.families())
    except Exception:
        return candidates[0] if candidates else "TkDefaultFont"
    for family in candidates:
        if family in available:
            return family
    return candidates[-1] if candidates else "TkDefaultFont"


def ui_font(size: int, weight: str = "normal"):
    family = _pick_font(_ARABIC_FONTS if is_rtl() else _LATIN_FONTS)
    return (family, size, weight) if weight != "normal" else (family, size)


# ---------------------------------------------------------------------------
# Arabic shaping / bidi
# ---------------------------------------------------------------------------
def _has_arabic(text: str) -> bool:
    for ch in text:
        if ("\u0600" <= ch <= "\u06FF" or "\u0750" <= ch <= "\u077F" or
                "\uFB50" <= ch <= "\uFDFF" or "\uFE70" <= ch <= "\uFEFF"):
            return True
    return False


def rtl_display(text):
    """Visual-order, pre-shaped string for Tk on Linux. No-op elsewhere."""
    if not text or not isinstance(text, str):
        return text
    if not _HAS_ARABIC_SHAPING or not _has_arabic(text):
        return text
    try:
        return _bidi_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


# ---------------------------------------------------------------------------
# Config load / save
# ---------------------------------------------------------------------------
def _load_config() -> None:
    global _current
    if not CONFIG_FILE.exists():
        return
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lang = json.load(f).get("language", "fr")
            if lang in LANGUAGES:
                _current = lang
    except Exception:
        pass


def save_config(lang: str) -> None:
    global _current
    if lang not in LANGUAGES:
        return
    _current = lang
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"language": lang}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_language() -> str:
    return _current


def set_language(lang: str) -> None:
    save_config(lang)


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------
def _load(lang: str) -> dict:
    if lang not in _CACHE:
        path = _LOCALES_DIR / f"{lang}.json"
        try:
            with open(path, encoding="utf-8") as f:
                _CACHE[lang] = json.load(f)
        except Exception:
            _CACHE[lang] = {}
    return _CACHE[lang]


def t(key: str, **kwargs) -> str:
    """Translate `key`, format with kwargs, apply RTL shaping."""
    text = _load(_current).get(key)
    if text is None:
        text = _load("en").get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return rtl_display(text)


_load_config()