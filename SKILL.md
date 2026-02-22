# Скилл: YouTube Transcribe

Транскрибация YouTube видео + автоматическое саммари.

## Триггеры
- "транскрибируй видео", "расшифруй ролик", "сделай конспект видео"
- "summarize youtube", "/transcribe <url>"
- Ссылка на YouTube в сообщении + запрос на транскрипцию

## Стратегия (от дешёвого к дорогому)
1. **YouTube субтитры** — бесплатно (youtube-transcript-api)
2. **Groq Whisper Turbo** — $0.04/час, если субтитров нет

## Зависимости
- `~/.agent-venv/bin/yt-dlp` — скачивание аудио
- `youtube-transcript-api` — получение субтитров
- `groq` — транскрипция и саммари
- `GROQ_API_KEY` — в `~/.config/systemd/user/telegram-mcp.env`

## Использование

```bash
# Простая транскрипция + саммари
GROQ_API_KEY=$(grep GROQ_API_KEY ~/.config/systemd/user/telegram-mcp.env | cut -d= -f2) \
  ~/.agent-venv/bin/python3 ~/.openclaw/workspace/skills/youtube-transcribe/transcribe.py \
  "https://youtube.com/watch?v=VIDEO_ID"

# Только саммари
GROQ_API_KEY=... python3 transcribe.py "URL" --summary-only
```

## Результат
Сохраняется в `memory/knowledge/transcripts/YYYY-MM-DD-название.md`:
- Метаданные видео
- Краткое саммари (5-7 тезисов)
- Полный транскрипт

## Лимиты Groq (free tier)
- Whisper: 20 часов/сутки
- Размер файла: до 25MB
- Для длинных видео (>2ч) нужна разбивка на чанки — TODO

## Стоимость
- Видео с субтитрами: **$0**
- 1 час без субтитров: **~$0.04** (Groq Whisper Turbo)
- Саммари через llama-3.3-70b: **~$0.0002** за запрос
