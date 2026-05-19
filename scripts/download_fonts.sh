#!/usr/bin/env bash
# Downloads fonts used by the renderer (SIL OFL / Apache 2.0 licensed).
# - Playfair Display Italic — for the quote text
# - Lato Regular — for author attribution and handle

set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)/fonts"
mkdir -p "$DIR"

download() {
  local url="$1"
  local out="$2"
  if [[ -f "$out" ]]; then
    echo "[fonts] already have $(basename "$out")"
    return 0
  fi
  echo "[fonts] downloading $(basename "$out")"
  curl -fsSL "$url" -o "$out"
}

download \
  "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf" \
  "$DIR/PlayfairDisplay-Italic.ttf"

download \
  "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Regular.ttf" \
  "$DIR/Lato-Regular.ttf"

echo "[fonts] done."
