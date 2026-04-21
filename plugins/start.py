from datetime import date as date_
import asyncio, time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from helper.database import insert, update_referral
from config import *

# 🔥 CHANNEL SETTINGS
FORCE_CHANNELS = ["@TBOT_UPDATE", "@TBOT_CHATS"]
PRIVATE_CHANNEL = "https://t.me/+IEdk6O6wlglmNGVl"


# =========================
# 🔍 FORCE SUB CHECK
# =========================
async def check_sub(client, user_id):
    for channel in FORCE_CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)

            if member.status in ["left", "kicked"]:
                return False

        except Exception as e:
            print(f"ForceSub Error {channel}: {e}")
            return False

    return True


# =========================
# 🚀 START
# =========================
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

    # 🔥 FORCE SUB CHECK
    if not await check_sub(client, user_id):
        return await message.reply_text(
            "⚠️ Join all channels and click VERIFY",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Updates", url="https://t.me/TBOT_UPDATE")],
                [InlineKeyboardButton("💬 Support", url="https://t.me/TBOT_CHATS")],
                [InlineKeyboardButton("🔒 Private", url=PRIVATE_CHANNEL)],
                [InlineKeyboardButton("✅ VERIFY", callback_data="verify")]
            ])
        )

    # ✅ NORMAL START UI
    await message.reply_text(
        f"""Hello {message.from_user.mention}

⚡ Advanced Rename Bot

👨‍💻 Developer: @t4tanjiro  
📢 Updates: @TBOT_UPDATE  
💬 Support: @TBOT_CHATS  

Made By @TBOT_UPDATE 🚀"""
    )


# =========================
# ✅ VERIFY BUTTON
# =========================
@Client.on_callback_query(filters.regex("verify"))
async def verify(client, query):

    user_id = query.from_user.id

    if not await check_sub(client, user_id):
        return await query.answer("❌ Join all channels first!", show_alert=True)

    await query.message.edit_text(
        f"""✅ Verification Successful!

Now you can use the bot 🎉"""
	)
