"""
Telegram Bot — генерация изображений и видео.
Исправленная версия: обновлены все HuggingFace модели (старые вернули 410 Gone),
Gemini переключён на Imagen 3 (избегаем 429 на flash-exp).
"""

import os
import logging
import requests
import base64
import time
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler,
)

# ─────────────────────────────────────────────
#  Ключи — из переменных окружения (Railway/VPS)
#  или вставь напрямую для локального запуска
# ─────────────────────────────────────────────
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN",   "")
GEMINI_API_KEY   = os.environ.get("GEMINI_API_KEY",   "")
HF_TOKEN         = os.environ.get("HF_TOKEN",         "")
SEEDANCE_API_KEY = os.environ.get("SEEDANCE_API_KEY", "")

# ─────────────────────────────────────────────
#  Рабочие API endpoint'ы (март 2025)
# ─────────────────────────────────────────────

# Gemini Imagen 3 — стабильный, без 429
GEMINI_IMAGEN_URL = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict"

# HuggingFace — только модели с активным Inference API (не 410)
HF_MODELS = {
    "img_flux_dev":    "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev",
    "img_flux_schnell":"https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
    "img_sd2":         "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
}

# HuggingFace видео — рабочая модель
HF_VIDEO_URL = "https://api-inference.huggingface.co/models/Wan-AI/Wan2.1-T2V-14B"

# Seedance
SEEDANCE_URL    = "https://api.seedanceapi.org/v1/video/text2video"
SEEDANCE_STATUS = "https://api.seedanceapi.org/v1/video/task/"

CHOOSING_MODE, CHOOSING_IMAGE_MODEL, WAITING_PROMPT, WAITING_VIDEO_PROMPT = range(4)

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════
#  ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ
# ════════════════════════════════════════════

def gen_imagen3(prompt: str) -> bytes | None:
    """Google Imagen 3 — стабильный, ~10 сек."""
    url = f"{GEMINI_IMAGEN_URL}?key={GEMINI_API_KEY}"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }
    try:
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        b64 = r.json()["predictions"][0]["bytesBase64Encoded"]
        return base64.b64decode(b64)
    except Exception as e:
        logger.error(f"Imagen3: {e}")
    return None


def gen_hf_image(prompt: str, model_url: str) -> bytes | None:
    """HuggingFace Inference API — FLUX.1-dev / schnell / SD2."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"num_inference_steps": 25, "guidance_scale": 7.5}
    }
    try:
        r = requests.post(model_url, headers=headers, json=payload, timeout=120)
        if r.status_code == 503:
            # Модель грузится — ждём и повторяем
            wait = r.json().get("estimated_time", 20)
            time.sleep(min(wait, 30))
            r = requests.post(model_url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        return r.content
    except Exception as e:
        logger.error(f"HF image ({model_url}): {e}")
    return None


# ════════════════════════════════════════════
#  ГЕНЕРАЦИЯ ВИДЕО
# ════════════════════════════════════════════

def gen_hf_video(prompt: str) -> bytes | None:
    """HuggingFace Wan2.1 T2V — рабочая модель видео."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    try:
        r = requests.post(HF_VIDEO_URL, headers=headers, json=payload, timeout=300)
        if r.status_code == 503:
            time.sleep(30)
            r = requests.post(HF_VIDEO_URL, headers=headers, json=payload, timeout=300)
        r.raise_for_status()
        return r.content
    except Exception as e:
        logger.error(f"HF video: {e}")
    return None


def gen_seedance(prompt: str) -> str | None:
    """Seedance 2.0 — polling до готовности."""
    headers = {"Authorization": f"Bearer {SEEDANCE_API_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post(SEEDANCE_URL, headers=headers,
                          json={"prompt": prompt, "resolution": "720p", "duration": 5}, timeout=30)
        r.raise_for_status()
        task_id = r.json().get("task_id")
        if not task_id:
            return None
        for _ in range(36):
            time.sleep(5)
            s = requests.get(f"{SEEDANCE_STATUS}{task_id}", headers=headers, timeout=15).json()
            if s.get("status") == "completed":
                return s.get("video_url")
            if s.get("status") == "failed":
                return None
    except Exception as e:
        logger.error(f"Seedance: {e}")
    return None


# ════════════════════════════════════════════
#  TELEGRAM HANDLERS
# ════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    kb = [[
        InlineKeyboardButton("🖼 Изображение", callback_data="mode_image"),
        InlineKeyboardButton("🎬 Видео",        callback_data="mode_video"),
    ]]
    await update.message.reply_text(
        "👋 *AI Медиа Генератор*\n\nВыбери что хочешь создать:",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    return CHOOSING_MODE


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Команды:*\n/start — меню\n/image — фото\n/video — видео\n/cancel — отмена\n\n"
        "💡 Промпты писать *на английском*\n"
        "Пример: `A cat on the moon, photorealistic, 4k`",
        parse_mode="Markdown")


