#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👑 INSTAGRAM ULTRA SUITE (CLEAN PREMIUM EDITION) - PART 1
# 🚀 RENDER CLOUD 24/7 COMPATIBLE
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import json
import time
import random
import logging
import asyncio
import threading
from datetime import datetime
from flask import Flask
import yt_dlp
from instagrapi import Client
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_START_TIME = datetime.now()

# ================= 🌐 WEB SERVER FOR RENDER =================
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "⚡ Instagram Ultra Bot is Active & Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

# ================= 👑 CONFIG & DATA FILES =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ACCOUNTS_FILE = "accounts.json"
TRACKING_FILE = "tracking_data.json"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

scheduler = AsyncIOScheduler()

def load_tracking_data():
    if not os.path.exists(TRACKING_FILE):
        return {}
    try:
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_tracking_data(data):
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ================= 🤖 HUMAN EMULATION & ROTATION =================
def human_delay(min_sec=3, max_sec=6):
    time.sleep(random.uniform(min_sec, max_sec))

def get_insta_client():
    if not os.path.exists(ACCOUNTS_FILE):
        return None
    try:
        with open(ACCOUNTS_FILE, "r") as f:
            accounts = json.load(f)
        if not accounts:
            return None

        acc = random.choice(accounts)
        cl = Client()
        cl.login_by_sessionid(acc["sessionid"])
        human_delay(1, 3)
        return cl
    except Exception as e:
        logger.error(f"Account Switch Error: {e}")
        return None

