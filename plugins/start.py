from datetime import date as date_
import datetime
import os, re
import asyncio
import random
from script import *
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
import time
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import humanize
from helper.progress import humanbytes
from helper.database import botdata, find_one, total_user
from helper.database import insert, used_limit, usertype, uploadlimit, addpredata, total_rename, total_size
from pyrogram.file_id import FileId
from helper.database import daily as daily_
from helper.date import check_expi
from config import *

# 🔥 referral import
from helper.database import update_referral

bot_username = BOT_USERNAME
log_channel = LOG_CHANNEL
token = BOT_TOKEN
botid = token.split(':')[0]


# =========================
# 🔥 VERIFY FUNCTION
# =========================
async def is_joined(client, user_id):
    try:
        member = await client.get_chat_member(FORCE_SUBS, user_id)
        if member.status in ["left", "kicked"]:
            return False
        return True
    except:
        return False


# =========================
# 🚀 START
# =========================
@Client.on_message(filters.private & filters.command(["start"]))
async def start(client, message):
    user_id = message.chat.id
    insert(int(user_id))

    # 🔥 REFERRAL
    try:
        ref_id = message.text.split(' ')[1]
        referrer_id = int(ref_id)
        if referrer_id != user_id:
            update_referral(user_id, referrer_id)
    except:
        pass

    # 🔥 FORCE SUB CHECK
    if FORCE_SUBS:
        if not await is_joined(client, user_id):
            return await message.reply_text(
                "⚠️ Please join our channel and click VERIFY",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_SUBS}")],
                    [InlineKeyboardButton("✅ VERIFY", callback_data="verify")]
                ])
            )

    loading = await message.reply_sticker("CAACAgIAAxkBAALmzGXSSt3ppnOsSl_spnAP8wHC26jpAAJEGQACCOHZSVKp6_XqghKoHgQ")
    await asyncio.sleep(2)
    await loading.delete()

    txt = f"""Hello {message.from_user.mention}

➻ Advanced Rename Bot

➻ Rename Files, Change Thumbnail & Caption

<b>Made By @HxBots</b>"""

    await message.reply_photo(
        photo=BOT_PIC,
        caption=txt,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Updates", url="https://t.me/tbotz_update"),
             InlineKeyboardButton("💬 Support", url="https://t.me/TBOT_CHATS")],
            [InlineKeyboardButton("🛠 Help", callback_data='help'),
             InlineKeyboardButton("❤️ About", callback_data='about')],
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/t4tanjiro")]
        ])
    )


# =========================
# 🔥 VERIFY BUTTON
# =========================
@Client.on_callback_query(filters.regex("verify"))
async def verify(client, query):
    user_id = query.from_user.id

    if not await is_joined(client, user_id):
        return await query.answer("❌ Join channel first!", show_alert=True)

    await query.message.edit_text("✅ Verification Successful! Now send your file.")


# =========================
# 📂 FILE HANDLER
# =========================
@Client.on_message((filters.private & (filters.document | filters.audio | filters.video)) | filters.channel & (filters.document | filters.audio | filters.video))
async def send_doc(client, message):
    user_id = message.from_user.id

    # 🔥 FORCE SUB CHECK
    if FORCE_SUBS:
        if not await is_joined(client, user_id):
            return await message.reply_text(
                "⚠️ Join channel and click VERIFY",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_SUBS}")],
                    [InlineKeyboardButton("✅ VERIFY", callback_data="verify")]
                ])
            )

    botdata(int(botid))
    bot_data = find_one(int(botid))
    prrename = bot_data['total_rename']
    prsize = bot_data['total_size']

    user_deta = find_one(user_id)
    used_date = user_deta["date"]
    buy_date = user_deta["prexdate"]
    daily = user_deta["daily"]
    user_type = user_deta["usertype"]

    c_time = time.time()
    LIMIT = 120 if user_type == "Free" else 10

    then = used_date + LIMIT
    left = round(then - c_time)

    if left > 0:
        await message.reply_text(f"⏳ Wait {left} sec")
        return

    media = await client.get_messages(message.chat.id, message.id)
    file = media.document or media.video or media.audio
    dcid = FileId.decode(file.file_id).dc_id
    filename = file.file_name

    # 🔥 FILE SIZE SYSTEM
    FREE_LIMIT = 2147483648
    PREMIUM_LIMIT = 4294967296

    if user_type == "Free" and file.file_size > FREE_LIMIT:
        await message.reply_text(
            "❌ Free limit 2GB\nUpgrade for 4GB",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Upgrade", callback_data="my_pl_call")]
            ])
        )
        return

    if user_type != "Free" and file.file_size > PREMIUM_LIMIT:
        await message.reply_text("❌ Max 4GB allowed")
        return

    filesize = humanize.naturalsize(file.file_size)

    total_rename(int(botid), prrename)
    total_size(int(botid), prsize, file.file_size)

    await message.reply_text(
        f"""File: `{filename}`
Size: {filesize}
DC: {dcid}""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Rename", callback_data="rename"),
             InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ])
		)
