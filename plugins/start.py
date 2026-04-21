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
from helper.database import insert, find_one, used_limit, usertype, uploadlimit, addpredata, total_rename, total_size
from pyrogram.file_id import FileId
from helper.database import daily as daily_
from helper.date import check_expi
from config import *
from helper.database import update_referral

bot_username = BOT_USERNAME
log_channel = LOG_CHANNEL
token = BOT_TOKEN
botid = token.split(':')[0]


@Client.on_message(filters.private & filters.command(["start"]))
async def start(client, message):
    user_id = message.chat.id
    old = insert(int(user_id))

    try:
        ref_id = message.text.split(' ')[1]
        referrer_id = int(ref_id)
        if referrer_id != user_id:
            update_referral(user_id, referrer_id)
    except:
        pass

    try:
        id = message.text.split(' ')[1]
    except IndexError:
        id = None

    loading_sticker_message = await message.reply_sticker("CAACAgIAAxkBAALmzGXSSt3ppnOsSl_spnAP8wHC26jpAAJEGQACCOHZSVKp6_XqghKoHgQ")
    await asyncio.sleep(2)
    await loading_sticker_message.delete()

    txt=f"""Hello {message.from_user.mention} \n\n➻ This Is An Advanced And Yet Powerful Rename Bot.\n\n➻ Using This Bot You Can Rename And Change Thumbnail Of Your Files.\n\n➻ You Can Also Convert Video To File Aɴᴅ File To Video.\n\n➻ This Bot Also Supports Custom Thumbnail And Custom Caption.\n\n<b>Bot Is Made By @HxBots</b>"""

    await message.reply_photo(
        photo=BOT_PIC,
        caption=txt,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📢 Updates", url="https://t.me/HxBots"),
              InlineKeyboardButton("💬 Support", url="https://t.me/HxSupport")],
             [InlineKeyboardButton("🛠️ Help", callback_data='help'),
              InlineKeyboardButton("❤️‍🩹 About", callback_data='about')],
             [InlineKeyboardButton("🧑‍💻 Developer 🧑‍💻", url="https://t.me/Kirodewal")]
            ]
        )
    )
    return


@Client.on_message((filters.private & (filters.document | filters.audio | filters.video)) | filters.channel & (filters.document | filters.audio | filters.video))
async def send_doc(client, message):
    update_channel = FORCE_SUBS
    user_id = message.from_user.id

    if update_channel:
        try:
            await client.get_chat_member(update_channel, user_id)
        except UserNotParticipant:
            _newus = find_one(message.from_user.id)
            user = _newus["usertype"]

            await message.reply_text(
                "<b>Hello Dear \n\nYou Need To Join In My Channel To Use Me\n\nKindly Please Join Channel</b>",
                reply_to_message_id=message.id,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔺 Update Channel 🔺", url=f"https://t.me/{update_channel}")]]
                )
            )

            await client.send_message(
                log_channel,
                f"<b><u>New User Started The Bot</u></b> \n\n<b>User ID</b> : `{user_id}` \n<b>First Name</b> : {message.from_user.first_name} \n<b>Last Name</b> : {message.from_user.last_name} \n<b>User Name</b> : @{message.from_user.username} \n<b>User Mention</b> : {message.from_user.mention} \n<b>User Link</b> : <a href='tg://openmessage?user_id={user_id}'>Click Here</a> \n<b>User Plan</b> : {user}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔺  Rᴇsᴛʀɪᴄᴛ Usᴇʀ ( **PM** )  🔺", callback_data="ceasepower")]]
                )
            )
            return

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

    if user_type == "Free":
        LIMIT = 120
    else:
        LIMIT = 10

    then = used_date + LIMIT
    left = round(then - c_time)
    conversion = datetime.timedelta(seconds=left)
    ltime = str(conversion)

    if left > 0:
        await message.reply_text(f"<b>Sorry Dude I Am Not Only For You \n\nFlood Control Is Active So Please Wait For {ltime} </b>", reply_to_message_id=message.id)

    else:
        media = await client.get_messages(message.chat.id, message.id)
        file = media.document or media.video or media.audio
        dcid = FileId.decode(file.file_id).dc_id
        filename = file.file_name
        file_id = file.file_id

        used_ = find_one(message.from_user.id)
        used = used_["used_limit"]
        limit = used_["uploadlimit"]

        expi = daily - int(time.mktime(time.strptime(str(date_.today()), '%Y-%m-%d')))
        if expi != 0:
            today = date_.today()
            pattern = '%Y-%m-%d'
            epcho = int(time.mktime(time.strptime(str(today), pattern)))
            daily_(message.from_user.id, epcho)
            used_limit(message.from_user.id, 0)

        remain = limit - used

        if remain < int(file.file_size):
            await message.reply_text(
                f"100% Of Daily {humanbytes(limit)} Data Quota Exhausted.\n\n<b>File Size Detected :</b> {humanbytes(file.file_size)}\n<b>Used Daily Limit :</b> {humanbytes(used)}\n\nYou Have Only <b>{humanbytes(remain)}</b> Left On Your Account.\n\nIf U Want To Rename Large File Upgrade Your Plan",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Upgrade", callback_data="my_pl_call")]])
            )
            return

        if file.file_size > 2147483648:
            if not STRING:
                await message.reply_text("❌ This bot can't process files larger than 2GB")
                return
            if user_type == "Free":
                await message.reply_text(
                    f"❌ Free Plan Limit: 2GB\n\n📦 File Size: {humanize.naturalsize(file.file_size)}\n\n💎 Upgrade to Premium for 4GB support.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Upgrade", callback_data="my_pl_call")]])
                )
                return
            if file.file_size > 4294967296:
                await message.reply_text(
                    f"❌ Maximum allowed size is 4GB.\n\n📦 Your File: {humanize.naturalsize(file.file_size)}"
                )
                return

        filesize = humanize.naturalsize(file.file_size)

        total_rename(int(botid), prrename)
        total_size(int(botid), prsize, file.file_size)

        await message.reply_text(
            f"""__What Do You Want Me To Do With This File ?__\n\nFile Name :- `{filename}`\nFile Size :- {filesize}\nDC ID :- {dcid}""",
            reply_to_message_id=message.id,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📝 Rename", callback_data="rename"),
                  InlineKeyboardButton("✖️ Cancel", callback_data="cancel")]]
            )
        )