# ================= 🎨 CLEAN & SLEEK KEYBOARD MENUS =================
def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🎬 Download Reel", callback_data="help_download"),
            InlineKeyboardButton("🎵 Extract Audio", callback_data="help_audio")
        ],
        [
            InlineKeyboardButton("👤 Profile Info", callback_data="help_lookup"),
            InlineKeyboardButton("📖 Story Saver", callback_data="help_story")
        ],
        [
            InlineKeyboardButton("🎯 Target Tracker", callback_data="help_tracking"),
            InlineKeyboardButton("📄 Export Lists", callback_data="help_export")
        ],
        [
            InlineKeyboardButton("📊 Active Targets", callback_data="list_targets"),
            InlineKeyboardButton("⚡ System Status", callback_data="bot_status")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ================= 🚀 COMMAND HANDLERS =================

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👑 <b>INSTAGRAM ULTRA SUITE</b>\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        "✨ <b>WELCOME TO YOUR PREMIUM ASSISTANT</b>\n\n"
        "⚡ <b>QUICK OPERATIONS:</b>\n"
        "├ 🎬 Send any <b>REEL link</b> to download\n"
        "├ 🎵 Send <code>/audio (link)</code> for MP3 song\n"
        "├ 👤 Send <code>@username</code> for Profile Info\n"
        "├ 📖 Send <code>/story username</code> for Active Stories\n"
        "├ 🎯 Send <code>/track username</code> for Live Surveillance\n"
        "├ 👥 Send <code>/followers username</code> for TXT Export\n"
        "├ ➡️ Send <code>/following username</code> for TXT Export\n"
        "└ ⚡ Send <code>/status</code> to check Bot Uptime\n\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        "👇 <b>Select an option from the menu below:</b>"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=main_menu_keyboard())

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = datetime.now() - BOT_START_TIME
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    session_count = 0
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r") as f:
                accs = json.load(f)
                session_count = len(accs)
        except:
            pass

    targets_count = len(load_tracking_data())

    status_text = (
        "⚡ <b>SYSTEM HEALTH & STATUS</b>\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"🟢 <b>Status:</b> Online 24/7\n"
        f"⏱️ <b>Uptime:</b> {hours}h {minutes}m {seconds}s\n"
        f"🔑 <b>Active Sessions:</b> {session_count} Accounts\n"
        f"🎯 <b>Tracking Targets:</b> {targets_count} Accounts\n"
        f"🛡️ <b>Anti-Ban Guard:</b> Active (Stealth Mode)\n"
        f"🖥️ <b>Server Host:</b> Render Cloud Web Service\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        "✨ All systems functioning normally!"
    )
    await update.message.reply_text(status_text, parse_mode="HTML")

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data_code = query.data

    if data_code == "help_download":
        await query.message.reply_text("🎬 <b>MEDIA DOWNLOADER</b>\n\nPaste any public Instagram Reel or Post link directly in this chat to receive HD Video.", parse_mode="HTML")
    elif data_code == "help_audio":
        await query.message.reply_text("🎵 <b>AUDIO EXTRACTOR</b>\n\nSend command: <code>/audio (Instagram Reel Link)</code> to extract MP3 audio.", parse_mode="HTML")
    elif data_code == "help_lookup":
        await query.message.reply_text("👤 <b>PROFILE INTELLIGENCE</b>\n\nSend any <code>@username</code> to get HD Profile Info and direct profile link.", parse_mode="HTML")
    elif data_code == "help_story":
        await query.message.reply_text("📖 <b>STORY SAVER</b>\n\nSyntax: <code>/story username</code>", parse_mode="HTML")
    elif data_code == "help_export":
        await query.message.reply_text("👥 <b>EXPORT LISTS</b>\n\n• <code>/followers username</code> - Export Followers TXT\n• <code>/following username</code> - Export Following TXT", parse_mode="HTML")
    elif data_code == "help_tracking":
        await query.message.reply_text("🎯 <b>TARGET SURVEILLANCE</b>\n\n• <code>/track username</code> - Start Tracking\n• <code>/untrack username</code> - Stop Tracking", parse_mode="HTML")
    elif data_code == "list_targets":
        await tracking_list_cmd(query, context)
    elif data_code == "bot_status":
        await status_cmd(query, context)

# ================= 📥 DOWNLOADER & PROFILE LOOKUP =================

async def audio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/audio (Reel Link)</code>", parse_mode="HTML")
        return

    url = context.args[0]
    msg = await update.message.reply_text("🎵 <i>Extracting audio stream...</i>", parse_mode="HTML")
    out_file = f"audio_{update.message.message_id}.mp3"

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'outtmpl': out_file.replace(".mp3", ""),
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open(out_file, 'rb') as audio_doc:
            await update.message.reply_audio(audio=audio_doc, caption="🎵 <b>Audio Extracted via Insta Suite</b> 🚀", parse_mode="HTML")

        if os.path.exists(out_file):
            os.remove(out_file)
        await msg.delete()
    except Exception as e:
        await msg.edit_text("❌ <b>Extraction failed!</b> Make sure the link is valid and public.", parse_mode="HTML")
        if os.path.exists(out_file):
            os.remove(out_file)

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "instagram.com" in text:
        msg = await update.message.reply_text("⏳ <i>Processing Instagram media...</i>", parse_mode="HTML")
        file_name = f"insta_{update.message.message_id}.mp4"

        ydl_opts = {'format': 'best', 'outtmpl': file_name, 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([text])

            with open(file_name, 'rb') as video:
                await update.message.reply_video(video=video, caption="🎬 <b>Downloaded via Insta Suite</b> 🚀", parse_mode="HTML")
            if os.path.exists(file_name):
                os.remove(file_name)
            await msg.delete()
        except Exception as e:
            await msg.edit_text("❌ <b>Download failed!</b> Post may be private or link is invalid.", parse_mode="HTML")
            if os.path.exists(file_name):
                os.remove(file_name)

    elif text.startswith("@"):
        username = text.replace("@", "").strip()
        msg = await update.message.reply_text("🔍 <i>Fetching profile details...</i>", parse_mode="HTML")

        cl = get_insta_client()
        if not cl:
            await msg.edit_text("⚠️ <b>System Alert:</b> Multi-account pool unavailable.", parse_mode="HTML")
            return

        try:
            human_delay(2, 4)
            user_info = cl.user_info_by_username(username)
            profile_url = f"https://instagram.com/{user_info.username}"

            caption = (
                f"👤 <b>PROFILE INTELLIGENCE</b>\n"
                f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                f"🆔 <b>Handle:</b> <a href='{profile_url}'>@{user_info.username}</a>\n"
                f"✨ <b>Full Name:</b> {user_info.full_name}\n"
                f"👥 <b>Followers:</b> {user_info.follower_count:,}\n"
                f"➡️ <b>Following:</b> {user_info.following_count:,}\n"
                f"📮 <b>Posts Count:</b> {user_info.media_count:,}\n"
                f"🔒 <b>Privacy Status:</b> {'Private 🔒' if user_info.is_private else 'Public 🔓'}\n"
                f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                f"📝 <b>Biography:</b>\n<i>{user_info.biography if user_info.biography else 'N/A'}</i>\n\n"
                f"👉 <b><a href='{profile_url}'>Click Here To Open Profile</a></b>"
            )

            await update.message.reply_photo(
                photo=str(user_info.profile_pic_url_hd),
                caption=caption,
                parse_mode="HTML"
            )
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ <b>Analysis Failed:</b> Unable to fetch profile for @{username}.", parse_mode="HTML")
# ================= 📁 EXPORTERS & STORY SAVER =================

async def followers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/followers username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "")
    msg = await update.message.reply_text(f"📄 <i>Fetching followers list for @{username}...</i>", parse_mode="HTML")

    cl = get_insta_client()
    if not cl:
        await msg.edit_text("❌ <b>Session Error:</b> Multi-account pool required.")
        return

    try:
        user_info = cl.user_info_by_username(username)
        if user_info.is_private:
            await msg.edit_text("🔒 <b>Private Profile:</b> Cannot fetch followers for private profiles.", parse_mode="HTML")
            return

        followers_dict = cl.user_followers(user_info.pk, amount=150)

        file_path = f"{username}_followers.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"=== FOLLOWERS LIST FOR @{username} ===\n\n")
            for uid, uinfo in followers_dict.items():
                f.write(f"@{uinfo.username} | Name: {uinfo.full_name}\n")

        with open(file_path, "rb") as doc:
            await update.message.reply_document(document=doc, caption=f"👥 <b>Followers Export — @{username}</b>", parse_mode="HTML")

        if os.path.exists(file_path):
            os.remove(file_path)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ <b>Export Failed:</b> {e}", parse_mode="HTML")

async def following_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/following username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "")
    msg = await update.message.reply_text(f"📄 <i>Fetching following list for @{username}...</i>", parse_mode="HTML")

    cl = get_insta_client()
    if not cl:
        await msg.edit_text("❌ <b>Session Error:</b> Multi-account pool required.")
        return

    try:
        user_info = cl.user_info_by_username(username)
        if user_info.is_private:
            await msg.edit_text("🔒 <b>Private Profile:</b> Cannot fetch following for private profiles.", parse_mode="HTML")
            return

        following_dict = cl.user_following(user_info.pk, amount=150)

        file_path = f"{username}_following.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"=== FOLLOWING LIST FOR @{username} ===\n\n")
            for uid, uinfo in following_dict.items():
                f.write(f"@{uinfo.username} | Name: {uinfo.full_name}\n")

        with open(file_path, "rb") as doc:
            await update.message.reply_document(document=doc, caption=f"➡️ <b>Following Export — @{username}</b>", parse_mode="HTML")

        if os.path.exists(file_path):
            os.remove(file_path)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ <b>Export Failed:</b> {e}", parse_mode="HTML")

