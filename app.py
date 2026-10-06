
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👑 INSTAGRAM ULTRA DOWNLOADER & TRACKER BOT
# 📱 MADE WITH PREMIUM AESTHETIC INTERFACE
# 🚀 RENDER FREE WEB SERVICE COMPATIBLE (FLASK INSIDE)
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import json
import time
import random
import logging
import asyncio
import threading
from Flask import Flask
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

# ================= 🌐 WEB SERVER FOR RENDER FREE SERVICE =================
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "⚡ Instagram Ultra Bot is Active & Running 24/7 on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

# ================= 👑 CONFIG & DATA FILES =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ACCOUNTS_FILE = "accounts.json"
TRACKING_FILE = "tracking_data.json"

scheduler = AsyncIOScheduler()

# Initialize Tracking File
if not os.path.exists(TRACKING_FILE):
    with open(TRACKING_FILE, "w") as f:
        json.dump({}, f)

def load_tracking_data():
    try:
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_tracking_data(data):
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ================= 🔄 MULTI-ACCOUNT ROTATION SYSTEM =================
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
        logger.info(f"✨ Successfully switched to Insta Session: {acc['username']}")
        return cl
    except Exception as e:
        logger.error(f"❌ Account Rotation Error: {e}")
        return None

# ================= 🎨 AESTHETIC KEYBOARD MENUS =================
def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📥 Download Reel", callback_data="help_download"),
            InlineKeyboardButton("🔍 Profile Lookup", callback_data="help_lookup")
        ],
        [
            InlineKeyboardButton("📸 Story Saver", callback_data="help_story"),
            InlineKeyboardButton("🎯 Target Tracker", callback_data="help_tracking")
        ],
        [
            InlineKeyboardButton("📊 Active Targets", callback_data="list_targets"),
            InlineKeyboardButton("⚡ Bot Status", callback_data="bot_status")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ================= 🚀 COMMAND HANDLERS =================

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "✨ <b>Welcome to Insta Ultra Bot</b> ✨\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔥 <b>Apka All-In-One Instagram Assistant!</b>\n\n"
        "⚡ <b>Quick Guide:</b>\n"
        "▸ 🎥 Send any <b>Reel / Video link</b> to Download.\n"
        "▸ 👤 Send <code>@username</code> for Profile Info & HD DP.\n"
        "▸ 📸 Send <code>/story username</code> to download Stories.\n"
        "▸ 🎯 Send <code>/track username</code> to start Live Tracking.\n\n"
        "👇 <b>Select an option from the menu below:</b>"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=main_menu_keyboard())

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help_download":
        await query.message.reply_text("📥 <b>Reel Downloader:</b>\nBus kisi bhi Instagram Reel/Post ka public link yahan chat me paste kar dein!", parse_mode="HTML")
    elif query.data == "help_lookup":
        await query.message.reply_text("🔍 <b>Profile Lookup & HD DP:</b>\nKisi bhi account ki details aur HD DP ke liye <code>@username</code> type karke bhejien.", parse_mode="HTML")
    elif query.data == "help_story":
        await query.message.reply_text("📸 <b>Story Saver:</b>\nCommand: <code>/story username</code>\n(Example: <code>/story cristiano</code>)", parse_mode="HTML")
    elif query.data == "help_tracking":
        await query.message.reply_text(
            "🎯 <b>Tracking Commands:</b>\n"
            "• <code>/track username</code> - Start Tracking Target\n"
            "• <code>/untrack username</code> - Remove Tracking\n"
            "• <code>/pause username</code> - Pause Tracking Alert\n"
            "• <code>/resume username</code> - Resume Alert", 
            parse_mode="HTML"
        )
    elif query.data == "list_targets":
        await tracking_list_cmd(query, context)
    elif query.data == "bot_status":
        await query.message.reply_text("⚡ <b>Bot Status:</b> 🟢 ONLINE (Render Free Web Service)\n🔄 <b>Account Pool:</b> Multi-Rotation Active", parse_mode="HTML")