async def mode_chosen(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    mode = q.data.split("_")[1]
    ctx.user_data["mode"] = mode
    if mode == "image":
        await _ask_image_model(q)
        return CHOOSING_IMAGE_MODEL
    else:
        await _ask_video_service(q)
        return WAITING_VIDEO_PROMPT


async def _ask_image_model(target):
    kb = [
        [InlineKeyboardButton("🌟 Imagen 3 (Google, лучшее)",  callback_data="img_imagen3")],
        [InlineKeyboardButton("⚡ FLUX.1-schnell (быстрый)",   callback_data="img_flux_schnell")],
        [InlineKeyboardButton("🎨 FLUX.1-dev (качество)",      callback_data="img_flux_dev")],
        [InlineKeyboardButton("🖌 Stable Diffusion 2.1",       callback_data="img_sd2")],
    ]
    txt = "🖼 *Выбери модель:*"
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    else:
        await target.reply_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))


async def _ask_video_service(target):
    kb = [
        [InlineKeyboardButton("🤗 HuggingFace Wan2.1 (бесплатно)", callback_data="vid_hf")],
        [InlineKeyboardButton("🎬 Seedance 2.0 (HD качество)",      callback_data="vid_seedance")],
    ]
    txt = "🎬 *Выбери сервис:*\n⚠️ Генерация занимает 1–3 мин"
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    else:
        await target.reply_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))


async def image_model_chosen(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    ctx.user_data["image_model"] = q.data
    await q.edit_message_text(
        "✏️ *Введи описание изображения:*\n\nПример:\n`A futuristic city at sunset, cinematic, 4k`",
        parse_mode="Markdown")
    return WAITING_PROMPT


async def video_service_chosen(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query; await q.answer()
    ctx.user_data["video_service"] = q.data
    await q.edit_message_text(
        "✏️ *Введи описание видео:*\n\nПример:\n`A cat playing in a field of flowers, cinematic`",
        parse_mode="Markdown")
    return WAITING_VIDEO_PROMPT


async def do_image(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    prompt = update.message.text
    model  = ctx.user_data.get("image_model", "img_imagen3")
    msg = await update.message.reply_text("⏳ Генерирую изображение…")

    data, name = None, ""
    if model == "img_imagen3":
        data, name = gen_imagen3(prompt), "Imagen 3 (Google)"
    elif model in HF_MODELS:
        labels = {
            "img_flux_schnell": "FLUX.1-schnell",
            "img_flux_dev":     "FLUX.1-dev",
            "img_sd2":          "Stable Diffusion 2.1",
        }
        data, name = gen_hf_image(prompt, HF_MODELS[model]), labels.get(model, model)

    await msg.delete()
    kb = [[
        InlineKeyboardButton("🔄 Ещё фото", callback_data="mode_image"),
        InlineKeyboardButton("🎬 Видео",     callback_data="mode_video"),
    ]]
    if data:
        await update.message.reply_photo(
            BytesIO(data),
            caption=f"✅ *{name}*\n`{prompt[:100]}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.message.reply_text(
            "❌ Ошибка генерации. Проверь API ключ или попробуй другую модель.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Попробовать снова", callback_data="mode_image")
            ]]))
    return ConversationHandler.END


async def do_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    prompt  = update.message.text
    service = ctx.user_data.get("video_service", "vid_hf")
    msg = await update.message.reply_text("⏳ Генерирую видео… это займёт 1–3 минуты")

    video_bytes, video_url, name = None, None, ""
    if service == "vid_hf":
        video_bytes, name = gen_hf_video(prompt), "HuggingFace Wan2.1"
    elif service == "vid_seedance":
        video_url, name = gen_seedance(prompt), "Seedance 2.0"

    await msg.delete()
    kb = [[
        InlineKeyboardButton("🔄 Ещё видео", callback_data="mode_video"),
        InlineKeyboardButton("🖼 Фото",       callback_data="mode_image"),
    ]]
    if video_bytes:
        await update.message.reply_video(
            BytesIO(video_bytes),
            caption=f"✅ *{name}*\n`{prompt[:100]}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb))
    elif video_url:
        await update.message.reply_text(
            f"✅ *{name}*\n`{prompt[:100]}`\n\n🔗 [Скачать видео]({video_url})",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.message.reply_text(
            "❌ Ошибка генерации видео. Попробуй позже или другой сервис.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Снова", callback_data="mode_video")
            ]]))
    return ConversationHandler.END


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Отменено. /start — начать заново")
    return ConversationHandler.END


# ════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════

def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("❌ TELEGRAM_TOKEN не задан!")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("image", lambda u,c: (_ask_image_model(u.message))),
            CommandHandler("video", lambda u,c: (_ask_video_service(u.message))),
            CallbackQueryHandler(mode_chosen, pattern="^mode_"),
        ],
        states={
            CHOOSING_MODE:        [CallbackQueryHandler(mode_chosen,        pattern="^mode_")],
            CHOOSING_IMAGE_MODEL: [CallbackQueryHandler(image_model_chosen, pattern="^img_")],
            WAITING_PROMPT:       [MessageHandler(filters.TEXT & ~filters.COMMAND, do_image)],
            WAITING_VIDEO_PROMPT: [
                CallbackQueryHandler(video_service_chosen, pattern="^vid_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, do_video),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_cmd))

    logger.info("🤖 Бот запущен!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