async def story_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/story username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "")
    msg = await update.message.reply_text(f"📖 <i>Fetching active stories for @{username}...</i>", parse_mode="HTML")

    cl = get_insta_client()
    if not cl:
        await msg.edit_text("⚠️ <b>Session Error:</b> Accounts pool required.", parse_mode="HTML")
        return

    try:
        user_info = cl.user_info_by_username(username)
        stories = cl.user_stories(user_info.pk)
        if not stories:
            await msg.edit_text("📭 <b>No active stories found for this profile.</b>", parse_mode="HTML")
            return

        for story in stories:
            url = story.video_url if story.media_type == 2 else story.thumbnail_url
            if story.media_type == 2:
                await update.message.reply_video(video=str(url), caption=f"📖 <b>Story Stream:</b> @{username}")
            else:
                await update.message.reply_photo(photo=str(url), caption=f"📖 <b>Story Image:</b> @{username}")
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ <b>Error:</b> Unable to fetch stories: {e}", parse_mode="HTML")

# ================= 🎯 SAFE TARGET TRACKING ENGINE =================

async def track_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/track username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "").lower()
    chat_id = str(update.effective_chat.id)

    cl = get_insta_client()
    if not cl:
        await update.message.reply_text("❌ <b>Session Error:</b> Accounts pool required.")
        return

    msg = await update.message.reply_text(f"🎯 <i>Activating tracking engine for @{username}...</i>", parse_mode="HTML")
    try:
        user_info = cl.user_info_by_username(username)
        data = load_tracking_data()

        active_stories = cl.user_stories(user_info.pk)
        initial_story_pks = [str(s.pk) for s in active_stories]

        recent_posts = cl.user_medias(user_info.pk, amount=3)
        initial_post_pks = [str(p.pk) for p in recent_posts]

        data[username] = {
            "user_id": str(user_info.pk),
            "chat_id": chat_id,
            "followers": user_info.follower_count,
            "following": user_info.following_count,
            "posts": user_info.media_count,
            "seen_stories": initial_story_pks,
            "seen_posts": initial_post_pks,
            "status": "active"
        }
        save_tracking_data(data)

        await msg.edit_text(
            f"🎯 <b>SURVEILLANCE ACTIVATED</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"👤 <b>Target:</b> @{username}\n"
            f"👥 <b>Initial Followers:</b> {user_info.follower_count:,}\n"
            f"➡️ <b>Initial Following:</b> {user_info.following_count:,}\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"🔔 Live surveillance active with Anti-Ban Stealth Guard.",
            parse_mode="HTML"
        )
    except Exception as e:
        await msg.edit_text(f"❌ <b>Tracking Failed:</b> {e}", parse_mode="HTML")

