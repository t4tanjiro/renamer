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
from helper.database import daily as daily_
from helper.database import update_referral, get_referral_data   # 🔥 ADDED
from pyrogram.file_id import FileId
from helper.date import check_expi
from config import *

bot_username = BOT_USERNAME
log_channel = LOG_CHANNEL
token = BOT_TOKEN
botid = token.split(':')[0]


# =========================
# 🚀 START COMMAND
# =========================
@Client.on_message(filters.private & filters.command(["start"]))
async def start(client, message):

    user_id = message.chat.id

    # insert user
    insert(int(user_id))

    # =========================
    # 🔥 REFERRAL SYSTEM
    # =========================
    try:
        ref_id = message.text.split(' ')[1]
    except IndexError:
        ref_id = None

    if ref_id:
        try:
            referrer_id = int(ref_id)
            if referrer_id != user_id:
                update_referral(user_id, referrer_id)
        except:
            pass

    # get referral data (optional display)
    ref_data = get_referral_data(user_id)
    points = ref_data["points"]

    # =========================
    # UI START
    # =========================
    loading_sticker_message = await message.reply_sticker(
        "CAACAgIAAxkBAALmzGXSSt3ppnOsSl_spnAP8wHC26jpAAJEGQACCOHZSVKp6_XqghKoHgQ"
    )
    await asyncio.sleep(2)
    await loading_sticker_message.delete()

    txt = f"""Hello {message.from_user.mention}

⭐ Your Points: {points}

➻ This Is An Advanced And Yet Powerful Rename Bot.

➻ Using This Bot You Can Rename And Change Thumbnail Of Your Files.

➻ You Can Also Convert Video To File And File To Video.

➻ This Bot Also Supports Custom Thumbnail And Custom Caption.

<b>Bot Is Made By @HxBots</b>
"""

    await message.reply_photo(
        photo=BOT_PIC,
        caption=txt,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📢 Updates", url="https://t.me/HxBots"),
                InlineKeyboardButton("💬 Support", url="https://t.me/HxSupport")
            ],
            [
                InlineKeyboardButton("🛠️ Help", callback_data='help'),
                InlineKeyboardButton("❤️‍🩹 About", callback_data='about')
            ],
            [
                InlineKeyboardButton("🧑‍💻 Developer 🧑‍💻", url="https://t.me/Kirodewal")
            ]
        ])
    )


# =========================
# 📂 FILE HANDLER (UNCHANGED)
# =========================
@Client.on_message(
    (filters.private & (filters.document | filters.audio | filters.video)) |
    (filters.channel & (filters.document | filters.audio | filters.video))
)
async def send_doc(client, message):

    update_channel = FORCE_SUBS
    user_id = message.from_user.id

    # 🔒 Force Sub
    if update_channel:
        try:
            await client.get_chat_member(update_channel, user_id)
        except UserNotParticipant:
            _newus = find_one(user_id)
            user = _newus["usertype"]

            await message.reply_text(
                "<b>Hello Dear \n\nYou Need To Join In My Channel To Use Me</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔺 Join Channel 🔺", url=f"https://t.me/{update_channel}")]
                ])
            )

            await client.send_message(
                log_channel,
                f"New User: {user_id} | Plan: {user}"
            )
            return

    # =========================
    # EXISTING LOGIC (UNCHANGED)
    # =========================
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

    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)

    await message.reply_text(
        f"""File: `{filename}`
Size: {filesize}

What do you want to do?""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Rename", callback_data="rename")]
        ])
	)
