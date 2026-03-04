# 🤖 TG Media Generator Bot

Telegram-бот для генерации **изображений** и **видео** через бесплатные AI API.

---

## ✨ Возможности

- 🖼 **4 модели для изображений** — Gemini, Stable Diffusion XL, Flux Schnell, Realistic Vision
- 🎬 **2 сервиса для видео** — HuggingFace ModelScope, Seedance 2.0
- 💸 **Полностью бесплатно** — только бесплатные API без карты
- 🔄 Удобное меню выбора прямо в чате

---

## 📦 Установка

```bash
pip install python-telegram-bot requests Pillow
```

---

## 🔑 Получение ключей

| Сервис | Лимит | Ссылка |
|---|---|---|
| Telegram Bot | — | [@BotFather](https://t.me/BotFather) |
| Google Gemini | 500 фото/день | [aistudio.google.com](https://aistudio.google.com) |
| HuggingFace | Бесплатно | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| Seedance 2.0 | Кредиты/день | [seedanceapi.org](https://seedanceapi.org) |

---

## ⚙️ Настройка

Открой `bot.py` и вставь ключи в секцию `CONFIG`:

```python
CONFIG = {
    "TELEGRAM_TOKEN":   "токен от @BotFather",
    "GEMINI_API_KEY":   "AIzaSy...",
    "HF_TOKEN":         "hf_...",
    "SEEDANCE_API_KEY": "sk-...",
}
```

---

## 🚀 Запуск

### Локально
```bash
python bot.py
```

### Railway.app (рекомендую — бесплатно, 24/7)
1. Загрузи репозиторий на GitHub
2. Зайди на [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Добавь переменные окружения в разделе **Variables**:
```
TELEGRAM_TOKEN=...
GEMINI_API_KEY=...
HF_TOKEN=...
SEEDANCE_API_KEY=...
```
4. Готово — бот работает 24/7 ✅

### VPS (Ubuntu)
```bash
bash deploy.sh        # установка

export TELEGRAM_TOKEN="..."
export GEMINI_API_KEY="..."
export HF_TOKEN="..."
bash start.sh         # запуск в фоне (screen)

screen -r tgbot       # логи
```

---

## 📁 Структура файлов

```
├── bot.py            # Основной бот (ключи в CONFIG)
├── bot_cloud.py      # Версия для облака (ключи из env)
├── Dockerfile        # Docker образ
├── requirements.txt  # Зависимости
├── railway.json      # Конфиг для Railway
├── render.yaml       # Конфиг для Render
├── deploy.sh         # Скрипт установки на VPS
└── start.sh          # Запуск через screen
```

---

## 💬 Команды бота

| Команда | Описание |
|---|---|
| `/start` | Главное меню |
| `/image` | Генерация изображения |
| `/video` | Генерация видео |
| `/help` | Справка |
| `/cancel` | Отмена |

---

## 💡 Советы по промптам

Пиши промпты **на английском** — результат будет лучше.

```
A cat on the moon, photorealistic, 4k
Cyberpunk city at night, neon lights, rain, cinematic
A butterfly in slow motion, macro, golden hour
```

---

## 📄 Лицензия

MIT