async def untrack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/untrack username</code>", parse_mode="HTML")
        return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()

    if username in data:
        del data[username]
        save_tracking_data(data)
        await update.message.reply_text(f"🛑 <b>Surveillance terminated for @{username}</b>", parse_mode="HTML")
    else:
        await update.message.reply_text("⚠️ <b>Target Not Found:</b> Username not in tracking list.")

async def pause_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()
    if username in data:
        data[username]["status"] = "paused"
        save_tracking_data(data)
        await update.message.reply_text(f"⏸ <b>Surveillance paused for @{username}</b>", parse_mode="HTML")

async def resume_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()
    if username in data:
        data[username]["status"] = "active"
        save_tracking_data(data)
        await update.message.reply_text(f"▶️ <b>Surveillance resumed for @{username}</b>", parse_mode="HTML")

async def tracking_list_cmd(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    data = load_tracking_data()
    if not data:
        msg = "📭 <b>No active tracking targets registered.</b>"
    else:
        msg = "📊 <b>ACTIVE SURVEILLANCE REGISTRY</b>\n<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        for user, info in data.items():
            status_icon = "🟢 Active" if info.get("status") == "active" else "⏸️ Paused"
            msg += f"• <b>@{user}</b> │ Status: {status_icon}\n"

    if hasattr(update_or_query, 'message'):
        await update_or_query.message.reply_text(msg, parse_mode="HTML")
    else:
        await update_or_query.message.reply_text(msg, parse_mode="HTML")

# --- BACKGROUND STEALTH TRACKING TASK ---
async def tracking_background_task(context: ContextTypes.DEFAULT_TYPE):
    data = load_tracking_data()
    if not data:
        return

    cl = get_insta_client()
    if not cl:
        return

    for username, info in list(data.items()):
        if info.get("status") != "active":
            continue

        try:
            human_delay(5, 12) # Safe Anti-Ban Delay
            user_id = info.get("user_id")
            user_info = cl.user_info_by_username(username)

            old_f, new_f = info.get("followers", 0), user_info.follower_count
            old_fg, new_fg = info.get("following", 0), user_info.following_count
            chat_id = info.get("chat_id")

            if new_f != old_f:
                diff = new_f - old_f
                icon = "📈" if diff > 0 else "📉"
                await context.bot.send_message(chat_id=chat_id, text=f"🚨 <b>SURVEILLANCE ALERT — @{username}</b> {icon}\nFollowers: <code>{old_f:,}</code> ➔ <b>{new_f:,}</b> ({diff:+d})", parse_mode="HTML")
                data[username]["followers"] = new_f

            if new_fg != old_fg:
                diff = new_fg - old_fg
                await context.bot.send_message(chat_id=chat_id, text=f"🚨 <b>SURVEILLANCE ALERT — @{username}</b> 🔄\nFollowing: <code>{old_fg:,}</code> ➔ <b>{new_fg:,}</b> ({diff:+d})", parse_mode="HTML")
                data[username]["following"] = new_fg

            save_tracking_data(data)
        except Exception as e:
            logger.error(f"Tracking check error for {username}: {e}")

# ================= 🚀 MAIN LAUNCHER =================

async def post_init_setup(application):
    commands = [
        BotCommand("start", "Start Bot & Open Suite"),
        BotCommand("status", "Check Live System Status"),
        BotCommand("audio", "Extract Audio/Song MP3"),
        BotCommand("followers", "Export Followers to TXT"),
        BotCommand("following", "Export Following to TXT"),
        BotCommand("story", "Download Instagram Story"),
        BotCommand("track", "Activate Surveillance"),
        BotCommand("untrack", "Terminate Surveillance"),
        BotCommand("pause", "Pause Surveillance Alerts"),
        BotCommand("resume", "Resume Surveillance Alerts"),
        BotCommand("tracking", "List Tracking Targets")
    ]
    await application.bot.set_my_commands(commands)

    if not scheduler.running:
        # Safe Interval: 20 Minutes (Prevent Bot Ban)
        scheduler.add_job(tracking_background_task, 'interval', minutes=20, kwargs={'context': application})
        scheduler.start()

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing!")
        return

    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init_setup).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("audio", audio_cmd))
    app.add_handler(CommandHandler("followers", followers_cmd))
    app.add_handler(CommandHandler("following", following_cmd))
    app.add_handler(CommandHandler("story", story_cmd))
    app.add_handler(CommandHandler("track", track_cmd))
    app.add_handler(CommandHandler("untrack", untrack_cmd))
    app.add_handler(CommandHandler("pause", pause_cmd))
    app.add_handler(CommandHandler("resume", resume_cmd))
    app.add_handler(CommandHandler("tracking", tracking_list_cmd))

    app.add_handler(CallbackQueryHandler(button_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    logger.info("🤖 Insta Ultra Bot is Live!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
