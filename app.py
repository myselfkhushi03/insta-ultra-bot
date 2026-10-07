#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👑 INSTAGRAM ULTRA SUITE (CRASH-PROOF EDITION) - PART 1
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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_START_TIME = datetime.now()
ADMIN_ID = 8536757095

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

def save_tracking_data(data):
    try:
        with open(TRACKING_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving tracking data: {e}")

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def human_delay(min_sec=2, max_sec=4):
    time.sleep(random.uniform(min_sec, max_sec))

def get_insta_client(bot_id=None):
    accounts = load_accounts()
    if not accounts:
        return None, None
    selected_acc = accounts[0]
    try:
        cl = Client()
        if "sessionid" in selected_acc and selected_acc["sessionid"]:
            cl.login_by_sessionid(selected_acc["sessionid"])
        else:
            cl.login(selected_acc["username"], selected_acc["password"])
        human_delay(1, 2)
        return cl, selected_acc
    except Exception as e:
        logger.error(f"Client Init Error: {e}")
        return None, selected_acc
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👑 INSTAGRAM ULTRA SUITE - PART 2
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        uptime = datetime.now() - BOT_START_TIME
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        accounts = load_accounts()
        targets_count = len(load_tracking_data())
        status_text = (
            "⚡ <b>SYSTEM HEALTH & STATUS</b>\n"
            f"🟢 <b>Status:</b> Online 24/7\n"
            f"⏱️ <b>Uptime:</b> {hours}h {minutes}m {seconds}s\n"
            f"🔑 <b>Registered Bots:</b> {len(accounts)} Accounts\n"
            f"🎯 <b>Tracking Targets:</b> {targets_count} Accounts\n"
        )
        await update.message.reply_text(status_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Status Error: {e}")

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data_code = query.data
        if data_code == "help_download":
            await query.message.reply_text("🎬 Paste any public Instagram Reel or Post link directly in chat.", parse_mode="HTML")
        elif data_code == "help_audio":
            await query.message.reply_text("🎵 Send <code>/audio (link)</code>", parse_mode="HTML")
        elif data_code.startswith("req_follow_"):
            username = data_code.replace("req_follow_", "")
            cl, _ = get_insta_client()
            if cl:
                user_info = cl.user_info_by_username(username)
                cl.user_follow(user_info.pk)
                await query.message.edit_text(f"✅ Follow Request Sent to @{username}!", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Callback Error: {e}")

# Admin Commands
async def login_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/login username password</code>", parse_mode="HTML")
        return
    username, password = context.args[0], context.args[1]
    try:
        cl = Client()
        cl.login(username, password)
        accounts = load_accounts()
        new_acc = {"bot_id": f"BOT{len(accounts)+1}", "username": username, "password": password, "sessionid": cl.sessionid}
        accounts.append(new_acc)
        save_accounts(accounts)
        await update.message.reply_text(f"🎉 Logged in @{username} successfully!", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Login Failed: {e}", parse_mode="HTML")

async def accounts_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    accounts = load_accounts()
    await update.message.reply_text(f"📊 Total accounts registered: {len(accounts)}", parse_mode="HTML")

async def set_insta_name_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    new_name = " ".join(context.args)
    cl, _ = get_insta_client()
    if cl:
        info = cl.account_info()
        cl.account_edit(full_name=new_name, biography=info.biography, username=info.username)
        await update.message.reply_text(f"✅ Name changed to {new_name}", parse_mode="HTML")

async def set_insta_bio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    new_bio = " ".join(context.args)
    cl, _ = get_insta_client()
    if cl:
        info = cl.account_info()
        cl.account_edit(full_name=info.full_name, biography=new_bio, username=info.username)
        await update.message.reply_text("✅ Bio updated!", parse_mode="HTML")

async def set_insta_username_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    new_username = re.sub(r'[^a-zA-Z0-9_.]', '', context.args[0].replace("@", ""))
    cl, _ = get_insta_client()
    if cl:
        info = cl.account_info()
        cl.account_edit(full_name=info.full_name, biography=info.biography, username=new_username)
        accounts = load_accounts()
        if accounts:
            accounts[0]["username"] = new_username
            accounts[0]["sessionid"] = cl.sessionid
            save_accounts(accounts)
        await update.message.reply_text(f"✅ Username changed to @{new_username}", parse_mode="HTML")

async def set_insta_dp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not update.message.photo: return
    photo_file = await update.message.photo[-1].get_file()
    file_path = os.path.join(DOWNLOAD_FOLDER, f"dp.jpg")
    await photo_file.download_to_drive(file_path)
    cl, _ = get_insta_client()
    if cl:
        cl.account_change_profile_picture(file_path)
        await update.message.reply_text("✅ DP Changed!", parse_mode="HTML")
    if os.path.exists(file_path): os.remove(file_path)
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👑 INSTAGRAM ULTRA SUITE - PART 3
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def audio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("⚠️ Usage: <code>/audio link</code>", parse_mode="HTML")
            return
        url = context.args[0]
        msg = await update.message.reply_text("🎵 Extracting audio...", parse_mode="HTML")
        download_template = os.path.join(DOWNLOAD_FOLDER, f"%(title)s.%(ext)s")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'outtmpl': download_template,
            'quiet': True
        }
        out_file = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            song_title = info.get('title', 'Audio')
            for f in os.listdir(DOWNLOAD_FOLDER):
                if f.endswith(".mp3"):
                    out_file = os.path.join(DOWNLOAD_FOLDER, f)
                    break
        if out_file and os.path.exists(out_file):
            with open(out_file, 'rb') as audio_doc:
                await update.message.reply_audio(audio=audio_doc, title=song_title)
            os.remove(out_file)
        await msg.delete()
    except Exception as e:
        logger.error(f"Audio Error: {e}")

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip() if update.message.text else ""
        if "instagram.com" in text:
            msg = await update.message.reply_text("⏳ Downloading media...", parse_mode="HTML")
            file_name = os.path.join(DOWNLOAD_FOLDER, f"insta.mp4")
            ydl_opts = {'format': 'best', 'outtmpl': file_name, 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([text])
            with open(file_name, 'rb') as video:
                await update.message.reply_video(video=video)
            if os.path.exists(file_name): os.remove(file_name)
            await msg.delete()
        elif text.startswith("@"):
            username = text.replace("@", "").strip()
            cl, _ = get_insta_client()
            if cl:
                user_info = cl.user_info_by_username(username)
                caption = f"👤 @{user_info.username}\nFollowers: {user_info.follower_count}"
                await update.message.reply_photo(photo=str(user_info.profile_pic_url_hd), caption=caption)
    except Exception as e:
        logger.error(f"Text Handler Error: {e}")

async def followers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    username = context.args[0].replace("@", "")
    cl, _ = get_insta_client()
    if cl:
        user_info = cl.user_info_by_username(username)
        followers_dict = cl.user_followers(user_info.pk, amount=50)
        file_path = f"{username}_followers.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            for uid, uinfo in followers_dict.items():
                f.write(f"@{uinfo.username}\n")
        with open(file_path, "rb") as doc:
            await update.message.reply_document(document=doc)
        if os.path.exists(file_path): os.remove(file_path)

async def following_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    username = context.args[0].replace("@", "")
    cl, _ = get_insta_client()
    if cl:
        user_info = cl.user_info_by_username(username)
        following_dict = cl.user_following(user_info.pk, amount=50)
        file_path = f"{username}_following.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            for uid, uinfo in following_dict.items():
                f.write(f"@{uinfo.username}\n")
        with open(file_path, "rb") as doc:
            await update.message.reply_document(document=doc)
        if os.path.exists(file_path): os.remove(file_path)

async def story_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    username = context.args[0].replace("@", "")
    cl, _ = get_insta_client()
    if cl:
        user_info = cl.user_info_by_username(username)
        stories = cl.user_stories(user_info.pk)
        for story in stories:
            await update.message.reply_photo(photo=str(story.thumbnail_url))
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👑 INSTAGRAM ULTRA SUITE - PART 4
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def track_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    username = context.args[0].replace("@", "").lower()
    chat_id = str(update.effective_chat.id)
    cl, _ = get_insta_client()
    if not cl: return
    try:
        user_info = cl.user_info_by_username(username)
        if user_info.is_private:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Send Follow Request", callback_data=f"req_follow_{username}")]])
            await update.message.reply_text(f"🔒 Private profile @{username}. Click to request follow:", reply_markup=keyboard)
            return
        data = load_tracking_data()
        data[username] = {
            "user_id": str(user_info.pk),
            "chat_id": chat_id,
            "followers": user_info.follower_count,
            "following": user_info.following_count,
            "status": "active"
        }
        save_tracking_data(data)
        await update.message.reply_text(f"🎯 Surveillance activated for @{username}!", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Track Error: {e}")

async def untrack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    username = context.args[0].replace("@", "").lower()
    data = load_tracking_data()
    if username in data:
        del data[username]
        save_tracking_data(data)
        await update.message.reply_text(f"🛑 Stopped tracking @{username}")

async def tracking_list_cmd(update, context: ContextTypes.DEFAULT_TYPE):
    data = load_tracking_data()
    msg = "📊 Active Targets:\n" + "\n".join([f"• @{u}" for u in data])
    await update.message.reply_text(msg)

async def tracking_background_task(context: ContextTypes.DEFAULT_TYPE):
    try:
        data = load_tracking_data()
        if not data: return
        cl, _ = get_insta_client()
        if not cl: return
        for username, info in list(data.items()):
            chat_id = info.get("chat_id")
            user_info = cl.user_info_by_username(username)
            old_f = info.get("followers", 0)
            if user_info.follower_count != old_f:
                await context.bot.send_message(chat_id=chat_id, text=f"🚨 @{username} followers changed: {old_f} ➔ {user_info.follower_count}")
                data[username]["followers"] = user_info.follower_count
                save_tracking_data(data)
    except Exception as e:
        logger.error(f"Background task error: {e}")

async def post_init_setup(application):
    if not scheduler.running:
        scheduler.add_job(tracking_background_task, 'interval', minutes=20, kwargs={'context': application})
        scheduler.start()

def main():
    if not BOT_TOKEN: return
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
    app.add_handler(CommandHandler("tracking", tracking_list_cmd))

    app.add_handler(CommandHandler("login", login_cmd))
    app.add_handler(CommandHandler("accounts", accounts_status_cmd))
    app.add_handler(CommandHandler(["setname", "setinstaname"], set_insta_name_cmd))
    app.add_handler(CommandHandler(["setbio", "setinstabio"], set_insta_bio_cmd))
    app.add_handler(CommandHandler(["setusername", "setinstausername"], set_insta_username_cmd))
    app.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r"^/(setdp|setinstadp)"), set_insta_dp_cmd))

    app.add_handler(CallbackQueryHandler(button_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    logger.info("🤖 Bot is Live!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
