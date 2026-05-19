"""Picks the next quote and base image, with usage tracking."""
from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path

from . import config


def load_quotes() -> list[dict]:
    with config.QUOTES_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_state() -> dict:
    if not config.POSTED_FILE.exists():
        return {"posted": []}
    with config.POSTED_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(state: dict) -> None:
    config.POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with config.POSTED_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def pick_next_quote() -> dict:
    """Pick a quote, preferring ones never posted; cycles fairly when all used."""
    quotes = load_quotes()
    if not quotes:
        raise RuntimeError("quotes.json is empty.")

    state = _load_state()
    posted = state.get("posted", [])
    used_ids = {p["quote_id"] for p in posted}
    last_used: dict[str, str] = {}
    for entry in posted:
        last_used[entry["quote_id"]] = entry.get("posted_at", "")

    unused = [q for q in quotes if q["id"] not in used_ids]
    if unused:
        return random.choice(unused)

    return sorted(quotes, key=lambda q: last_used.get(q["id"], ""))[0]


def pick_base_image() -> Path:
    candidates = [
        p
        for p in config.BASE_IMAGES_DIR.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        and not p.name.startswith("_")
    ]
    if not candidates:
        raise RuntimeError(
            f"No base images found in {config.BASE_IMAGES_DIR}. "
            "Drop at least one .jpg/.png in there."
        )
    return random.choice(candidates)


def record_post(quote_id: str, video_relpath: str, ig_media_id: str) -> None:
    state = _load_state()
    state.setdefault("posted", []).append(
        {
            "quote_id": quote_id,
            "video": video_relpath,
            "ig_media_id": ig_media_id,
            "posted_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    _save_state(state)
