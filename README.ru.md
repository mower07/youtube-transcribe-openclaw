[🇺🇸 English](README.md) | 🇷🇺 Русский

# YouTube Transcribe — скилл для OpenClaw

Транскрибирует YouTube видео и делает краткий конспект.

**Работает на:** OpenClaw на собственном VPS/сервере.
**Не работает на:** cloud-hosted агентах (Kimi Claw и аналоги) — YouTube блокирует их IP целиком, включая запросы субтитров.

---

## Как работает

1. Пробует получить субтитры через `youtube-transcript-api` — бесплатно, без скачивания аудио
2. Если субтитров нет — скачивает аудио через `yt-dlp` и отправляет в Groq Whisper Turbo

Результат: саммари через llama-3.3-70b + markdown-файл с полным транскриптом.

---

## Требования

- Python venv с зависимостями
- Groq API key — бесплатный аккаунт на [groq.com](https://console.groq.com) даёт 20 часов транскрипции в сутки
- ffmpeg не нужен

---

## Установка

```bash
pip install youtube-transcript-api groq yt-dlp

export GROQ_API_KEY=your_key_here

# Опционально — если yt-dlp блокируется на вашем IP:
export YTDLP_COOKIES=/path/to/cookies.txt
```

Скопировать в папку скилла:

```
skills/youtube-transcribe/
├── SKILL.md
├── README.md
└── transcribe.py
```

---

## Использование

```bash
GROQ_API_KEY=your_key python3 transcribe.py "https://youtube.com/watch?v=VIDEO_ID"

# Только саммари
GROQ_API_KEY=your_key python3 transcribe.py "URL" --summary-only
```

Результат сохраняется в `memory/knowledge/transcripts/YYYY-MM-DD-название.md`.

---

## Пример вывода

```
🎬 OpenClaw Setup with OpenRouter | Канал: ATOM | 4:07
✅ Субтитры получены
✅ Сохранено: transcripts/2026-02-22-openclaw-setup.md

САММАРИ:
- Удаление текущих настроек через openclaw uninstall
- Переустановка через openclaw onboard
- Выбор модели и ввод API ключа
- Подключение Telegram-канала
```

---

## Стоимость

| Сценарий | Цена |
|---|---|
| Видео с субтитрами | $0 |
| 1 час без субтитров (Groq Whisper) | ~$0.04 |
| Саммари (llama-3.3-70b) | ~$0.0002 |

---

## Ограничения

**IP-блокировка.** YouTube блокирует запросы (включая субтитры) с IP крупных облачных провайдеров. Если вы видите ошибку `RequestBlocked` или `Sign in to confirm` — ваш IP в чёрном списке. Решение: cookies.txt (см. ниже) или смена провайдера. На managed cloud (Kimi и аналоги) это не решается.

**Cookies для обхода IP-блокировки.** Работает только если у вас есть доступ к файловой системе агента:
1. Установить расширение "Get cookies.txt LOCALLY" в Chrome/Firefox
2. Зайти на youtube.com залогиненным → экспортировать cookies.txt
3. Загрузить на сервер, задать `export YTDLP_COOKIES=/path/to/cookies.txt`

Cookies обновлять раз в несколько месяцев.

**Размер файла.** Скрипт использует `worstaudio` и лимит 24MB — Groq принимает до 25MB. Видео длиннее ~2.5 часов могут не влезть.

**ffmpeg не нужен.** yt-dlp скачивает нативные форматы (m4a/webm), конвертация не требуется.

---

## Триггеры

```
транскрибируй видео / расшифруй ролик / сделай конспект / summarize youtube
```

---

Сделано для [OpenClaw](https://openclaw.ai).
