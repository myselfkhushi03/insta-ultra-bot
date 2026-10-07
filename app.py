#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👑 INSTAGRAM ULTRA SUITE (CRASH-PROOF EDITION)
# 🚀 RENDER CLOUD 24/7 COMPATIBLE
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import json
import time
import random
import logging
import asyncio
import re
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
    BotCommand,
    BotCommandScopeChat
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

# ================= 👑 ADMIN CONFIGURATION =================
ADMIN_ID = 8536757095  # Authorized Admin Telegram User ID

# ================= 🌐 WEB SERVER FOR RENDER =================
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "⚡ Instagram Ultra Bot is Active & Running 24/7!"

def run_flask():
    try:
        port = int(os.environ.get("PORT", 8080))
        web_app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Flask Web Server Error: {e}")

# ================= 👑 CONFIG & DATA FILES =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ACCOUNTS_FILE = "accounts.json"
TRACKING_FILE = "tracking_data.json"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

scheduler = AsyncIOScheduler()

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    try:
        with open(ACCOUNTS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading accounts: {e}")
        return []

def save_accounts(data):
    try:
        with open(ACCOUNTS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving accounts: {e}")

def load_tracking_data():
    if not os.path.exists(TRACKING_FILE):
        return {}
    try:
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading tracking data: {e}")
        return {}

def save_tracking_data(data):
    try:
        with open(TRACKING_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving tracking data: {e}")

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

# ================= 🤖 HUMAN EMULATION & CLIENT GETTER =================
def human_delay(min_sec=2, max_sec=4):
    time.sleep(random.uniform(min_sec, max_sec))

def get_insta_client(bot_id=None):
    accounts = load_accounts()
    if not accounts:
        return None, None

    selected_acc = None
    if bot_id and bot_id.upper() != "ALL":
        for acc in accounts:
            if acc.get("bot_id", "").upper() == bot_id.upper():
                selected_acc = acc
                break
        if not selected_acc:
            return None, None
    else:
        selected_acc = random.choice(accounts)

    try:
        cl = Client()
        if "sessionid" in selected_acc and selected_acc["sessionid"]:
            cl.login_by_sessionid(selected_acc["sessionid"])
        else:
            cl.login(selected_acc["username"], selected_acc["password"])
        human_delay(1, 2)
        return cl, selected_acc
    except Exception as e:
        logger.error(f"Client Init Error for {selected_acc.get('username')}: {e}")
        return None, selected_acc
# ================= 🎨 CLEAN KEYBOARD MENUS & USER COMMANDS =================
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

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
    except Exception as e:
        logger.error(f"Start CMD Error: {e}")
        await update.message.reply_text(f"❌ <b>Error:</b> {e}", parse_mode="HTML")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        uptime = datetime.now() - BOT_START_TIME
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        accounts = load_accounts()
        targets_count = len(load_tracking_data())

        status_text = (
            "⚡ <b>SYSTEM HEALTH & STATUS</b>\n"
            "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            f"🟢 <b>Status:</b> Online 24/7\n"
            f"⏱️ <b>Uptime:</b> {hours}h {minutes}m {seconds}s\n"
            f"🔑 <b>Registered Bots:</b> {len(accounts)} Accounts\n"
            f"🎯 <b>Tracking Targets:</b> {targets_count} Accounts\n"
            f"🛡️ <b>Anti-Ban Guard:</b> Active (Stealth Mode)\n"
            f"🖥️ <b>Server Host:</b> Render Cloud Web Service\n"
            "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            "✨ All systems functioning normally!"
        )
        await update.message.reply_text(status_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Status CMD Error: {e}")
        await update.message.reply_text(f"❌ <b>Status Error:</b> {e}", parse_mode="HTML")

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
        elif data_code.startswith("req_follow_"):
            username = data_code.replace("req_follow_", "")
            cl, acc = get_insta_client()
            if not cl:
                await query.message.reply_text("❌ <b>Session Error:</b> Instagram account pool not available.", parse_mode="HTML")
                return
            
            try:
                user_info = cl.user_info_by_username(username)
                cl.user_follow(user_info.pk)
                
                data = load_tracking_data()
                chat_id = str(query.message.chat.id)
                data[username] = {
                    "user_id": str(user_info.pk),
                    "chat_id": chat_id,
                    "followers": user_info.follower_count,
                    "following": user_info.following_count,
                    "posts": user_info.media_count,
                    "seen_stories": [],
                    "seen_posts": [],
                    "status": "pending_request"
                }
                save_tracking_data(data)
                
                await query.message.edit_text(
                    f"✅ <b>Follow Request Sent!</b>\n\n"
                    f"👤 <b>Target:</b> @{username}\n"
                    f"⏳ Bot is periodically checking for request acceptance. Surveillance will automatically start as soon as it's approved!",
                    parse_mode="HTML"
                )
            except Exception as e:
                await query.message.reply_text(f"❌ <b>Error Sending Request:</b> {e}", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Button Callback Error: {e}")

# ================= 👑 ADMIN COMMANDS & BOT MANAGER =================

async def login_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            return

        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "⚠️ <b>Usage:</b>\n"
                "<code>/login username password</code>\n"
                "<code>/login username password 2fa_code</code> (if 2FA active)",
                parse_mode="HTML"
            )
            return

        username = context.args[0].replace("@", "").strip()
        password = context.args[1].strip()
        two_factor_code = context.args[2].strip() if len(context.args) >= 3 else None

        msg = await update.message.reply_text(f"⏳ <i>Attempting Instagram login for @{username}...</i>", parse_mode="HTML")

        try:
            cl = Client()
            if two_factor_code:
                cl.login(username, password, verification_code=two_factor_code)
            else:
                cl.login(username, password)

            sessionid = cl.sessionid
            accounts = load_accounts()

            bot_id = f"BOT{len(accounts) + 1}"
            for acc in accounts:
                if acc.get("username", "").lower() == username.lower():
                    bot_id = acc.get("bot_id", bot_id)
                    accounts.remove(acc)
                    break

            new_acc = {
                "bot_id": bot_id,
                "username": username,
                "password": password,
                "sessionid": sessionid,
                "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            accounts.append(new_acc)
            save_accounts(accounts)

            await msg.edit_text(
                f"🎉 <b>INSTAGRAM ACCOUNT LOGGED IN!</b>\n"
                f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                f"🆔 <b>Bot ID:</b> <code>{bot_id}</code>\n"
                f"👤 <b>Username:</b> @{username}\n"
                f"🔑 <b>Session ID:</b> Saved Successfully\n"
                f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                f"✅ Ready for operations!",
                parse_mode="HTML"
            )
        except Exception as e:
            err_str = str(e)
            if "two_factor" in err_str.lower() or "2fa" in err_str.lower():
                await msg.edit_text(
                    f"🔒 <b>2FA Verification Required!</b>\n\n"
                    f"Please run command with 2FA code:\n"
                    f"<code>/login {username} {password} YOUR_2FA_CODE</code>",
                    parse_mode="HTML"
                )
            else:
                await msg.edit_text(f"❌ <b>Login Failed:</b>\n<code>{err_str}</code>", parse_mode="HTML")
    except Exception as main_e:
        logger.error(f"Login CMD Main Error: {main_e}")
        await update.message.reply_text(f"❌ <b>Command Error:</b> {main_e}", parse_mode="HTML")

async def accounts_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            return

        msg = await update.message.reply_text("🔍 <i>Checking Instagram accounts pool status...</i>", parse_mode="HTML")
        accounts = load_accounts()

        if not accounts:
            await msg.edit_text("📭 No accounts registered in pool.", parse_mode="HTML")
            return

        res_text = "👑 <b>INSTAGRAM BOTS POOL REGISTRY</b>\n<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        active_cnt = 0
        dead_cnt = 0

        for idx, acc in enumerate(accounts, 1):
            bot_id = acc.get("bot_id", f"BOT{idx}")
            uname = acc.get("username", "Unknown")
            pwd = acc.get("password", "N/A")
            sess = acc.get("sessionid", "")

            status_str = "🔴 Shutdown"
            try:
                cl = Client()
                if sess:
                    cl.login_by_sessionid(sess)
                else:
                    cl.login(uname, pwd)
                info = cl.account_info()
                uname = info.username
                status_str = "🟢 Active"
                active_cnt += 1
            except Exception:
                dead_cnt += 1

            res_text += (
                f"🆔 <b>ID:</b> <code>{bot_id}</code> │ <b>Status:</b> {status_str}\n"
                f"👤 <b>Username:</b> @{uname}\n"
                f"🔑 <b>Password:</b> <code>{pwd}</code>\n"
                f"<code>──────────────────────────────</code>\n"
            )

        res_text += f"\n📊 <b>Total:</b> {len(accounts)} | 🟢 <b>Active:</b> {active_cnt} | 🔴 <b>Shutdown:</b> {dead_cnt}"
        await msg.edit_text(res_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Accounts CMD Error: {e}")
        await update.message.reply_text(f"❌ <b>Failed to fetch accounts:</b> {e}", parse_mode="HTML")
async def set_insta_name_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            return

        if not context.args or len(context.args) < 2:
            await update.message.reply_text("⚠️ <b>Usage:</b> <code>/setinstaname [BOT_ID/ALL] New Name</code>", parse_mode="HTML")
            return

        target_id = context.args[0].upper()
        new_name = " ".join(context.args[1:])

        accounts = load_accounts()
        if not accounts:
            await update.message.reply_text("❌ No bots in pool.", parse_mode="HTML")
            return

        msg = await update.message.reply_text(f"⏳ <i>Updating Name for target: {target_id}...</i>", parse_mode="HTML")
        results = []

        for acc in accounts:
            b_id = acc.get("bot_id", "").upper()
            if target_id == "ALL" or target_id == b_id:
                try:
                    cl, _ = get_insta_client(b_id)
                    if cl:
                        cl.account_edit(full_name=new_name)
                        results.append(f"✅ <b>{b_id} (@{acc['username']}):</b> Name changed to '{new_name}'")
                    else:
                        results.append(f"❌ <b>{b_id}:</b> Client Login Failed")
                except Exception as e:
                    results.append(f"❌ <b>{b_id}:</b> {e}")

        await msg.edit_text("\n".join(results) if results else "❌ Target Bot ID not found.", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Set Name Error: {e}")
        await update.message.reply_text(f"❌ <b>Error:</b> {e}", parse_mode="HTML")

async def set_insta_bio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            return

        if not context.args or len(context.args) < 2:
            await update.message.reply_text("⚠️ <b>Usage:</b> <code>/setinstabio [BOT_ID/ALL] New Bio Text</code>", parse_mode="HTML")
            return

        target_id = context.args[0].upper()
        new_bio = " ".join(context.args[1:])

        accounts = load_accounts()
        if not accounts:
            await update.message.reply_text("❌ No bots in pool.", parse_mode="HTML")
            return

        msg = await update.message.reply_text(f"⏳ <i>Updating Bio for target: {target_id}...</i>", parse_mode="HTML")
        results = []

        for acc in accounts:
            b_id = acc.get("bot_id", "").upper()
            if target_id == "ALL" or target_id == b_id:
                try:
                    cl, _ = get_insta_client(b_id)
                    if cl:
                        cl.set_biography(new_bio)
                        results.append(f"✅ <b>{b_id} (@{acc['username']}):</b> Bio Updated!")
                    else:
                        results.append(f"❌ <b>{b_id}:</b> Client Login Failed")
                except Exception as e:
                    results.append(f"❌ <b>{b_id}:</b> {e}")

        await msg.edit_text("\n".join(results) if results else "❌ Target Bot ID not found.", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Set Bio Error: {e}")
        await update.message.reply_text(f"❌ <b>Error:</b> {e}", parse_mode="HTML")

async def set_insta_username_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            return

        if not context.args or len(context.args) < 2:
            await update.message.reply_text("⚠️ <b>Usage:</b> <code>/setinstausername [BOT_ID] new_username</code>", parse_mode="HTML")
            return

        target_id = context.args[0].upper()
        raw_input = context.args[1].replace("@", "").replace(",", "").strip()
        new_username = re.sub(r'[^a-zA-Z0-9_.]', '', raw_input)

        if target_id == "ALL":
            await update.message.reply_text("⚠️ Cannot set same username for ALL bots. Please specify a single Bot ID (e.g. BOT1).", parse_mode="HTML")
            return

        cl, acc_data = get_insta_client(target_id)
        if not cl:
            await update.message.reply_text(f"❌ Could not login to bot {target_id}.", parse_mode="HTML")
            return

        msg = await update.message.reply_text(f"⏳ <i>Changing username for {target_id} to @{new_username}...</i>", parse_mode="HTML")
        try:
            cl.set_username(new_username)
            
            accounts = load_accounts()
            for a in accounts:
                if a.get("bot_id", "").upper() == target_id:
                    a["username"] = new_username
                    a["sessionid"] = cl.sessionid
                    break
            save_accounts(accounts)

            await msg.edit_text(f"✅ <b>{target_id}:</b> Username successfully changed to <b>@{new_username}</b>", parse_mode="HTML")
        except Exception as e:
            err_msg = str(e)
            if "taken" in err_msg.lower() or "not available" in err_msg.lower():
                await msg.edit_text(f"❌ Username <b>@{new_username}</b> is already taken or unavailable on Instagram.", parse_mode="HTML")
            else:
                await msg.edit_text(f"❌ Username Change Error:\n<code>{err_msg}</code>", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Set Username Error: {e}")
        await update.message.reply_text(f"❌ <b>Error:</b> {e}", parse_mode="HTML")

async def set_insta_dp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            return

        if not update.message.photo:
            await update.message.reply_text("⚠️ Send a photo with caption: <code>/setinstadp [BOT_ID/ALL]</code>", parse_mode="HTML")
            return

        caption = update.message.caption or ""
        parts = caption.split()
        target_id = parts[1].upper() if len(parts) >= 2 else "ALL"

        msg = await update.message.reply_text("⏳ <i>Updating Profile Picture...</i>", parse_mode="HTML")
        photo_file = await update.message.photo[-1].get_file()
        file_path = os.path.join(DOWNLOAD_FOLDER, f"dp_{update.message.message_id}.jpg")
        await photo_file.download_to_drive(file_path)

        accounts = load_accounts()
        results = []

        for acc in accounts:
            b_id = acc.get("bot_id", "").upper()
            if target_id == "ALL" or target_id == b_id:
                try:
                    cl, _ = get_insta_client(b_id)
                    if cl:
                        cl.account_change_profile_picture(file_path)
                        results.append(f"✅ <b>{b_id} (@{acc['username']}):</b> DP Changed!")
                    else:
                        results.append(f"❌ <b>{b_id}:</b> Login Failed")
                except Exception as e:
                    results.append(f"❌ <b>{b_id}:</b> {e}")

        await msg.edit_text("\n".join(results) if results else "❌ Target Bot ID not found.", parse_mode="HTML")
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.error(f"Set DP Error: {e}")
        await update.message.reply_text(f"❌ <b>DP Update Error:</b> {e}", parse_mode="HTML")

# ================= 📥 DOWNLOADER & PROFILE LOOKUP =================

async def audio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("⚠️ <b>Usage:</b> <code>/audio (Reel Link)</code>", parse_mode="HTML")
            return

        url = context.args[0]
        msg = await update.message.reply_text("🎵 <i>Extracting audio stream...</i>", parse_mode="HTML")
        
        download_template = os.path.join(DOWNLOAD_FOLDER, f"%(title)s_{update.message.message_id}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'outtmpl': download_template,
            'quiet': True
        }

        out_file = None
        song_title = "Unknown Audio"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                song_title = info.get('title', 'Instagram_Audio')
                
                clean_title = sanitize_filename(song_title)
                expected_filename = f"{clean_title}_{update.message.message_id}.mp3"
                out_file = os.path.join(DOWNLOAD_FOLDER, expected_filename)

                if not os.path.exists(out_file):
                    for f in os.listdir(DOWNLOAD_FOLDER):
                        if str(update.message.message_id) in f and f.endswith(".mp3"):
                            out_file = os.path.join(DOWNLOAD_FOLDER, f)
                            break

            if out_file and os.path.exists(out_file):
                with open(out_file, 'rb') as audio_doc:
                    await update.message.reply_audio(
                        audio=audio_doc,
                        title=song_title,
                        filename=f"{sanitize_filename(song_title)}.mp3",
                        caption=f"🎵 <b>Song Name:</b> <i>{song_title}</i>\n🚀 Extracted via <b>Insta Suite</b>",
                        parse_mode="HTML"
                    )
                os.remove(out_file)
            else:
                await msg.edit_text("❌ <b>Audio extraction failed!</b> Could not locate audio file.", parse_mode="HTML")

            await msg.delete()
        except Exception as e:
            logger.error(f"Audio command extraction error: {e}")
            await msg.edit_text(f"❌ <b>Extraction failed!</b>\n<code>{e}</code>", parse_mode="HTML")
            if out_file and os.path.exists(out_file):
                os.remove(out_file)
    except Exception as main_e:
        logger.error(f"Audio CMD Error: {main_e}")
        await update.message.reply_text(f"❌ <b>Audio CMD Error:</b> {main_e}", parse_mode="HTML")

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip() if update.message.text else ""

        if "instagram.com" in text:
            msg = await update.message.reply_text("⏳ <i>Processing Instagram media...</i>", parse_mode="HTML")
            file_name = os.path.join(DOWNLOAD_FOLDER, f"insta_{update.message.message_id}.mp4")

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
                await msg.edit_text(f"❌ <b>Download failed!</b>\n<code>{e}</code>", parse_mode="HTML")
                if os.path.exists(file_name):
                    os.remove(file_name)

        elif text.startswith("@"):
            username = text.replace("@", "").strip()
            msg = await update.message.reply_text("🔍 <i>Fetching profile details...</i>", parse_mode="HTML")

            cl, _ = get_insta_client()
            if not cl:
                await msg.edit_text("⚠️ <b>System Alert:</b> Multi-account pool unavailable.", parse_mode="HTML")
                return

            try:
                human_delay(1, 3)
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
                await msg.edit_text(f"❌ <b>Analysis Failed:</b>\n<code>{e}</code>", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Handle Text Error: {e}")
# ================= 📁 EXPORTERS & STORY SAVER =================

async def followers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("⚠️ <b>Usage:</b> <code>/followers username</code>", parse_mode="HTML")
            return

        username = context.args[0].replace("@", "")
        msg = await update.message.reply_text(f"📄 <i>Fetching followers list for @{username}...</i>", parse_mode="HTML")

        cl, _ = get_insta_client()
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
            await msg.edit_text(f"❌ <b>Export Failed:</b>\n<code>{e}</code>", parse_mode="HTML")
    except Exception as main_e:
        logger.error(f"Followers CMD Error: {main_e}")

async def following_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("⚠️ <b>Usage:</b> <code>/following username</code>", parse_mode="HTML")
            return

        username = context.args[0].replace("@", "")
        msg = await update.message.reply_text(f"📄 <i>Fetching following list for @{username}...</i>", parse_mode="HTML")

        cl, _ = get_insta_client()
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
            await msg.edit_text(f"❌ <b>Export Failed:</b>\n<code>{e}</code>", parse_mode="HTML")
    except Exception as main_e:
        logger.error(f"Following CMD Error: {main_e}")

async def story_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("⚠️ <b>Usage:</b> <code>/story username</code>", parse_mode="HTML")
            return

        username = context.args[0].replace("@", "")
        msg = await update.message.reply_text(f"📖 <i>Fetching active stories for @{username}...</i>", parse_mode="HTML")

        cl, _ = get_insta_client()
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
            await msg.edit_text(f"❌ <b>Error:</b>\n<code>{e}</code>", parse_mode="HTML")
    except Exception as main_e:
        logger.error(f"Story CMD Error: {main_e}")

# ================= 🎯 SAFE TARGET TRACKING ENGINE =================

async def track_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("⚠️ <b>Usage:</b> <code>/track username</code>", parse_mode="HTML")
            return

        username = context.args[0].replace("@", "").lower()
        chat_id = str(update.effective_chat.id)

        cl, _ = get_insta_client()
        if not cl:
            await update.message.reply_text("❌ <b>Session Error:</b> Accounts pool required.")
            return

        msg = await update.message.reply_text(f"🎯 <i>Activating tracking engine for @{username}...</i>", parse_mode="HTML")
        try:
            user_info = cl.user_info_by_username(username)

            if user_info.is_private:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Send Follow Request", callback_data=f"req_follow_{username}")]
                ])
                await msg.edit_text(
                    f"🔒 <b>PRIVATE ACCOUNT DETECTED</b>\n"
                    f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                    f"👤 <b>Target:</b> @{username}\n"
                    f"⚠️ Unable to fetch data because profile is private.\n\n"
                    f"👉 Click the button below to send a Follow Request from bot session. Once accepted, surveillance starts automatically!",
                    parse_mode="HTML",
                    reply_markup=keyboard
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
            await msg.edit_text(f"❌ <b>Tracking Failed:</b>\n<code>{e}</code>", parse_mode="HTML")
    except Exception as main_e:
        logger.error(f"Track CMD Main Error: {main_e}")

async def untrack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
    except Exception as e:
        logger.error(f"Untrack Error: {e}")

async def pause_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            return
        username = context.args[0].replace("@", "").lower()
        data = load_tracking_data()
        if username in data:
            data[username]["status"] = "paused"
            save_tracking_data(data)
            await update.message.reply_text(f"⏸ <b>Surveillance paused for @{username}</b>", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Pause CMD Error: {e}")

async def resume_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            return
        username = context.args[0].replace("@", "").lower()
        data = load_tracking_data()
        if username in data:
            data[username]["status"] = "active"
            save_tracking_data(data)
            await update.message.reply_text(f"▶️ <b>Surveillance resumed for @{username}</b>", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Resume CMD Error: {e}")

async def tracking_list_cmd(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = load_tracking_data()
        if not data:
            msg = "📭 <b>No active tracking targets registered.</b>"
        else:
            msg = "📊 <b>ACTIVE SURVEILLANCE REGISTRY</b>\n<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
            for user, info in data.items():
                status = info.get("status")
                if status == "active":
                    status_icon = "🟢 Active"
                elif status == "pending_request":
                    status_icon = "⏳ Follow Req Pending"
                else:
                    status_icon = "⏸️ Paused"
                msg += f"• <b>@{user}</b> │ Status: {status_icon}\n"

        if hasattr(update_or_query, 'message'):
            await update_or_query.message.reply_text(msg, parse_mode="HTML")
        else:
            await update_or_query.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Tracking List Error: {e}")

# --- BACKGROUND STEALTH TRACKING TASK ---
async def tracking_background_task(context: ContextTypes.DEFAULT_TYPE):
    try:
        data = load_tracking_data()
        if not data:
            return

        cl, _ = get_insta_client()
        if not cl:
            return

        for username, info in list(data.items()):
            status = info.get("status")
            chat_id = info.get("chat_id")
            user_id = info.get("user_id")

            if status == "paused":
                continue

            try:
                human_delay(3, 6)
                user_info = cl.user_info_by_username(username)

                if status == "pending_request":
                    can_access = False
                    if not user_info.is_private:
                        can_access = True
                    else:
                        try:
                            cl.user_stories(user_id)
                            can_access = True
                        except Exception:
                            can_access = False

                    if can_access:
                        try:
                            active_stories = cl.user_stories(user_id)
                            initial_story_pks = [str(s.pk) for s in active_stories]
                            recent_posts = cl.user_medias(user_id, amount=3)
                            initial_post_pks = [str(p.pk) for p in recent_posts]

                            data[username]["seen_stories"] = initial_story_pks
                            data[username]["seen_posts"] = initial_post_pks
                            data[username]["followers"] = user_info.follower_count
                            data[username]["following"] = user_info.following_count
                            data[username]["posts"] = user_info.media_count
                            data[username]["status"] = "active"
                            save_tracking_data(data)

                            await context.bot.send_message(
                                chat_id=chat_id,
                                text=f"🎉 <b>FOLLOW REQUEST ACCEPTED!</b>\n"
                                     f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                                     f"👤 <b>Target:</b> @{username}\n"
                                     f"✅ Access granted! Live surveillance has been automatically activated.",
                                parse_mode="HTML"
                            )
                            continue
                        except Exception:
                            continue
                    else:
                        continue

                if data[username].get("status") == "active":
                    old_f, new_f = info.get("followers", 0), user_info.follower_count
                    old_fg, new_fg = info.get("following", 0), user_info.following_count

                    if new_f != old_f:
                        diff = new_f - old_f
                        icon = "📈" if diff > 0 else "📉"
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"🚨 <b>SURVEILLANCE ALERT — @{username}</b> {icon}\nFollowers: <code>{old_f:,}</code> ➔ <b>{new_f:,}</b> ({diff:+d})",
                            parse_mode="HTML"
                        )
                        data[username]["followers"] = new_f

                    if new_fg != old_fg:
                        diff = new_fg - old_fg
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"🚨 <b>SURVEILLANCE ALERT — @{username}</b> 🔄\nFollowing: <code>{old_fg:,}</code> ➔ <b>{new_fg:,}</b> ({diff:+d})",
                            parse_mode="HTML"
                        )
                        data[username]["following"] = new_fg

                    seen_stories = info.get("seen_stories", [])
                    current_stories = cl.user_stories(user_id)
                    for story in current_stories:
                        s_pk = str(story.pk)
                        if s_pk not in seen_stories:
                            story_url = story.video_url if story.media_type == 2 else story.thumbnail_url
                            caption = f"📖 <b>NEW STORY DETECTED!</b>\n👤 Target: @{username}"
                            if story.media_type == 2:
                                await context.bot.send_video(chat_id=chat_id, video=str(story_url), caption=caption, parse_mode="HTML")
                            else:
                                await context.bot.send_photo(chat_id=chat_id, photo=str(story_url), caption=caption, parse_mode="HTML")
                            seen_stories.append(s_pk)
                    data[username]["seen_stories"] = seen_stories

                    seen_posts = info.get("seen_posts", [])
                    current_posts = cl.user_medias(user_id, amount=3)
                    for post in current_posts:
                        p_pk = str(post.pk)
                        if p_pk not in seen_posts:
                            post_url = f"https://instagram.com/p/{post.code}/"
                            post_caption = post.caption_text[:200] if post.caption_text else "No Caption"
                            alert_msg = (
                                f"🎬 <b>NEW POST / REEL DETECTED!</b>\n"
                                f"<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
                                f"👤 <b>Target:</b> @{username}\n"
                                f"📝 <b>Caption:</b> <i>{post_caption}...</i>\n"
                                f"🔗 <b>Link:</b> <a href='{post_url}'>Click Here to View Post</a>"
                            )
                            await context.bot.send_message(chat_id=chat_id, text=alert_msg, parse_mode="HTML")
                            seen_posts.append(p_pk)
                    data[username]["seen_posts"] = seen_posts

                    save_tracking_data(data)
            except Exception as e:
                logger.error(f"Tracking check error for {username}: {e}")
    except Exception as main_bg_e:
        logger.error(f"Background Task Error: {main_bg_e}")

# ================= 🚀 MAIN LAUNCHER =================

async def post_init_setup(application):
    try:
        user_commands = [
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
        await application.bot.set_my_commands(user_commands)

        admin_commands = user_commands + [
            BotCommand("login", "Login IG Account (Admin)"),
            BotCommand("accounts", "Bots Registry & Status (Admin)"),
            BotCommand("setinstaname", "Set Bot Name (Admin)"),
            BotCommand("setinstabio", "Set Bot Bio (Admin)"),
            BotCommand("setinstausername", "Set Bot Username (Admin)")
        ]
        try:
            await application.bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=ADMIN_ID))
        except Exception as e:
            logger.error(f"Admin menu registration error: {e}")

        if not scheduler.running:
            scheduler.add_job(tracking_background_task, 'interval', minutes=20, kwargs={'context': application})
            scheduler.start()
    except Exception as e:
        logger.error(f"Post Init Setup Error: {e}")

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

    # Admin Exclusive Handlers (Clean Commands)
    app.add_handler(CommandHandler("login", login_cmd))
    app.add_handler(CommandHandler("accounts", accounts_status_cmd))
    app.add_handler(CommandHandler(["setname", "setinstaname"], set_insta_name_cmd))
    app.add_handler(CommandHandler(["setbio", "setinstabio"], set_insta_bio_cmd))
    app.add_handler(CommandHandler(["setusername", "setinstausername"], set_insta_username_cmd))
    app.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r"^/(setdp|setinstadp)"), set_insta_dp_cmd))

    app.add_handler(CallbackQueryHandler(button_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    logger.info("🤖 Insta Ultra Bot is Live!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
