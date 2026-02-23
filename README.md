🇺🇸 English | [🇷🇺 Русский](README.ru.md)

# YouTube Transcribe — OpenClaw Skill

Transcribes YouTube videos and generates a concise summary.

**Works on:** OpenClaw running on your own VPS/server.
**Does NOT work on:** cloud-hosted agents (Kimi Claw and similar) — YouTube blocks their IPs entirely, including subtitle requests.

---

## How It Works

1. Tries to fetch subtitles via `youtube-transcript-api` — free, no audio download needed
2. If no subtitles — downloads audio via `yt-dlp` and sends it to Groq Whisper Turbo

Output: summary via llama-3.3-70b + a markdown file with the full transcript.

---

## Requirements

- Python venv with dependencies installed
- Groq API key — free account at [groq.com](https://console.groq.com) gives 20 hours of transcription per day
- ffmpeg is not required

---

## Installation

```bash
pip install youtube-transcript-api groq yt-dlp

export GROQ_API_KEY=your_key_here

# Optional — if yt-dlp gets blocked on your IP:
export YTDLP_COOKIES=/path/to/cookies.txt
```

Copy into the skill directory:

```
skills/youtube-transcribe/
├── SKILL.md
├── README.md
└── transcribe.py
```

---

## Usage

```bash
GROQ_API_KEY=your_key python3 transcribe.py "https://youtube.com/watch?v=VIDEO_ID"

# Summary only
GROQ_API_KEY=your_key python3 transcribe.py "URL" --summary-only
```

Output is saved to `memory/knowledge/transcripts/YYYY-MM-DD-title.md`.

---

## Example Output

```
🎬 OpenClaw Setup with OpenRouter | Channel: ATOM | 4:07
✅ Subtitles fetched
✅ Saved: transcripts/2026-02-22-openclaw-setup.md

SUMMARY:
- Removing existing config via openclaw uninstall
- Reinstalling via openclaw onboard
- Selecting model and entering API key
- Connecting Telegram channel
```

---

## Cost

| Scenario | Price |
|---|---|
| Video with subtitles | $0 |
| 1 hour without subtitles (Groq Whisper) | ~$0.04 |
| Summary (llama-3.3-70b) | ~$0.0002 |

---

## Limitations

**IP blocking.** YouTube blocks requests (including subtitles) from IPs of major cloud providers. If you see `RequestBlocked` or `Sign in to confirm` — your IP is on the blocklist. Fix: cookies.txt (see below) or switch provider. On managed cloud (Kimi and similar) this cannot be resolved.

**Cookies to bypass IP blocking.** Only works if you have filesystem access to the agent's server:
1. Install the "Get cookies.txt LOCALLY" extension in Chrome/Firefox
2. Open youtube.com while logged in → export cookies.txt
3. Upload to the server, set `export YTDLP_COOKIES=/path/to/cookies.txt`

Refresh cookies every few months.

**File size.** The script uses `worstaudio` with a 24MB limit — Groq accepts up to 25MB. Videos longer than ~2.5 hours may not fit.

**ffmpeg not required.** yt-dlp downloads native formats (m4a/webm); no conversion needed.

---

## Triggers

```
транскрибируй видео / расшифруй ролик / сделай конспект / summarize youtube
```

---

Built for [OpenClaw](https://openclaw.ai).
