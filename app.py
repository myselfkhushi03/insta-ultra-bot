#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👑 INSTAGRAM ULTRA DOWNLOADER & TRACKER BOT
# 📱 ULTRA-PREMIUM EDITION (ENGLISH UI)
# 🚀 RENDER FREE WEB SERVICE COMPATIBLE (FLASK INSIDE)
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import json
import time
import random
import logging
import asyncio
import threading
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

# ================= 🎨 ULTRA-PREMIUM KEYBOARD MENUS =================
def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📥 Download Reel", callback_data="help_download"),
            InlineKeyboardButton("🔍 Profile & QR Code", callback_data="help_lookup")
        ],
        [
            InlineKeyboardButton("📸 Story Saver", callback_data="help_story"),
            InlineKeyboardButton("🎯 Target Tracker", callback_data="help_tracking")
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
        "💎 <b>𝕴𝖓𝖘𝖙𝖆𝖌𝖗𝖆𝖒 𝖀𝖑𝖙𝖗𝖆 𝕾𝖚𝖎𝖙𝖊</b> 💎\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        "👑 <b>YOUR ENTERPRISE INSTAGRAM SUITE</b>\n\n"
        "⚡ <b>Quick Operations:</b>\n"
        "▸ 🎥 Paste any <b>Reel / Video Link</b> to extract HD media.\n"
        "▸ 👤 Send <code>@username</code> for HD Avatar, Analytics & QR Code.\n"
        "▸ 📸 Send <code>/story username</code> to fetch active Stories.\n"
        "▸ 🎯 Send <code>/track username</code> to initiate Live Surveillance.\n\n"
        "<b>Select a menu option below to explore commands:</b>"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=main_menu_keyboard())

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help_download":
        await query.message.reply_text("📥 <b>𝕸𝖊𝖉𝖎𝖆 𝕰𝖝𝖙𝖗𝖆𝖈𝖙𝖔𝖗:</b>\nPaste any public Instagram Reel or Post link directly in this chat to receive high-definition media.", parse_mode="HTML")
    elif query.data == "help_lookup":
        await query.message.reply_text("🔍 <b>𝕻𝖗𝖔𝖋𝖎𝖑𝖊 𝕴𝖓𝖙𝖊𝖑𝖑𝖎𝖌𝖊𝖓𝖈𝖊:</b>\nSend any <code>@username</code> to generate deep profile analytics, HD avatar, direct portal link, and a custom QR code.", parse_mode="HTML")
    elif query.data == "help_story":
        await query.message.reply_text("📸 <b>𝕾𝖙𝖔𝖗𝖞 𝕬𝖗𝖈𝖍𝖎𝖛𝖊𝖗:</b>\nSyntax: <code>/story username</code>\n(Example: <code>/story cristiano</code>)", parse_mode="HTML")
    elif query.data == "help_tracking":
        await query.message.reply_text(
            "🎯 <b>𝕾𝖚𝖗𝖛𝖊𝖎𝖑𝖑𝖆𝖓𝖈𝖊 𝕮𝖔𝖓𝖙𝖗𝖔𝖑:</b>\n"
            "• <code>/track username</code> — Activate live surveillance\n"
            "• <code>/untrack username</code> — Terminate tracking\n"
            "• <code>/pause username</code> — Pause live alerts\n"
            "• <code>/resume username</code> — Resume live alerts", 
            parse_mode="HTML"
        )
    elif query.data == "list_targets":
        await tracking_list_cmd(query, context)
    elif query.data == "bot_status":
        await query.message.reply_text(
            "⚡ <b>𝕾𝖞𝖘𝖙𝖊𝖒 𝕾𝖙𝖆𝖙𝖚𝖘:</b> 🟢 ONLINE\n"
            "<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            "🖥️ <b>Host:</b> Render Free Web Engine\n"
            "🔄 <b>Session Manager:</b> Multi-Account Pool Active", 
            parse_mode="HTML"
        )

