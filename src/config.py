"""Centralized configuration. Loads from environment / .env file."""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# --- Paths ---------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
BASE_IMAGES_DIR = DATA_DIR / "base_images"
AUDIO_DIR = DATA_DIR / "audio"
QUOTES_FILE = DATA_DIR / "quotes.json"
FONTS_DIR = ROOT / "fonts"
STATE_DIR = ROOT / "state"
POSTED_FILE = STATE_DIR / "posted.json"
POSTS_DIR = ROOT / "posts"


# --- Fonts ---------------------------------------------------------------
FONT_QUOTE = FONTS_DIR / "PlayfairDisplay-Italic.ttf"
FONT_AUTHOR = FONTS_DIR / "Lato-Regular.ttf"
FONT_HANDLE = FONTS_DIR / "Lato-Regular.ttf"


# --- Image / video render settings --------------------------------------
IMG_WIDTH = 1080
IMG_HEIGHT = 1920
REEL_DURATION = 30  # seconds

# Text panel overlay
OVERLAY_COLOR = (15, 15, 15)       # near-black
OVERLAY_OPACITY = 155              # 0-255
TEXT_PANEL_PADDING = 64
TEXT_PANEL_CORNER_RADIUS = 32

QUOTE_FONT_SIZE = 58
AUTHOR_FONT_SIZE = 34
HANDLE_FONT_SIZE = 28

TEXT_COLOR = (255, 252, 245)       # warm white for quote
AUTHOR_COLOR = (210, 200, 185)     # muted warm for author
HANDLE_COLOR = (180, 170, 158)

SIDE_PADDING = 90
LINE_SPACING_QUOTE = 16
GAP_QUOTE_AUTHOR = 52              # space between quote and "— Author"


# --- Instagram API -------------------------------------------------------
IG_LONG_LIVED_TOKEN = os.getenv("IG_LONG_LIVED_TOKEN", "")
IG_USER_ID = os.getenv("IG_USER_ID", "")
IG_APP_ID = os.getenv("IG_APP_ID", "")
IG_APP_SECRET = os.getenv("IG_APP_SECRET", "")
IG_API_VERSION = os.getenv("IG_API_VERSION", "v22.0")
IG_API_HOST = "https://graph.instagram.com"


# --- GitHub (for hosting the rendered video) ----------------------------
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
IG_HANDLE = os.getenv("IG_HANDLE", "")


# --- Caption template ---------------------------------------------------
HASHTAGS = (
    "#quotes #dailyquote #motivation #wisdom #mindset #inspiration "
    "#quoteoftheday #wordsofwisdom #philosophy #life #inkandexistence"
)


def assert_runtime_config() -> None:
    missing = [
        name
        for name, value in [
            ("IG_LONG_LIVED_TOKEN", IG_LONG_LIVED_TOKEN),
            ("IG_USER_ID", IG_USER_ID),
            ("GITHUB_REPO", GITHUB_REPO),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "See .env.example."
        )