# ================= 📥 DOWNLOADER & PROFILE LOOKUP =================

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # 1. Video/Reel Downloader
    if "instagram.com" in text:
        msg = await update.message.reply_text("⚡ <i>Processing Instagram Reel/Video...</i>", parse_mode="HTML")
        file_name = f"insta_{update.message.message_id}.mp4"
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_name,
            'quiet': True,
            'no_warnings': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([text])

            with open(file_name, 'rb') as video:
                await update.message.reply_video(
                    video=video,
                    caption="✨ <b>Downloaded via Insta Ultra Bot</b> 🚀",
                    parse_mode="HTML"
                )
            if os.path.exists(file_name):
                os.remove(file_name)
            await msg.delete()
        except Exception as e:
            logger.error(f"Download Error: {e}")
            await msg.edit_text("❌ <b>Download Failed!</b> Post private ho sakti hai ya link invalid hai.", parse_mode="HTML")
            if os.path.exists(file_name):
                os.remove(file_name)

    # 2. Profile Lookup & HD DP Download (@username)
    elif text.startswith("@"):
        username = text.replace("@", "").strip()
        msg = await update.message.reply_text("🔍 <i>Fetching Instagram Profile & HD DP...</i>", parse_mode="HTML")
        
        cl = get_insta_client()
        if not cl:
            await msg.edit_text("⚠️ Account Session Unavailable. Basic downloader is active.", parse_mode="HTML")
            return

        try:
            user_info = cl.user_info_by_username(username)
            caption = (
                f"👤 <b>Name:</b> {user_info.full_name}\n"
                f"🆔 <b>Username:</b> @{user_info.username}\n"
                f"👥 <b>Followers:</b> {user_info.follower_count:,}\n"
                f"➡️ <b>Following:</b> {user_info.following_count:,}\n"
                f"📮 <b>Posts:</b> {user_info.media_count}\n"
                f"🔒 <b>Is Private:</b> {'Yes 🔒' if user_info.is_private else 'No 🔓'}\n\n"
                f"📝 <b>Bio:</b>\n<i>{user_info.biography}</i>"
            )
            await update.message.reply_photo(
                photo=str(user_info.profile_pic_url_hd),
                caption=caption,
                parse_mode="HTML"
            )
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ Profile lookup failed for @{username}.", parse_mode="HTML")

async def story_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/story username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "")
    msg = await update.message.reply_text(f"📸 <i>Fetching stories for @{username}...</i>", parse_mode="HTML")

    cl = get_insta_client()
    if not cl:
        await msg.edit_text("⚠️ Insta Session File Required for Stories.", parse_mode="HTML")
        return

    try:
        user_id = cl.user_id_from_username(username)
        stories = cl.user_stories(user_id)
        if not stories:
            await msg.edit_text("📭 Abhi koi Active Story nahi hai.", parse_mode="HTML")
            return

        for story in stories:
            url = story.video_url if story.media_type == 2 else story.thumbnail_url
            if story.media_type == 2:
                await update.message.reply_video(video=str(url), caption=f"📸 Story by @{username}")
            else:
                await update.message.reply_photo(photo=str(url), caption=f"📸 Story by @{username}")
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Failed to fetch story: {e}", parse_mode="HTML")

# ================= 🎯 LIVE TARGET TRACKING ENGINE =================

async def track_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/track username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "").lower()
    chat_id = str(update.effective_chat.id)

    cl = get_insta_client()
    if not cl:
        await update.message.reply_text("❌ Multi-Account Session required for tracking.")
        return

    msg = await update.message.reply_text(f"🎯 <i>Setting up tracker for @{username}...</i>", parse_mode="HTML")
    try:
        user_info = cl.user_info_by_username(username)
        data = load_tracking_data()

        data[username] = {
            "user_id": str(user_info.pk),
            "chat_id": chat_id,
            "followers": user_info.follower_count,
            "following": user_info.following_count,
            "posts": user_info.media_count,
            "status": "active"
        }
        save_tracking_data(data)

        await msg.edit_text(
            f"🎯 <b>Tracking Activated for @{username}!</b>\n\n"
            f"👥 Followers: {user_info.follower_count}\n"
            f"➡️ Following: {user_info.following_count}\n\n"
            f"🔔 Bot ab Followers, Following aur Posts par najar rakhega!",
            parse_mode="HTML"
        )
    except Exception as e:
        await msg.edit_text(f"❌ Could not track profile: {e}", parse_mode="HTML")

