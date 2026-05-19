"""Daily orchestrator with two stages so CI can commit-and-push between them.

Subcommands:
  render          Pick a quote, render the reel, write to posts/ and state/_pending.json.
  publish         Read state/_pending.json, call Instagram Graph API, record to state/posted.json.
  all             Render + publish in one go (local testing).

Flags:
  --dry-run       (render mode) Skip writing the pending state file.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import config, image_renderer, instagram_poster, quote_loader, video_renderer

PENDING_FILE = config.STATE_DIR / "_pending.json"


def build_caption(quote: dict) -> str:
    parts = [
        f'"{quote["text"]}"',
        "",
        f'— {quote["author"]}',
    ]
    if config.IG_HANDLE:
        parts.extend(["", f"Follow {config.IG_HANDLE} for daily quotes."])
    parts.extend(["", config.HASHTAGS])
    return "\n".join(parts)


def render_step(dry_run: bool = False) -> dict:
    quote = quote_loader.pick_next_quote()
    base_image = quote_loader.pick_base_image()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    video_relpath = f"posts/{timestamp}-{quote['id']}.mp4"
    video_path = config.ROOT / video_relpath
    image_path = video_path.with_suffix(".jpg")

    print(f"[inkandexistence] quote:  {quote['id']} — {quote['author']}")
    print(f"[inkandexistence] base:   {base_image.name}")
    print(f"[inkandexistence] output: {video_path}")

    image_renderer.render_quote(
        base_image_path=base_image,
        quote_text=quote["text"],
        author=quote["author"],
        output_path=image_path,
        handle=config.IG_HANDLE or None,
    )
    video_renderer.render_reel(image_path=image_path, output_path=video_path)
    image_path.unlink(missing_ok=True)

    info = {
        "quote_id": quote["id"],
        "video_relpath": video_relpath,
        "caption": build_caption(quote),
        "rendered_at": datetime.now(timezone.utc).isoformat(),
    }

    if not dry_run:
        PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
        with PENDING_FILE.open("w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        print(f"[inkandexistence] pending state written to {PENDING_FILE}")
    return info


def publish_step(info: dict | None = None) -> str:
    if info is None:
        if not PENDING_FILE.exists():
            raise RuntimeError(
                f"No pending render found at {PENDING_FILE}. Run 'render' first."
            )
        with PENDING_FILE.open("r", encoding="utf-8") as f:
            info = json.load(f)

    config.assert_runtime_config()

    video_url = instagram_poster.public_media_url(info["video_relpath"])
    print(f"[inkandexistence] video url: {video_url}")

    media_id = instagram_poster.post(video_url=video_url, caption=info["caption"])
    print(f"[inkandexistence] published media id: {media_id}")

    quote_loader.record_post(
        quote_id=info["quote_id"],
        video_relpath=info["video_relpath"],
        ig_media_id=media_id,
    )

    if PENDING_FILE.exists():
        PENDING_FILE.unlink()
    return media_id


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Ink & Existence daily quote poster.")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="Render only.")
    r.add_argument("--dry-run", action="store_true")

    sub.add_parser("publish", help="Publish previously-rendered reel to Instagram.")
    sub.add_parser("all", help="Render and publish in one go.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.cmd == "render":
        render_step(dry_run=args.dry_run)
    elif args.cmd == "publish":
        publish_step()
    elif args.cmd == "all":
        info = render_step(dry_run=False)
        publish_step(info)
    return 0


if __name__ == "__main__":
    sys.exit(main())
