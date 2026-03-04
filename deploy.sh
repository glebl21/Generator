#!/bin/bash
# Скрипт автоматической установки бота на Ubuntu VPS
# Использование: bash deploy.sh

echo "🚀 Установка Telegram бота на сервер..."

# 1. Обновление системы
sudo apt update && sudo apt upgrade -y

# 2. Установка Python
sudo apt install python3 python3-pip python3-venv -y

# 3. Создание папки проекта
mkdir -p ~/tgbot && cd ~/tgbot

# 4. Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# 5. Установка зависимостей
pip install python-telegram-bot requests Pillow

echo "✅ Зависимости установлены!"
echo ""
echo "📋 Следующий шаг:"
echo "   1. Скопируй bot.py в папку ~/tgbot/"
echo "   2. Вставь свои API ключи в CONFIG"
echo "   3. Запусти: bash start.sh"
