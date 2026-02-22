# YouTube Transcribe — скилл для OpenClaw

Транскрибирует YouTube видео и делает краткий конспект. Работает бесплатно если у видео есть субтитры, и за копейки ($0.04/час) если нет.

---

## Как работает

Стратегия двухступенчатая — от дешёвого к платному:

1. Пробует получить субтитры напрямую с YouTube через `youtube-transcript-api` — это бесплатно и мгновенно
2. Если субтитров нет — скачивает аудио через `yt-dlp` и отправляет в Groq Whisper Turbo

После транскрипции — краткое саммари через llama-3.3-70b. Результат сохраняется в markdown-файл.

---

## Требования

- Python-окружение (venv)
- Groq API key — [бесплатный аккаунт на groq.com](https://console.groq.com) даёт 20 часов транскрипции в сутки
- Без ffmpeg: yt-dlp скачивает аудио в нативных форматах (m4a / webm)

---

## Установка

```bash
# Установить зависимости
pip install youtube-transcript-api groq yt-dlp

# Обязательно: Groq API ключ
export GROQ_API_KEY=your_key_here

# Опционально: cookies для обхода IP-блокировки на VPS
export YTDLP_COOKIES=/path/to/cookies.txt
```

Скопировать `transcribe.py` и `SKILL.md` в папку скилла OpenClaw:

```
skills/youtube-transcribe/
├── SKILL.md
├── README.md
└── transcribe.py
```

---

## Использование

```bash
# Транскрипция + саммари
GROQ_API_KEY=your_key python3 transcribe.py "https://youtube.com/watch?v=VIDEO_ID"

# Только саммари (без вывода полного транскрипта в консоль)
GROQ_API_KEY=your_key python3 transcribe.py "https://youtube.com/watch?v=VIDEO_ID" --summary-only
```

Результат сохраняется в `memory/knowledge/transcripts/YYYY-MM-DD-название.md`.

---

## Пример вывода

```
🎬 Транскрибация: https://youtube.com/watch?v=...
  Название: OpenClaw Setup with OpenRouter
  Канал: ATOM
  Длительность: 4:07

📋 Пробую субтитры YouTube...
  ✅ Субтитры получены

📝 Длина транскрипта: 2200 символов

🤖 Делаю саммари...

✅ Сохранено: memory/knowledge/transcripts/2026-02-22-openclaw-setup.md

САММАРИ:
В видео показан процесс переустановки OpenClaw с OpenRouter API...
- Удаление текущих настроек
- Повторная установка через openclaw onboard
- Выбор модели и ввод ключа API
- Подключение Telegram-канала
```

---

## Стоимость

| Сценарий | Цена |
|---|---|
| Видео с субтитрами | $0 |
| 1 час аудио без субтитров | ~$0.04 (Groq Whisper Turbo) |
| Саммари (один запрос) | ~$0.0002 (llama-3.3-70b) |

Groq Free Tier: 20 часов транскрипции в сутки — для большинства задач хватает.

---

## Ограничения

- Субтитры доступны не у всех видео и не на всех языках
- ffmpeg не нужен, но без него нет конвертации форматов — только нативный m4a/webm
- Файл аудио до 24MB (лимит Groq API 25MB) — скрипт использует `worstaudio` чтобы уложиться

## IP-блокировка на VPS: как решить

YouTube блокирует скачивание аудио с IP некоторых облачных провайдеров.
Путь через субтитры этой проблемы не имеет — работает на любом сервере.

Если нужен fallback для видео без субтитров — один раз настроить cookies:

**Шаг 1.** Установить расширение ["Get cookies.txt LOCALLY"](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) в Chrome или Firefox.

**Шаг 2.** Зайти на youtube.com (залогиниться), нажать расширение → Export → сохранить `cookies.txt`.

**Шаг 3.** Загрузить файл на сервер и прописать путь:

```bash
export YTDLP_COOKIES=/path/to/cookies.txt
```

После этого скрипт будет автоматически использовать cookies для всех загрузок — пользователь просто даёт ссылку и получает транскрипцию.

> Cookies периодически протухают — раз в несколько месяцев нужно обновить файл.

---

## Триггеры для агента

```
- "транскрибируй видео"
- "расшифруй ролик"
- "сделай конспект видео"
- "summarize youtube"
- ссылка на YouTube + запрос на конспект
```

---

Сделано для [OpenClaw](https://openclaw.ai) — AI-агент в Telegram.
