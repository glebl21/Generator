 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/bot.py b/bot.py
index cb041729803454f6b270afc4fe4b6f346d2b5c63..7ccbc6d81394bd5f36888fdaa0019277a1b88542 100644
--- a/bot.py
+++ b/bot.py
@@ -2,87 +2,91 @@
 Telegram Bot — генерация изображений и видео.
 
 Сервисы:
 - Pollinations.AI  — изображения, БЕСПЛАТНО БЕЗ КЛЮЧА (flux, realism, anime, 3d, turbo)
 - Google Gemini    — изображения, бесплатный ключ на aistudio.google.com
 - Seedance 2.0     — видео, бесплатные дневные кредиты на seedanceapi.org
 
 Установка:
     pip install python-telegram-bot requests
 
 Ключи (Railway → Variables, или export перед запуском):
     TELEGRAM_TOKEN   — @BotFather
     GEMINI_API_KEY   — aistudio.google.com  (опционально, запасной сервис)
     SEEDANCE_API_KEY — seedanceapi.org       (опционально, для видео)
 """
 
 import os
 import logging
 import requests
 import base64
 import time
 from urllib.parse import quote
 from io import BytesIO
 
 from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
+from telegram.error import Conflict
 from telegram.ext import (
     Application, CommandHandler, MessageHandler,
     CallbackQueryHandler, ContextTypes, filters, ConversationHandler,
 )
 
 # ─── Ключи из окружения ───────────────────────────────────────────
 TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN",   "")
 GEMINI_API_KEY   = os.environ.get("GEMINI_API_KEY",   "")
 SEEDANCE_API_KEY = os.environ.get("SEEDANCE_API_KEY", "")
 
 # ─── Pollinations.AI — БЕЗ ключа, полностью бесплатно ────────────
 # Документация: https://pollinations.ai
 POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
 
 POLLINATIONS_MODELS = {
     "pol_flux":     ("flux",         "⚡ Flux (универсальный)"),
     "pol_realism":  ("flux-realism", "📸 Flux Realism (фото)"),
     "pol_anime":    ("flux-anime",   "🎌 Flux Anime"),
     "pol_3d":       ("flux-3d",      "🎮 Flux 3D"),
     "pol_turbo":    ("turbo",        "🚀 Turbo (быстрый)"),
 }
 
 # ─── Gemini — запасной ────────────────────────────────────────────
 GEMINI_URL = (
     "https://generativelanguage.googleapis.com/v1beta/models/"
     "gemini-2.0-flash-exp-image-generation:generateContent"
 )
 
 # ─── Seedance — видео ─────────────────────────────────────────────
 SEEDANCE_URL    = "https://api.seedanceapi.org/v1/video/text2video"
 SEEDANCE_STATUS = "https://api.seedanceapi.org/v1/video/task/"
 
 CHOOSING_MODE, CHOOSING_IMAGE_MODEL, WAITING_PROMPT, WAITING_VIDEO_PROMPT = range(4)
 
 logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
 logger = logging.getLogger(__name__)
 
+CONFLICT_LOG_COOLDOWN_SEC = 30
+_last_conflict_log_at = 0.0
+
 
 # ════════════════════════════════════════════
 #  ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ
 # ════════════════════════════════════════════
 
 def gen_pollinations(prompt: str, model: str = "flux") -> bytes | None:
     """
     Pollinations.AI — бесплатно, без ключа, без лимитов регистрации.
     Возвращает сырые байты JPEG.
     """
     encoded = quote(prompt)
     url = f"{POLLINATIONS_BASE}/{encoded}?model={model}&width=1024&height=1024&nologo=true"
     try:
         r = requests.get(url, timeout=60)
         r.raise_for_status()
         return r.content
     except Exception as e:
         logger.error(f"Pollinations ({model}): {e}")
     return None
 
 
 def gen_gemini(prompt: str) -> bytes | None:
     """Gemini Flash — запасной вариант, нужен бесплатный ключ."""
     if not GEMINI_API_KEY:
         return None
@@ -152,50 +156,65 @@ async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
     ]]
     await update.message.reply_text(
         "👋 *AI Медиа Генератор*\n\n"
         "🖼 *5 бесплатных моделей* для изображений\n"
         "🎬 *Видео* через Seedance 2.0\n\n"
         "Выбери что хочешь создать:",
         parse_mode="Markdown",
         reply_markup=InlineKeyboardMarkup(kb),
     )
     return CHOOSING_MODE
 
 
 async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
     await update.message.reply_text(
         "📖 *Команды:*\n"
         "/start — меню\n"
         "/image — генерация фото\n"
         "/video — генерация видео\n"
         "/cancel — отмена\n\n"
         "💡 Промпты писать *на английском*\n"
         "Пример: `A cat on the moon, photorealistic, 4k`",
         parse_mode="Markdown",
     )
 
 
+async def image_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
+    await _ask_image_model(update.message)
+    return CHOOSING_IMAGE_MODEL
+
+
+async def video_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
+    ctx.user_data["video_service"] = "vid_seedance"
+    await update.message.reply_text(
+        "✏️ *Введи описание видео:*\n\n"
+        "Пример: `A cat playing in flowers, cinematic`",
+        parse_mode="Markdown",
+    )
+    return WAITING_VIDEO_PROMPT
+
+
 async def mode_chosen(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
     q = update.callback_query
     await q.answer()
     mode = q.data.split("_")[1]
     ctx.user_data["mode"] = mode
     if mode == "image":
         await _ask_image_model(q)
         return CHOOSING_IMAGE_MODEL
     else:
         await _ask_video_prompt(q)
         return WAITING_VIDEO_PROMPT
 
 
 async def _ask_image_model(target):
     kb = [
         [InlineKeyboardButton("⚡ Flux (универсальный)",   callback_data="pol_flux")],
         [InlineKeyboardButton("📸 Flux Realism (фото)",    callback_data="pol_realism")],
         [InlineKeyboardButton("🎌 Flux Anime",              callback_data="pol_anime")],
         [InlineKeyboardButton("🎮 Flux 3D",                callback_data="pol_3d")],
         [InlineKeyboardButton("🚀 Turbo (быстро)",         callback_data="pol_turbo")],
         [InlineKeyboardButton("✨ Gemini (нужен ключ)",    callback_data="img_gemini")],
     ]
     txt = "🖼 *Выбери модель:*\n\n_Первые 5 — полностью бесплатно, без ключей_"
     if hasattr(target, "edit_message_text"):
         await target.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
@@ -285,68 +304,83 @@ async def do_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
     ]]
     if video_url:
         await update.message.reply_text(
             f"✅ *Seedance 2.0*\n`{prompt[:100]}`\n\n🔗 [Скачать видео]({video_url})",
             parse_mode="Markdown",
             reply_markup=InlineKeyboardMarkup(kb),
         )
     else:
         err = "❌ Видео не сгенерировано."
         if not SEEDANCE_API_KEY:
             err += "\n\n⚠️ Ключ SEEDANCE_API_KEY не задан!\nПолучи бесплатно: seedanceapi.org"
         await update.message.reply_text(
             err,
             reply_markup=InlineKeyboardMarkup([[
                 InlineKeyboardButton("🔄 Снова", callback_data="mode_video")
             ]]),
         )
     return ConversationHandler.END
 
 
 async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
     await update.message.reply_text("❌ Отменено. /start — начать заново")
     return ConversationHandler.END
 
 
+async def on_error(update: object, ctx: ContextTypes.DEFAULT_TYPE) -> None:
+    global _last_conflict_log_at
+
+    err = ctx.error
+    if isinstance(err, Conflict):
+        now = time.monotonic()
+        if now - _last_conflict_log_at >= CONFLICT_LOG_COOLDOWN_SEC:
+            _last_conflict_log_at = now
+            logger.warning(
+                "⚠️ Конфликт Telegram getUpdates: вероятно запущен второй инстанс бота. "
+                "Текущий процесс продолжит polling и попробует снова."
+            )
+        return
+
+    logger.exception("Необработанная ошибка", exc_info=err)
+
+
 # ════════════════════════════════════════════
 #  MAIN
 # ════════════════════════════════════════════
 
 def main():
     if not TELEGRAM_TOKEN:
         raise RuntimeError("❌ Переменная TELEGRAM_TOKEN не задана!")
 
     app = Application.builder().token(TELEGRAM_TOKEN).build()
 
     conv = ConversationHandler(
         entry_points=[
             CommandHandler("start", start),
-            CommandHandler("image", lambda u, c: (
-                _ask_image_model(u.message)
-            )),
-            CommandHandler("video", lambda u, c: (
-                _ask_video_prompt(u.message)
-            )),
+            CommandHandler("image", image_cmd),
+            CommandHandler("video", video_cmd),
             CallbackQueryHandler(mode_chosen, pattern="^mode_"),
         ],
         states={
             CHOOSING_MODE:        [CallbackQueryHandler(mode_chosen,        pattern="^mode_")],
             CHOOSING_IMAGE_MODEL: [CallbackQueryHandler(image_model_chosen, pattern="^(pol_|img_)")],
             WAITING_PROMPT:       [MessageHandler(filters.TEXT & ~filters.COMMAND, do_image)],
             WAITING_VIDEO_PROMPT: [
                 CallbackQueryHandler(video_service_chosen, pattern="^vid_"),
                 MessageHandler(filters.TEXT & ~filters.COMMAND, do_video),
             ],
         },
         fallbacks=[CommandHandler("cancel", cancel)],
         allow_reentry=True,
+        per_message=True,
     )
 
     app.add_handler(conv)
     app.add_handler(CommandHandler("help", help_cmd))
+    app.add_error_handler(on_error)
 
     logger.info("🤖 Бот запущен!")
     app.run_polling(drop_pending_updates=True)
 
 
 if __name__ == "__main__":
     main()
 
EOF
)