# ================= 📥 DOWNLOADER & PROFILE LOOKUP =================

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # 1. Video/Reel Downloader
    if "instagram.com" in text:
        msg = await update.message.reply_text("⏳ <b>[ 𝕻𝖗𝖔𝖈𝖊𝖘𝖘𝖎𝖓𝖌 ]</b> <i>Extracting High-Definition Stream...</i>", parse_mode="HTML")
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
                    caption="✨ <b>Media Extracted via Insta Ultra Suite</b> 🚀",
                    parse_mode="HTML"
                )
            if os.path.exists(file_name):
                os.remove(file_name)
            await msg.delete()
        except Exception as e:
            logger.error(f"Download Error: {e}")
            await msg.edit_text("❌ <b>Extraction Failed!</b> The post may be private or the link is invalid.", parse_mode="HTML")
            if os.path.exists(file_name):
                os.remove(file_name)

    # 2. Profile Lookup, HD DP, Direct Link & QR Code Generator
    elif text.startswith("@"):
        username = text.replace("@", "").strip()
        msg = await update.message.reply_text("🔍 <b>[ 𝕬𝖓𝖆𝖑𝖞𝖟𝖎𝖓𝖌 ]</b> <i>Gathering Profile Analytics & QR...</i>", parse_mode="HTML")
        
        cl = get_insta_client()
        if not cl:
            await msg.edit_text("⚠️ <b>System Alert:</b> Multi-account pool unavailable. Basic download engine active.", parse_mode="HTML")
            return

        try:
            user_info = cl.user_info_by_username(username)
            profile_url = f"https://instagram.com/{user_info.username}"
            qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={profile_url}"

            caption = (
                f"👑 <b>𝕻𝖗𝖔𝖋𝖎𝖑𝖊 𝕴𝖓𝖙𝖊𝖑𝖑𝖎𝖌𝖊𝖓𝖈𝖊</b> 👑\n"
                f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                f"👤 <b>Full Name:</b> {user_info.full_name}\n"
                f"🆔 <b>Handle:</b> @{user_info.username}\n"
                f"👥 <b>Followers:</b> {user_info.follower_count:,}\n"
                f"➡️ <b>Following:</b> {user_info.following_count:,}\n"
                f"📮 <b>Posts Count:</b> {user_info.media_count:,}\n"
                f"🔒 <b>Privacy Status:</b> {'Private 🔒' if user_info.is_private else 'Public 🔓'}\n"
                f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                f"📝 <b>Biography:</b>\n<i>{user_info.biography if user_info.biography else 'N/A'}</i>"
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 Open Direct Profile", url=profile_url)]
            ])

            # Send HD DP
            await update.message.reply_photo(
                photo=str(user_info.profile_pic_url_hd),
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )

            # Send Profile QR Code
            await update.message.reply_photo(
                photo=qr_api_url,
                caption=f"📱 <b>𝕼𝕽 𝕬𝖈𝖈𝖊𝖘𝖘 𝕮𝖆𝖗𝖉</b>\n<code>Scan to open @{user_info.username}'s profile directly</code>",
                parse_mode="HTML"
            )

            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ <b>Analysis Failed:</b> Unable to fetch profile for @{username}.", parse_mode="HTML")

async def story_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/story username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "")
    msg = await update.message.reply_text(f"📸 <b>[ 𝕾𝖈𝖆𝖓𝖓𝖎𝖓𝖌 ]</b> <i>Fetching active stories for @{username}...</i>", parse_mode="HTML")

    cl = get_insta_client()
    if not cl:
        await msg.edit_text("⚠️ <b>Session Error:</b> Instagram session pool required for Stories.", parse_mode="HTML")
        return

    try:
        user_id = cl.user_id_from_username(username)
        stories = cl.user_stories(user_id)
        if not stories:
            await msg.edit_text("📭 <b>No active stories found for this profile.</b>", parse_mode="HTML")
            return

        for story in stories:
            url = story.video_url if story.media_type == 2 else story.thumbnail_url
            if story.media_type == 2:
                await update.message.reply_video(video=str(url), caption=f"📸 <b>Story Stream:</b> @{username}")
            else:
                await update.message.reply_photo(photo=str(url), caption=f"📸 <b>Story Image:</b> @{username}")
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ <b>Error:</b> Unable to fetch stories: {e}", parse_mode="HTML")

# ================= 🎯 LIVE TARGET TRACKING ENGINE =================

