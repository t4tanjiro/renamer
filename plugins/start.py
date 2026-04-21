from datetime import date as date_
import datetime
import asyncio
import time
from script import *
from pyrogram.errors import UserNotParticipant
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import humanize
from helper.progress import humanbytes
from helper.database import (
    insert, find_one, botdata,
    used_limit, usertype, uploadlimit,
    total_rename, total_size,
    daily as daily_,
    update_referral
)
from pyrogram.file_id import FileId
from helper.date import check_expi
from config import *

botid = BOT_TOKEN.split(':')[0]

# 🔥 FORCE SUB CHANNELS
FORCE_CHANNELS = ["TBOT_UPDATE", "TBOT_CHATS"]
PRIVATE_CHANNEL = "https://t.me/+QOYj8sm8eLFlODQ1"


async def check_sub(client, user_id):
    for ch in FORCE_CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True


@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user_id = message.chat.id
    insert(user_id)

    # 🔥 REFERRAL
    try:
        ref = int(message.text.split(" ")[1])
        if ref != user_id:
            update_referral(user_id, ref)
    except:
        pass

    txt = f"""Hello {message.from_user.mention}

➻ Advanced Rename Bot ⚡

👨‍💻 Developer: @t4tanjiro  
📢 Updates: @TBOT_UPDATE  
💬 Support: @TBOT_CHATS  

Made By @TBOT_UPDATE 🚀
"""

    await message.reply_photo(
        photo=BOT_PIC,
        caption=txt,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Updates", url="https://t.me/TBOT_UPDATE"),
             InlineKeyboardButton("💬 Support", url="https://t.me/TBOT_CHATS")],
            [InlineKeyboardButton("🛠 Help", callback_data="help"),
             InlineKeyboardButton("❤️ About", callback_data="about")],
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/t4tanjiro")]
        ])
    )


# =========================
# FILE HANDLER + FORCE SUB
# =========================
@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def send_doc(client, message):

    user_id = message.from_user.id

    if not await check_sub(client, user_id):
        return await message.reply_text(
            "⚠️ Join all channels to use bot",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Updates", url="https://t.me/TBOT_UPDATE")],
                [InlineKeyboardButton("💬 Support", url="https://t.me/TBOT_CHATS")],
                [InlineKeyboardButton("🔒 Private", url=PRIVATE_CHANNEL)]
            ])
        )

    media = await client.get_messages(message.chat.id, message.id)
    file = media.document or media.video or media.audio

    await message.reply_text(
        f"File: `{file.file_name}`\nSize: {humanize.naturalsize(file.file_size)}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Rename", callback_data="rename")]
        ])
	)
