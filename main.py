import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
from yt_dlp import YoutubeDL

# 🔑 ضع توكن البوت هنا
BOT_TOKEN = "7966509996:AAE7MNoWhWCURre5zKmojjAZwpVXir0EeUI"

# 📂 مجلد التحميل
DOWNLOAD_FOLDER = "./downloads/"

# 🧾 إعدادات التسجيل
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ⚙️ إعدادات yt-dlp العامة
YDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
    'noplaylist': True,
    'quiet': True,
    'merge_output_format': 'mp4',
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'geo_bypass': True,
    'writethumbnail': False,
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4'
    }]
}


# 🚀 أمر البدء
async def start_command(update: Update, context):
    await update.message.reply_text(
        "👋 أهلاً بك! أرسل لي أي رابط من:\n"
        "📺 YouTube | 🎵 TikTok | 📸 Instagram | 📘 Facebook\n\n"
        "وسأقوم بتحميل الفيديو وإرساله إليك 🎬"
    )


# 🎬 تحميل الفيديو
async def download_video(update: Update, context):
    url = update.message.text.strip()
    msg = await update.message.reply_text("⏳ py : ziad shahin جاري معالجة الرابط...")

    # التأكد من وجود مجلد التحميل
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # أحيانًا yt-dlp يضيف امتداد مختلف (مثل webm)
        if not os.path.exists(filename):
            base = os.path.splitext(filename)[0]
            filename = base + ".mp4"

        await msg.edit_text("✅ z_shتم التحميل! جاري الإرسال...")

        file_size = os.path.getsize(filename) / (1024 * 1024)  # بالميجابايت

        caption = f"🎥 *{info.get('title', 'فيديو بدون عنوان')}*\n✅ تم التحميل بنجاح!"
        with open(filename, "rb") as video_file:
            if file_size <= 50:
                # 📹 الفيديو صغير → يرسل كـ Video
                await update.message.reply_video(
                    video=video_file,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    supports_streaming=True
                )
            else:
                # 📁 الفيديو كبير → يرسل كـ Document
                await update.message.reply_document(
                    document=video_file,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )

        # حذف الملف بعد الإرسال
        os.remove(filename)
        await msg.edit_text("🗑️ تم حذف الملف المؤقت بنجاح.")
        logger.info(f"✅ تم إرسال الفيديو: {info.get('title', '')}")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error: {error_msg}")
        await msg.edit_text(f"❌ حدث خطأ أثناء التحميل:\n`{error_msg[:200]}`", parse_mode=ParseMode.MARKDOWN)


# 🧠 الدالة الرئيسية
def main():
    if not BOT_TOKEN or "ضع_التوكن" in BOT_TOKEN:
        print("❌ ضع التوكن الصحيح في المتغير BOT_TOKEN.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # أوامر وفلترات
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'https?://'), download_video))

    logger.info("🤖 البوت يعمل الآن... استماع للرابط 🔗")
    app.run_polling(poll_interval=2)


if __name__ == "__main__":
    main()
