# ink & existence

Daily quote reels posted to Instagram automatically via GitHub Actions at 10 PM IST.

## How it works

1. **Render** — picks a random quote from `data/quotes.json`, overlays it on a random background image from `data/base_images/`, mixes in background music from `data/audio/`, and produces an MP4 reel in `posts/`.
2. **Commit** — the rendered video is committed so it's reachable at `raw.githubusercontent.com` (required by the Instagram API).
3. **Publish** — the reel is posted to Instagram as a Reel. Progress is logged to `state/posted.json`.

## Setup

### 1. Add your content

| Path | What to put there |
|---|---|
| `data/quotes.json` | Array of `{ "id", "text", "author" }` objects |
| `data/base_images/` | Background images (`.jpg` / `.png`, any resolution — they're center-cropped to 9:16) |
| `data/audio/` | Background music tracks (`.mp3` / `.m4a`) |

### 2. Download fonts

```bash
bash scripts/download_fonts.sh
```

### 3. Configure secrets & variables

In your GitHub repo → **Settings → Secrets and variables → Actions**:

**Secrets**

| Name | Value |
|---|---|
| `IG_LONG_LIVED_TOKEN` | Instagram long-lived access token |
| `IG_USER_ID` | Instagram user ID |
| `IG_APP_ID` | Instagram app ID |
| `IG_APP_SECRET` | Instagram app secret |

**Variables**

| Name | Value |
|---|---|
| `IG_HANDLE` | e.g. `@inkandexistence` |

### 4. Set `GITHUB_REPO`

The workflow passes `github.repository` automatically — no manual setup needed.

### Local testing

```bash
cp .env.example .env
# fill in .env
pip install -r requirements.txt
bash scripts/download_fonts.sh
python -m src.main all
```

Use `--dry-run` to render without writing state:

```bash
python -m src.main render --dry-run
```

## Quotes format

```json
[
  { "id": "q-001", "text": "The only way out is through.", "author": "Robert Frost" }
]
```

IDs must be unique. The poster cycles through all quotes before repeating.