async def untrack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️️ <b>Usage:</b> <code>/untrack username</code>", parse_mode="HTML")
        return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()

    if username in data:
        del data[username]
        save_tracking_data(data)
        await update.message.reply_text(f"🛑 <b>Tracking stopped for @{username}</b>", parse_mode="HTML")
    else:
        await update.message.reply_text("⚠️ Yeh user tracking list me nahi hai.")

async def pause_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/pause username</code>", parse_mode="HTML")
        return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()

    if username in data:
        data[username]["status"] = "paused"
        save_tracking_data(data)
        await update.message.reply_text(f"⏸️ <b>Tracking Paused for @{username}</b>", parse_mode="HTML")

async def resume_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/resume username</code>", parse_mode="HTML")
        return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()

    if username in data:
        data[username]["status"] = "active"
        save_tracking_data(data)
        await update.message.reply_text(f"▶️ <b>Tracking Resumed for @{username}</b>", parse_mode="HTML")

async def tracking_list_cmd(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    data = load_tracking_data()
    if not data:
        msg = "📭 <b>Koi active tracking target nahi hai.</b>"
    else:
        msg = "📊 <b>Your Active Tracking Targets:</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        for user, info in data.items():
            status_icon = "🟢 Active" if info.get("status") == "active" else "⏸️ Paused"
            msg += f"• <b>@{user}</b> | Status: {status_icon}\n"

    if hasattr(update_or_query, 'message'):
        await update_or_query.message.reply_text(msg, parse_mode="HTML")
    else:
        await update_or_query.message.reply_text(msg, parse_mode="HTML")

# --- BACKGROUND TRACKING TASK (EVERY 10 MINS) ---
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
            user_info = cl.user_info_by_username(username)
            old_f = info.get("followers", 0)
            new_f = user_info.follower_count

            old_fg = info.get("following", 0)
            new_fg = user_info.following_count

            chat_id = info.get("chat_id")

            # Follower Alert
            if new_f != old_f:
                diff = new_f - old_f
                icon = "📈" if diff > 0 else "📉"
                alert_msg = (
                    f"🔔 <b>TRACKER ALERT for @{username}</b> {icon}\n\n"
                    f"👥 <b>Followers Changed:</b> {old_f:,} ➔ <b>{new_f:,}</b> ({diff:+d})"
                )
                await context.bot.send_message(chat_id=chat_id, text=alert_msg, parse_mode="HTML")
                data[username]["followers"] = new_f

            # Following Alert
            if new_fg != old_fg:
                diff = new_fg - old_fg
                alert_msg = (
                    f"🔔 <b>TRACKER ALERT for @{username}</b> 🔄\n\n"
                    f"➡️ <b>Following Changed:</b> {old_fg:,} ➔ <b>{new_fg:,}</b> ({diff:+d})"
                )
                await context.bot.send_message(chat_id=chat_id, text=alert_msg, parse_mode="HTML")
                data[username]["following"] = new_fg

            save_tracking_data(data)
            await asyncio.sleep(5)  # Delay between accounts
        except Exception as e:
            logger.error(f"Tracking check error for {username}: {e}")

# ================= 🚀 MAIN LAUNCHER =================

async def post_init_setup(application):
    commands = [
        BotCommand("start", "Start Bot & Open Menu"),
        BotCommand("story", "Download Instagram Story"),
        BotCommand("track", "Start Tracking Target"),
        BotCommand("untrack", "Stop Tracking"),
        BotCommand("pause", "Pause Tracking Alerts"),
        BotCommand("resume", "Resume Tracking Alerts"),
        BotCommand("tracking", "List All Active Targets")
    ]
    await application.bot.set_my_commands(commands)

    # Start Background Tracking Scheduler (Every 10 Minutes)
    if not scheduler.running:
        scheduler.add_job(tracking_background_task, 'interval', minutes=10, kwargs={'context': application})
        scheduler.start()
        logger.info("🎯 Tracking Scheduler Started Successfully!")

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing!")
        return

    # 1. Start Flask Server in Background Thread for Render Web Service
    threading.Thread(target=run_flask, daemon=True).start()

    # 2. Start Telegram Bot
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init_setup).build()

    app.add_handler(CommandHandler("start", start_cmd))
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
