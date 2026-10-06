#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👑 INSTAGRAM ULTRA DOWNLOADER & TRACKER BOT
# 📱 SYSTEM STATUS & MONITORED EDITION (PART 1)
# 🚀 RENDER FREE WEB SERVICE COMPATIBLE
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

# Track Bot Start Time for Uptime
BOT_START_TIME = datetime.now()

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
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

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

# ================= 🤖 HUMAN EMULATION & WARMUP SYSTEM =================
def human_delay(min_sec=3, max_sec=6):
    """Simulates realistic human pause between requests"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

def perform_human_warmup(cl):
    """Simulates browsing feed/explore to prevent bot detection flags"""
    try:
        logger.info("🎬 Human Emulation: Simulating user feed scroll...")
        cl.get_timeline_feed()
        human_delay(2, 4)
    except Exception as e:
        logger.warning(f"⚠️ Warmup simulation skipped: {e}")

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

        human_delay(1, 3)
        perform_human_warmup(cl)

        logger.info(f"✨ Successfully switched to Insta Session: {acc['username']}")
        return cl
    except Exception as e:
        logger.error(f"❌ Account Rotation Error: {e}")
        return None

# ================= 🎨 ULTRA-STYLISH KEYBOARD MENUS =================
def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📥 ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ", callback_data="help_download"),
            InlineKeyboardButton("🔍 ᴘʀᴏғɪʟᴇ & ǫʀ", callback_data="help_lookup")
        ],
        [
            InlineKeyboardButton("📸 sᴛᴏʀʏ sᴀᴠᴇʀ", callback_data="help_story"),
            InlineKeyboardButton("🎯 ᴛᴀʀɢᴇᴛ ᴛʀᴀᴄᴋᴇʀ", callback_data="help_tracking")
        ],
        [
            InlineKeyboardButton("👥 ᴇxᴘᴏʀᴛ ʟɪsᴛs", callback_data="help_export"),
            InlineKeyboardButton("📊 ᴀᴄᴛɪᴠᴇ ᴛᴀʀɢᴇᴛs", callback_data="list_targets")
        ],
        [
            InlineKeyboardButton("⚡ sʏsᴛᴇᴍ sᴛᴀᴛᴜs", callback_data="bot_status")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ================= 🚀 COMMAND HANDLERS =================

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👑 <b>ɪɴsᴛᴀɢʀᴀᴍ ᴜʟᴛʀᴀ sᴜɪᴛᴇ</b>\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        "✨ <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴀssɪsᴛᴀɴᴛ</b>\n\n"
        "⚡ <b>ǫᴜɪᴄᴋ ᴏᴘᴇʀᴀᴛɪᴏɴs:</b>\n"
        "▸ 🎬 Send any <b>ʀᴇᴇʟ / ᴠɪᴅᴇᴏ ʟɪɴᴋ</b> to download.\n"
        "▸ 👤 Send <code>@username</code> for HD DP, Profile Info & QR Link.\n"
        "▸ 📸 Send <code>/story username</code> to fetch active Stories.\n"
        "▸ 🎯 Send <code>/track username</code> for Live Surveillance.\n"
        "▸ 👥 Send <code>/followers username</code> to get Followers TXT.\n"
        "▸ ➡️ Send <code>/following username</code> to get Following TXT.\n"
        "▸ ⚡ Send <code>/status</code> to check Bot Uptime & Health.\n\n"
        "👇 <b>sᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ ғʀᴏᴍ ᴛʜᴇ ᴍᴇɴᴜ ʙᴇʟᴏᴡ:</b>"
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
        "⚡ <b>sʏsᴛᴇᴍ ʜᴇᴀʟᴛʜ & sᴛᴀᴛᴜs</b>\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"🟢 <b>sᴛᴀᴛᴜs:</b> ᴏɴʟɪɴᴇ 24/7\n"
        f"⏱️ <b>ᴜᴘᴛɪᴍᴇ:</b> {hours}h {minutes}m {seconds}s\n"
        f"🔑 <b>ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴs:</b> {session_count} ᴀᴄᴄᴏᴜɴᴛs ᴘᴏᴏʟ\n"
        f"🎯 <b>ᴛʀᴀᴄᴋɪɴɢ ᴛᴀʀɢᴇᴛs:</b> {targets_count} ᴀᴄᴄᴏᴜɴᴛs\n"
        f"🛡 <b>ᴀɴᴛɪ-ᴅᴇᴛᴇᴄᴛɪᴏɴ:</b> ᴀᴄᴛɪᴠᴇ (ʜᴜᴍᴀɴ ᴇᴍᴜʟᴀᴛɪᴏɴ)\n"
        f"🖥️ <b>sᴇʀᴠᴇʀ ʜᴏsᴛ:</b> ʀᴇɴᴅᴇʀ ᴄʟᴏᴜᴅ ᴡᴇʙ sᴇʀᴠɪᴄᴇ\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        "✨ ᴀʟʟ sʏsᴛᴇᴍs ғᴜɴᴄᴛɪᴏɴɪɴɢ ɴᴏʀᴍᴀʟʟʏ!"
    )
    await update.message.reply_text(status_text, parse_mode="HTML")

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help_download":
        await query.message.reply_text("📥 <b>ᴍᴇᴅɪᴀ ᴇxᴛʀᴀᴄᴛᴏʀ</b>\n\nPaste any public Instagram Reel or Post link directly in this chat to receive high-definition media.", parse_mode="HTML")
    elif query.data == "help_lookup":
        await query.message.reply_text("🔍 <b>ᴘʀᴏғɪʟᴇ ɪɴᴛᴇʟʟɪɢᴇɴᴄᴇ</b>\n\nSend any <code>@username</code> to receive profile statistics, HD avatar, direct link, and integrated QR code button.", parse_mode="HTML")
    elif query.data == "help_story":
        await query.message.reply_text("📸 <b>sᴛᴏʀʏ sᴀᴠᴇʀ</b>\n\nSyntax: <code>/story username</code>\n(Example: <code>/story cristiano</code>)", parse_mode="HTML")
    elif query.data == "help_export":
        await query.message.reply_text(
            "👥 <b>ᴇxᴘᴏʀᴛ ᴜsᴇʀ ʟɪsᴛs</b>\n"
            "<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            "• <code>/followers username</code> — Export Followers into TXT File\n"
            "• <code>/following username</code> — Export Following into TXT File",
            parse_mode="HTML"
        )
    elif query.data == "help_tracking":
        await query.message.reply_text(
            "🎯 <b>sᴜʀᴠᴇɪʟʟᴀɴᴄᴇ ᴄᴏɴᴛʀᴏʟ</b>\n"
            "<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            "• <code>/track username</code> — Activate surveillance\n"
            "• <code>/untrack username</code> — Terminate tracking\n"
            "• <code>/pause username</code> — Pause live alerts\n"
            "• <code>/resume username</code> — Resume live alerts", 
            parse_mode="HTML"
        )
    elif query.data == "list_targets":
        await tracking_list_cmd(query, context)
    elif query.data == "bot_status":
        await status_cmd(query, context)

# ================= 📥 DOWNLOADER & PROFILE LOOKUP =================

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "instagram.com" in text:
        msg = await update.message.reply_text("⏳ <i>ᴘʀᴏᴄᴇssɪɴɢ ɪɴsᴛᴀɢʀᴀᴍ ᴍᴇᴅɪᴀ sᴛʀᴇᴀᴍ...</i>", parse_mode="HTML")
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
                    caption="🎬 <b>ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ᴠɪᴀ ɪɴsᴛᴀ ᴜʟᴛʀᴀ sᴜɪᴛᴇ</b> 🚀",
                    parse_mode="HTML"
                )
            if os.path.exists(file_name):
                os.remove(file_name)
            await msg.delete()
        except Exception as e:
            logger.error(f"Download Error: {e}")
            await msg.edit_text("❌ <b>ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ!</b> Post may be private or link is invalid.", parse_mode="HTML")
            if os.path.exists(file_name):
                os.remove(file_name)

    elif text.startswith("@"):
        username = text.replace("@", "").strip()
        msg = await update.message.reply_text("🔍 <i>ғᴇᴛᴄʜɪɴɢ ᴘʀᴏғɪʟᴇ ᴀɴᴀʟʏᴛɪᴄs...</i>", parse_mode="HTML")

        cl = get_insta_client()
        if not cl:
            await msg.edit_text("⚠️ <b>sʏsᴛᴇᴍ ᴀʟᴇʀᴛ:</b> Multi-account pool unavailable.", parse_mode="HTML")
            return

        try:
            human_delay(2, 4)
            user_info = cl.user_info_by_username(username)
            profile_url = f"https://instagram.com/{user_info.username}"
            qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={profile_url}"

            caption = (
                f"👤 <b>ᴘʀᴏғɪʟᴇ ɪɴᴛᴇʟʟɪɢᴇɴᴄᴇ</b>\n"
                f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                f"✨ <b>ғᴜʟʟ ɴᴀᴍᴇ:</b> {user_info.full_name}\n"
                f"🆔 <b>ʜᴀɴᴅʟᴇ:</b> @{user_info.username}\n"
                f"👥 <b>ғᴏʟʟᴏᴡᴇʀs:</b> {user_info.follower_count:,}\n"
                f"➡️ <b>ғᴏʟʟᴏᴡɪɴɢ:</b> {user_info.following_count:,}\n"
                f"📮 <b>ᴘᴏsᴛs ᴄᴏᴜɴᴛ:</b> {user_info.media_count:,}\n"
                f"🔒 <b>ᴘʀɪᴠᴀᴄʏ sᴛᴀᴛᴜs:</b> {'Private 🔒' if user_info.is_private else 'Public 🔓'}\n"
                f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                f"📝 <b>ʙɪᴏɢʀᴀᴘʜʏ:</b>\n<i>{user_info.biography if user_info.biography else 'N/A'}</i>"
            )

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🌐 ᴏᴘᴇɴ ᴅɪʀᴇᴄᴛ ᴘʀᴏғɪʟᴇ", url=profile_url),
                    InlineKeyboardButton("📱 ǫʀ ᴀᴄᴄᴇss ᴄᴀʀᴅ", url=qr_api_url)
                ]
            ])

            await update.message.reply_photo(
                photo=str(user_info.profile_pic_url_hd),
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )

            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ <b>ᴀɴᴀʟʏsɪs ғᴀɪʟᴇᴅ:</b> Unable to fetch profile for @{username}.", parse_mode="HTML")
# ================= 📁 FOLLOWERS & FOLLOWING FILE EXPORTER =================

async def followers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>ᴜsᴀɢᴇ:</b> <code>/followers username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "")
    msg = await update.message.reply_text(f"📄 <i>ғᴇᴛᴄʜɪɴɢ ғᴏʟʟᴏᴡᴇʀs ʟɪsᴛ ғᴏʀ @{username}... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>", parse_mode="HTML")

    cl = get_insta_client()
    if not cl:
        await msg.edit_text("❌ <b>sᴇssɪᴏɴ ᴇʀʀᴏʀ:</b> Multi-account pool required.")
        return

    try:
        user_info = cl.user_info_by_username(username)
        if user_info.is_private:
            await msg.edit_text("🔒 <b>ᴘʀɪᴠᴀᴛᴇ ᴘʀᴏғɪʟᴇ:</b> Cannot fetch followers list for private profiles.", parse_mode="HTML")
            return

        user_id = user_info.pk
        human_delay(2, 4)

        followers_dict = cl.user_followers(user_id, amount=150)

        file_path = f"{username}_followers.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"=== FOLLOWERS LIST FOR @{username} ===\n")
            f.write(f"Total Exported: {len(followers_dict)}\n\n")
            for uid, uinfo in followers_dict.items():
                f.write(f"@{uinfo.username} | Name: {uinfo.full_name}\n")

        with open(file_path, "rb") as doc:
            await update.message.reply_document(
                document=doc,
                caption=f"👥 <b>ғᴏʟʟᴏᴡᴇʀs ᴇxᴘᴏʀᴛ — @{username}</b>\n<code>Total extracted: {len(followers_dict)} accounts</code>",
                parse_mode="HTML"
            )

        if os.path.exists(file_path):
            os.remove(file_path)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ <b>ᴇxᴘᴏʀᴛ ғᴀɪʟᴇᴅ:</b> {e}", parse_mode="HTML")

async def following_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>ᴜsᴀɢᴇ:</b> <code>/following username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "")
    msg = await update.message.reply_text(f"📄 <i>ғᴇᴛᴄʜɪɴɢ ғᴏʟʟᴏᴡɪɴɢ ʟɪsᴛ ғᴏʀ @{username}... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>", parse_mode="HTML")

    cl = get_insta_client()
    if not cl:
        await msg.edit_text("❌ <b>sᴇssɪᴏɴ ᴇʀʀᴏʀ:</b> Multi-account pool required.")
        return

    try:
        user_info = cl.user_info_by_username(username)
        if user_info.is_private:
            await msg.edit_text("🔒 <b>ᴘʀɪᴠᴀᴛᴇ ᴘʀᴏғɪʟᴇ:</b> Cannot fetch following list for private profiles.", parse_mode="HTML")
            return

        user_id = user_info.pk
        human_delay(2, 4)

        following_dict = cl.user_following(user_id, amount=150)

        file_path = f"{username}_following.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"=== FOLLOWING LIST FOR @{username} ===\n")
            f.write(f"Total Exported: {len(following_dict)}\n\n")
            for uid, uinfo in following_dict.items():
                f.write(f"@{uinfo.username} | Name: {uinfo.full_name}\n")

        with open(file_path, "rb") as doc:
            await update.message.reply_document(
                document=doc,
                caption=f"➡️ <b>ғᴏʟʟᴏᴡɪɴɢ ᴇxᴘᴏʀᴛ — @{username}</b>\n<code>Total extracted: {len(following_dict)} accounts</code>",
                parse_mode="HTML"
            )

        if os.path.exists(file_path):
            os.remove(file_path)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ <b>ᴇxᴘᴏʀᴛ ғᴀɪʟᴇᴅ:</b> {e}", parse_mode="HTML")

async def story_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>ᴜsᴀɢᴇ:</b> <code>/story username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "")
    msg = await update.message.reply_text(f"📸 <i>ғᴇᴛᴄʜɪɴɢ ᴀᴄᴛɪᴠᴇ sᴛᴏʀɪᴇs ғᴏʀ @{username}...</i>", parse_mode="HTML")

    cl = get_insta_client()
    if not cl:
        await msg.edit_text("⚠️ <b>sᴇssɪᴏɴ ᴇʀʀᴏʀ:</b> Instagram session pool required.", parse_mode="HTML")
        return

    try:
        human_delay(2, 4)
        user_info = cl.user_info_by_username(username)
        if user_info.is_private:
            await msg.edit_text("🔒 <b>ᴘʀɪᴠᴀᴛᴇ ᴀᴄᴄᴏᴜɴᴛ ᴀʟᴇʀᴛ:</b> Stories cannot be downloaded from private accounts.", parse_mode="HTML")
            return

        user_id = user_info.pk
        stories = cl.user_stories(user_id)
        if not stories:
            await msg.edit_text("📭 <b>ɴᴏ ᴀᴄᴛɪᴠᴇ sᴛᴏʀɪᴇs ғᴏᴜɴᴅ ғᴏʀ ᴛʜɪs ᴘʀᴏғɪʟᴇ.</b>", parse_mode="HTML")
            return

        for story in stories:
            url = story.video_url if story.media_type == 2 else story.thumbnail_url
            if story.media_type == 2:
                await update.message.reply_video(video=str(url), caption=f"📸 <b>sᴛᴏʀʏ sᴛʀᴇᴀᴍ:</b> @{username}")
            else:
                await update.message.reply_photo(photo=str(url), caption=f"📸 <b>sᴛᴏʀʏ ɪᴍᴀɢᴇ:</b> @{username}")
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ <b>ᴇʀʀᴏʀ:</b> Unable to fetch stories: {e}", parse_mode="HTML")

# ================= 🎯 LIVE TARGET TRACKING ENGINE =================

async def track_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>ᴜsᴀɢᴇ:</b> <code>/track username</code>", parse_mode="HTML")
        return

    username = context.args[0].replace("@", "").lower()
    chat_id = str(update.effective_chat.id)

    cl = get_insta_client()
    if not cl:
        await update.message.reply_text("❌ <b>sᴇssɪᴏɴ ᴇʀʀᴏʀ:</b> Multi-account setup required.")
        return

    msg = await update.message.reply_text(f"🎯 <i>ᴀᴄᴛɪᴠᴀᴛɪɴɢ ᴛʀᴀᴄᴋɪɴɢ ᴇɴɢɪɴᴇ ғᴏʀ @{username}...</i>", parse_mode="HTML")
    try:
        human_delay(2, 4)
        user_info = cl.user_info_by_username(username)

        if user_info.is_private:
            await msg.edit_text(
                f"🔒 <b>ᴘʀɪᴠᴀᴛᴇ ᴀᴄᴄᴏᴜɴᴛ ᴀʟᴇʀᴛ</b>\n"
                f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                f"⚠️ <b>ᴛᴀʀɢᴇᴛ:</b> @{username}\n\n"
                f"❌ Tracking and live surveillance are <b>NOT possible</b> on private profiles due to Instagram privacy restrictions.",
                parse_mode="HTML"
            )
            return

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
            f"🎯 <b>sᴜʀᴠᴇɪʟʟᴀɴᴄᴇ ᴀᴄᴛɪᴠᴀᴛᴇᴅ</b>\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"👤 <b>ᴛᴀʀɢᴇᴛ:</b> @{username}\n"
            f"👥 <b>ɪɴɪᴛɪᴀʟ ғᴏʟʟᴏᴡᴇʀs:</b> {user_info.follower_count:,}\n"
            f"➡️ <b>ɪɴɪᴛɪᴀʟ ғᴏʟʟᴏᴡɪɴɢ:</b> {user_info.following_count:,}\n"
            f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"🔔 Live surveillance is active. You will receive real-time alerts upon any changes (Stories, Posts, Followers, Following).",
            parse_mode="HTML"
        )
    except Exception as e:
        await msg.edit_text(f"❌ <b>ᴛʀᴀᴄᴋɪɴɢ ғᴀɪʟᴇᴅ:</b> {e}", parse_mode="HTML")

async def untrack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>ᴜsᴀɢᴇ:</b> <code>/untrack username</code>", parse_mode="HTML")
        return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()

    if username in data:
        del data[username]
        save_tracking_data(data)
        await update.message.reply_text(f"🛑 <b>sᴜʀᴠᴇɪʟʟᴀɴᴄᴇ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ ғᴏʀ @{username}</b>", parse_mode="HTML")
    else:
        await update.message.reply_text("⚠️ <b>ᴛᴀʀɢᴇᴛ ɴᴏᴛ ғᴏᴜɴᴅ:</b> Username is not in your tracking registry.")

async def pause_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>ᴜsᴀɢᴇ:</b> <code>/pause username</code>", parse_mode="HTML")
        return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()

    if username in data:
        data[username]["status"] = "paused"
        save_tracking_data(data)
        await update.message.reply_text(f"⏸ <b>sᴜʀᴠᴇɪʟʟᴀɴᴄᴇ ᴘᴀᴜsᴇᴅ ғᴏʀ @{username}</b>", parse_mode="HTML")

async def resume_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ <b>ᴜsᴀɢᴇ:</b> <code>/resume username</code>", parse_mode="HTML")
        return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()

    if username in data:
        data[username]["status"] = "active"
        save_tracking_data(data)
        await update.message.reply_text(f"▶️ <b>sᴜʀᴠᴇɪʟʟᴀɴᴄᴇ ʀᴇsᴜᴍᴇᴅ ғᴏʀ @{username}</b>", parse_mode="HTML")

async def tracking_list_cmd(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    data = load_tracking_data()
    if not data:
        msg = "📭 <b>ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛʀᴀᴄᴋɪɴɢ ᴛᴀʀɢᴇᴛs ʀᴇɢɪsᴛᴇʀᴇᴅ.</b>"
    else:
        msg = "📊 <b>ᴀᴄᴛɪᴠᴇ sᴜʀᴠᴇɪʟʟᴀɴᴄᴇ ʀᴇɢɪsᴛʀʏ</b>\n<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        for user, info in data.items():
            status_icon = "🟢 Active" if info.get("status") == "active" else "⏸️ Paused"
            msg += f"• <b>@{user}</b> │ Status: {status_icon}\n"

    if hasattr(update_or_query, 'message'):
        await update_or_query.message.reply_text(msg, parse_mode="HTML")
    else:
        await update_or_query.message.reply_text(msg, parse_mode="HTML")

# --- BACKGROUND TRACKING TASK ---
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
            human_delay(3, 8)
            user_id = info.get("user_id")
            if not user_id:
                user_info = cl.user_info_by_username(username)
                user_id = str(user_info.pk)
                info["user_id"] = user_id

            user_info = cl.user_info_by_username(username)

            old_f = info.get("followers", 0)
            new_f = user_info.follower_count

            old_fg = info.get("following", 0)
            new_fg = user_info.following_count

            chat_id = info.get("chat_id")

            # 1. FOLLOWER CHANGE ALERT
            if new_f != old_f:
                diff = new_f - old_f
                icon = "📈" if diff > 0 else "📉"
                alert_msg = (
                    f"🚨 <b>sᴜʀᴠᴇɪʟʟᴀɴᴄᴇ ᴀʟᴇʀᴛ — @{username}</b> {icon}\n"
                    f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                    f"👥 <b>ғᴏʟʟᴏᴡᴇʀs ᴄʜᴀɴɢᴇᴅ:</b>\n"
                    f"<code>{old_f:,}</code> ➔ <b>{new_f:,}</b> ({diff:+d})"
                )
                await context.bot.send_message(chat_id=chat_id, text=alert_msg, parse_mode="HTML")
                data[username]["followers"] = new_f

            # 2. FOLLOWING CHANGE ALERT
            if new_fg != old_fg:
                diff = new_fg - old_fg
                alert_msg = (
                    f"🚨 <b>sᴜʀᴠᴇɪʟʟᴀɴᴄᴇ ᴀʟᴇʀᴛ — @{username}</b> 🔄\n"
                    f"<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                    f"➡️ <b>ғᴏʟʟᴏᴡɪɴɢ ᴄʜᴀɴɢᴇᴅ:</b>\n"
                    f"<code>{old_fg:,}</code> ➔ <b>{new_fg:,}</b> ({diff:+d})"
                )
                await context.bot.send_message(chat_id=chat_id, text=alert_msg, parse_mode="HTML")
                data[username]["following"] = new_fg

            # 3. AUTOMATIC NEW STORY DOWNLOAD & ALERT
            seen_stories = info.get("seen_stories", [])
            active_stories = cl.user_stories(user_id)

            for story in active_stories:
                story_pk = str(story.pk)
                if story_pk not in seen_stories:
                    file_path = cl.story_download(story.pk, folder=DOWNLOAD_FOLDER)
                    caption = f"🚨 <b>ɴᴇᴡ sᴛᴏʀʏ ᴅᴇᴛᴇᴄᴛᴇᴅ!</b>\n👤 <b>Target:</b> @{username}"

                    if str(file_path).endswith(".mp4"):
                        with open(file_path, "rb") as vf:
                            await context.bot.send_video(chat_id=chat_id, video=vf, caption=caption, parse_mode="HTML")
                    else:
                        with open(file_path, "rb") as pf:
                            await context.bot.send_photo(chat_id=chat_id, photo=pf, caption=caption, parse_mode="HTML")

                    seen_stories.append(story_pk)
                    if os.path.exists(file_path):
                        os.remove(file_path)

            data[username]["seen_stories"] = seen_stories

            # 4. AUTOMATIC NEW POST/REEL DETECT & ALERT
            seen_posts = info.get("seen_posts", [])
            recent_posts = cl.user_medias(user_id, amount=3)

            for post in recent_posts:
                post_pk = str(post.pk)
                if post_pk not in seen_posts:
                    file_path = cl.media_download(post.pk, folder=DOWNLOAD_FOLDER)
                    caption = f"🚨 <b>ɴᴇᴡ ᴘᴏsᴛ / ʀᴇᴇʟ ᴅᴇᴛᴇᴄᴛᴇᴅ!</b>\n👤 <b>Target:</b> @{username}"

                    if str(file_path).endswith(".mp4"):
                        with open(file_path, "rb") as vf:
                            await context.bot.send_video(chat_id=chat_id, video=vf, caption=caption, parse_mode="HTML")
                    else:
                        with open(file_path, "rb") as pf:
                            await context.bot.send_photo(chat_id=chat_id, photo=pf, caption=caption, parse_mode="HTML")

                    seen_posts.append(post_pk)
                    if os.path.exists(file_path):
                        os.remove(file_path)

            data[username]["seen_posts"] = seen_posts

            save_tracking_data(data)
        except Exception as e:
            logger.error(f"Tracking check error for {username}: {e}")

# ================= 🚀 MAIN LAUNCHER =================

async def post_init_setup(application):
    commands = [
        BotCommand("start", "Start Bot & Open Suite"),
        BotCommand("status", "Check Live System Status & Uptime"),
        BotCommand("followers", "Export Followers to TXT File"),
        BotCommand("following", "Export Following to TXT File"),
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

    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init_setup).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
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
