"""
Версия бота для облачного деплоя.
Ключи читаются из переменных окружения (environment variables).
"""

import os, logging, requests, base64, time
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler,
)

# ─────────────────────────────────────────────
#  Ключи из переменных окружения
#  (для локального запуска — создай файл .env и используй python-dotenv)
# ─────────────────────────────────────────────
TELEGRAM_TOKEN  = os.environ.get("TELEGRAM_TOKEN",  "")
GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY",  "")
HF_TOKEN        = os.environ.get("HF_TOKEN",        "")
SEEDANCE_API_KEY = os.environ.get("SEEDANCE_API_KEY", "")

# ─────────────────────────────────────────────
#  API endpoints
# ─────────────────────────────────────────────
GEMINI_IMAGE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent"
HF_IMAGE_MODELS = {
    "img_sdxl": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
    "img_flux":  "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
    "img_real":  "https://api-inference.huggingface.co/models/SG161222/Realistic_Vision_V6.0_B1_noVAE",
}
HF_VIDEO_URL   = "https://api-inference.huggingface.co/models/ali-vilab/text-to-video-ms-1.7b"
SEEDANCE_URL   = "https://api.seedanceapi.org/v1/video/text2video"
SEEDANCE_STATUS = "https://api.seedanceapi.org/v1/video/task/"

CHOOSING_MODE, CHOOSING_IMAGE_MODEL, WAITING_PROMPT, WAITING_VIDEO_PROMPT = range(4)

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Image generators ────────────────────────────────────────────────────────

def gen_gemini(prompt):
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }
    try:
        r = requests.post(f"{GEMINI_IMAGE_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        for part in r.json()["candidates"][0]["content"]["parts"]:
            if part.get("inlineData"):
                return base64.b64decode(part["inlineData"]["data"])
    except Exception as e:
        logger.error(f"Gemini: {e}")
    return None

def gen_hf_image(prompt, model_url):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt, "parameters": {"num_inference_steps": 20}}
    try:
        r = requests.post(model_url, headers=headers, json=payload, timeout=120)
        if r.status_code == 503:
            time.sleep(20)
            r = requests.post(model_url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        return r.content
    except Exception as e:
        logger.error(f"HF image: {e}")
    return None


# ── Video generators ─────────────────────────────────────────────────────────

def gen_hf_video(prompt):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt, "parameters": {"num_frames": 16, "num_inference_steps": 25}}
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

def gen_seedance(prompt):
    headers = {"Authorization": f"Bearer {SEEDANCE_API_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post(SEEDANCE_URL, headers=headers,
                          json={"prompt": prompt, "resolution": "720p", "duration": 5}, timeout=30)
        r.raise_for_status()
        task_id = r.json().get("task_id")
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


# ── Handlers ─────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🖼 Изображение", callback_data="mode_image"),
           InlineKeyboardButton("🎬 Видео",        callback_data="mode_video")]]
    await update.message.reply_text(
        "👋 *AI медиа-генератор*\n\nВыбери что хочешь создать:",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    return CHOOSING_MODE

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Команды:* /start /image /video /cancel\n\n"
        "💡 Промпты лучше писать *на английском*\n"
        "Пример: `A cat on the moon, photorealistic, 4k`",
        parse_mode="Markdown")

async def mode_chosen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
        [InlineKeyboardButton("✨ Gemini (рек.)",      callback_data="img_gemini")],
        [InlineKeyboardButton("🎨 Stable Diffusion XL", callback_data="img_sdxl")],
        [InlineKeyboardButton("⚡ Flux Schnell",         callback_data="img_flux")],
        [InlineKeyboardButton("📸 Realistic Vision",     callback_data="img_real")],
    ]
    txt = "🖼 *Выбери модель:*"
    m = target.message if hasattr(target, "message") else target
    await m.reply_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb)) if hasattr(target, "message") \
        else await target.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def _ask_video_service(target):
    kb = [
        [InlineKeyboardButton("🤗 HuggingFace (бесплатно)", callback_data="vid_hf")],
        [InlineKeyboardButton("🎬 Seedance 2.0 (HD)",        callback_data="vid_seedance")],
    ]
    txt = "🎬 *Выбери сервис:*\n⚠️ Генерация занимает 1-3 мин"
    m = target.message if hasattr(target, "message") else target
    await m.reply_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb)) if hasattr(target, "message") \
        else await target.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def image_model_chosen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    ctx.user_data["image_model"] = q.data
    await q.edit_message_text(
        "✏️ *Введи описание изображения:*\n\nПример: `A futuristic city at sunset, 4k`",
        parse_mode="Markdown")
    return WAITING_PROMPT

async def video_service_chosen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    ctx.user_data["video_service"] = q.data
    await q.edit_message_text(
        "✏️ *Введи описание видео:*\n\nПример: `A cat playing in flowers, cinematic`",
        parse_mode="Markdown")
    return WAITING_VIDEO_PROMPT

async def do_image(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    model  = ctx.user_data.get("image_model", "img_gemini")
    msg = await update.message.reply_text("⏳ Генерирую…")

    data, name = None, ""
    if model == "img_gemini":  data, name = gen_gemini(prompt), "Gemini"
    elif model in HF_IMAGE_MODELS: data, name = gen_hf_image(prompt, HF_IMAGE_MODELS[model]), model.split("_")[1].upper()

    await msg.delete()
    kb = [[InlineKeyboardButton("🔄 Ещё фото", callback_data="mode_image"),
           InlineKeyboardButton("🎬 Видео",     callback_data="mode_video")]]
    if data:
        await update.message.reply_photo(BytesIO(data),
            caption=f"✅ *{name}*\n`{prompt[:100]}`", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.message.reply_text("❌ Ошибка генерации. Проверь API ключ или попробуй позже.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Снова", callback_data="mode_image")]]))
    return ConversationHandler.END

async def do_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    prompt  = update.message.text
    service = ctx.user_data.get("video_service", "vid_hf")
    msg = await update.message.reply_text("⏳ Генерирую видео… 1-3 минуты")

    video_bytes, video_url, name = None, None, ""
    if service == "vid_hf":
        video_bytes, name = gen_hf_video(prompt), "HuggingFace"
    elif service == "vid_seedance":
        video_url, name = gen_seedance(prompt), "Seedance 2.0"

    await msg.delete()
    kb = [[InlineKeyboardButton("🔄 Ещё видео", callback_data="mode_video"),
           InlineKeyboardButton("🖼 Фото",       callback_data="mode_image")]]
    if video_bytes:
        await update.message.reply_video(BytesIO(video_bytes),
            caption=f"✅ *{name}*\n`{prompt[:100]}`", parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb))
    elif video_url:
        await update.message.reply_text(
            f"✅ *{name}*\n`{prompt[:100]}`\n\n🔗 [Скачать видео]({video_url})",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.message.reply_text("❌ Ошибка генерации видео. Попробуй позже.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Снова", callback_data="mode_video")]]))
    return ConversationHandler.END

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено. /start — начать заново")
    return ConversationHandler.END


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Переменная TELEGRAM_TOKEN не задана!")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("image", lambda u,c: (c.user_data.update({"mode":"image"}), _ask_image_model(u.message))[-1]),
            CommandHandler("video", lambda u,c: (c.user_data.update({"mode":"video"}), _ask_video_service(u.message))[-1]),
            CallbackQueryHandler(mode_chosen, pattern="^mode_"),
        ],
        states={
            CHOOSING_MODE:        [CallbackQueryHandler(mode_chosen, pattern="^mode_")],
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
