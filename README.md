 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
index 069fa270a501ad4032b12f5086079c80b5205da3..980b72b4d4862d78d3e9427fd11f19ed094a15ba 100644
--- a/README.md
+++ b/README.md
@@ -44,50 +44,52 @@ CONFIG = {
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
 
+> ℹ️ `HF_TOKEN` можно хранить в Variables, но в текущем `bot.py` он не используется.
+
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
 
EOF
)