async def track_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/track username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "").lower()
    chat_id = str(update.effective_chat.id)

    cl = get_insta_client()
    if not cl:
        await update.message.reply_text("❌ <b>Session Pool Error:</b> Multi-account setup required for live surveillance.")
        return

    msg = await update.message.reply_text(f"🎯 <b>[ 𝕴𝖓𝖎𝖙𝖎𝖆𝖑𝖎𝖟𝖎𝖓𝖌 ]</b> <i>Configuring tracking parameters for @{username}...</i>", parse_mode="HTML")
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
            f"🎯 <b>𝕾𝖚𝖗𝖛𝖊𝖎𝖑𝖑𝖆𝖓𝖈𝖊 𝕬𝖈𝖙𝖎𝖛𝖆𝖙𝖊𝖉!</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"👤 <b>Target:</b> @{username}\n"
            f"👥 <b>Initial Followers:</b> {user_info.follower_count:,}\n"
            f"➡️ <b>Initial Following:</b> {user_info.following_count:,}\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"🔔 <b>Status:</b> Live automated surveillance initiated. Updates will be delivered instantly.",
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
        await update.message.reply_text(f"🛑 <b>Surveillance Terminated for @{username}</b>", parse_mode="HTML")
    else:
        await update.message.reply_text("⚠️ <b>Target Not Found:</b> Username is not in your tracking registry.")

async def pause_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/pause username</code>", parse_mode="HTML")
        return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()

    if username in data:
        data[username]["status"] = "paused"
        save_tracking_data(data)
        await update.message.reply_text(f"⏸️️ <b>Surveillance Paused for @{username}</b>", parse_mode="HTML")

async def resume_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/resume username</code>", parse_mode="HTML")
        return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()

    if username in data:
        data[username]["status"] = "active"
        save_tracking_data(data)
        await update.message.reply_text(f"▶️ <b>Surveillance Resumed for @{username}</b>", parse_mode="HTML")

async def tracking_list_cmd(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    data = load_tracking_data()
    if not data:
        msg = "📭 <b>No active tracking targets registered.</b>"
    else:
        msg = "📊 <b>𝕬𝖈𝖙𝖎𝖛𝖊 𝕾𝖚𝖗𝖛𝖊𝖎𝖑𝖑𝖆𝖓𝖈𝖊 𝕽𝖊𝖌𝖎𝖘𝖙𝖗𝖞:</b>\n<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        for user, info in data.items():
            status_icon = "🟢 Active" if info.get("status") == "active" else "⏸️ Paused"
            msg += f"• <b>@{user}</b> │ Status: {status_icon}\n"

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
                    f"🚨 <b>𝕾𝖚𝖗𝖛𝖊𝖎𝖑𝖑𝖆𝖓𝖈𝖊 𝕬𝖑𝖊𝖗𝖙 — @{username}</b> {icon}\n"
                    f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                    f"👥 <b>Followers Activity:</b>\n"
                    f"<code>{old_f:,}</code> ➔ <b>{new_f:,}</b> ({diff:+d})"
                )
                await context.bot.send_message(chat_id=chat_id, text=alert_msg, parse_mode="HTML")
                data[username]["followers"] = new_f

            # Following Alert
            if new_fg != old_fg:
                diff = new_fg - old_fg
                alert_msg = (
                    f"🚨 <b>𝕾𝖚𝖗𝖛𝖊𝖎𝖑𝖑𝖆𝖓𝖈𝖊 𝕬𝖑𝖊𝖗𝖙 — @{username}</b> 🔄\n"
                    f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                    f"➡️ <b>Following Activity:</b>\n"
                    f"<code>{old_fg:,}</code> ➔ <b>{new_fg:,}</b> ({diff:+d})"
                )
                await context.bot.send_message(chat_id=chat_id, text=alert_msg, parse_mode="HTML")
                data[username]["following"] = new_fg

            save_tracking_data(data)
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Tracking check error for {username}: {e}")

# ================= 🚀 MAIN LAUNCHER =================

async def post_init_setup(application):
    commands = [
        BotCommand("start", "Start Bot & Open Suite"),
        BotCommand("story", "Download Instagram Story"),
        BotCommand("track", "Activate Surveillance"),
        BotCommand("untrack", "Terminate Surveillance"),
        BotCommand("pause", "Pause Surveillance Alerts"),
        BotCommand("resume", "Resume Surveillance Alerts"),
        BotCommand("tracking", "List All Surveillance Targets")
    ]
    await application.bot.set_my_commands(commands)

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
