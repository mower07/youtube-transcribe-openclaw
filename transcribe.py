#!/usr/bin/env python3
"""
YouTube Transcribe — скилл для транскрибации YouTube видео.
Стратегия:
  1. Пробует получить субтитры через youtube-transcript-api (бесплатно)
  2. Если нет — скачивает аудио через yt-dlp и транскрибирует через Groq Whisper
"""

import sys
import os
import re
import json
import tempfile
from pathlib import Path
from datetime import datetime

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
VENV_PYTHON = os.path.expanduser("~/.agent-venv/bin/python3")
YTDLP_BIN = os.path.expanduser("~/.agent-venv/bin/yt-dlp")


def extract_video_id(url: str) -> str:
    """Извлечь video ID из YouTube URL."""
    patterns = [
        r"(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    raise ValueError(f"Не могу извлечь video ID из: {url}")


def get_subtitles(video_id: str, languages: list = None) -> str | None:
    """Попробовать получить субтитры через youtube-transcript-api."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        if languages is None:
            languages = ["ru", "en"]
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=languages)
        return " ".join([t.text for t in transcript])
    except Exception as e:
        print(f"  [subtitle] Нет субтитров: {e}", file=sys.stderr)
        return None


def get_video_info(url: str) -> dict:
    """Получить метаданные видео."""
    import subprocess
    result = subprocess.run(
        [YTDLP_BIN, "--dump-json", "--no-playlist", url],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return {
            "title": data.get("title", "Unknown"),
            "duration": data.get("duration", 0),
            "channel": data.get("uploader", "Unknown"),
            "upload_date": data.get("upload_date", ""),
        }
    return {}


def download_audio(url: str, output_dir: str) -> str:
    """Скачать аудио через yt-dlp (без ffmpeg)."""
    import subprocess
    output_template = os.path.join(output_dir, "audio.%(ext)s")
    result = subprocess.run(
        [
            YTDLP_BIN,
            "-f", "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
            "-o", output_template,
            "--no-playlist",
            url,
        ],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp error: {result.stderr[:500]}")
    
    # Find the downloaded file
    for ext in ["m4a", "webm", "ogg", "opus", "mp3", "wav"]:
        candidate = os.path.join(output_dir, f"audio.{ext}")
        if os.path.exists(candidate):
            return candidate
    raise RuntimeError("Аудио файл не найден после скачивания")


def transcribe_with_groq(audio_path: str, language: str = None) -> str:
    """Транскрибировать аудио через Groq Whisper."""
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    
    file_size = os.path.getsize(audio_path)
    print(f"  [groq] Файл: {Path(audio_path).name}, размер: {file_size // 1024}KB", file=sys.stderr)
    
    # Groq limit: 25MB
    if file_size > 25 * 1024 * 1024:
        raise RuntimeError(f"Файл слишком большой ({file_size // 1024 // 1024}MB). Groq принимает до 25MB.")
    
    kwargs = {
        "file": (Path(audio_path).name, open(audio_path, "rb")),
        "model": "whisper-large-v3-turbo",
        "response_format": "text",
    }
    if language:
        kwargs["language"] = language
    
    result = client.audio.transcriptions.create(**kwargs)
    return result if isinstance(result, str) else result.text


def summarize(text: str, title: str = "") -> str:
    """Сделать краткое саммари через Groq (llama)."""
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""Сделай краткое резюме этой транскрипции видео. 
Заголовок: {title}

Транскрипция (первые 8000 символов):
{text[:8000]}

Формат:
- 3-5 предложений: основная суть
- 5-7 ключевых тезисов (через дефис)
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
    )
    return response.choices[0].message.content


def save_result(video_id: str, info: dict, transcript: str, summary: str, method: str) -> str:
    """Сохранить результат в memory/knowledge."""
    output_dir = Path.home() / ".openclaw/workspace/memory/knowledge/transcripts"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    title_slug = re.sub(r"[^\w\s-]", "", info.get("title", video_id))[:50].strip().replace(" ", "-").lower()
    filename = f"{date_str}-{title_slug}.md"
    filepath = output_dir / filename
    
    content = f"""# {info.get('title', video_id)}

**Канал:** {info.get('channel', '?')}  
**Video ID:** {video_id}  
**Дата:** {date_str}  
**Метод транскрипции:** {method}  
**URL:** https://youtu.be/{video_id}

---

## Саммари

{summary}

---

## Полный транскрипт

{transcript}
"""
    filepath.write_text(content, encoding="utf-8")
    return str(filepath)


def main():
    if len(sys.argv) < 2:
        print("Использование: python3 transcribe.py <youtube_url> [--summary-only]")
        sys.exit(1)
    
    url = sys.argv[1]
    summary_only = "--summary-only" in sys.argv
    
    print(f"\n🎬 Транскрибация: {url}")
    
    # Get video info
    print("  Получаю метаданные...")
    info = get_video_info(url)
    if info:
        print(f"  Название: {info['title']}")
        print(f"  Канал: {info['channel']}")
        duration = info.get('duration', 0)
        print(f"  Длительность: {duration // 60}:{duration % 60:02d}")
    
    video_id = extract_video_id(url)
    transcript = None
    method = ""
    
    # Strategy 1: Try subtitles
    print("\n📋 Пробую субтитры YouTube...")
    transcript = get_subtitles(video_id)
    if transcript:
        method = "YouTube субтитры (бесплатно)"
        print("  ✅ Субтитры получены")
    else:
        # Strategy 2: Download + Groq
        print("\n🎵 Скачиваю аудио для транскрипции через Groq...")
        if not GROQ_API_KEY:
            print("❌ GROQ_API_KEY не задан")
            sys.exit(1)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = download_audio(url, tmpdir)
            print(f"  ✅ Аудио скачано: {Path(audio_path).name}")
            print("  Транскрибирую через Groq Whisper...")
            transcript = transcribe_with_groq(audio_path)
            method = "Groq Whisper Large V3 Turbo"
            print("  ✅ Транскрипция готова")
    
    if not transcript:
        print("❌ Не удалось получить транскрипт")
        sys.exit(1)
    
    print(f"\n📝 Длина транскрипта: {len(transcript)} символов")
    
    # Summary
    print("\n🤖 Делаю саммари...")
    summary = summarize(transcript, info.get("title", ""))
    
    # Save
    filepath = save_result(video_id, info, transcript, summary, method)
    print(f"\n✅ Сохранено: {filepath}")
    
    print("\n" + "="*50)
    print("САММАРИ:")
    print("="*50)
    print(summary)
    print("="*50)
    
    if not summary_only:
        print("\nТРАНСКРИПТ (первые 1000 символов):")
        print(transcript[:1000] + "..." if len(transcript) > 1000 else transcript)


if __name__ == "__main__":
    main()
