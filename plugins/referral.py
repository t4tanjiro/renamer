from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from helper.database import (
    get_referral_data,
    reset_points,
    uploadlimit,
    usertype,
    addpre
)

LOG_CHANNEL = LOG_CHANNEL
OWNER_ID = OWNER


# =========================
# 👥 REFER COMMAND
# =========================
@Client.on_message(filters.private & filters.command("refer"))
async def refer(client, message):

    user_id = message.from_user.id
    data = get_referral_data(user_id)

    bot = await client.get_me()
    link = f"https://t.me/{bot.username}?start={user_id}"

    await message.reply_text(
        f"""
👥 Referral System

🔗 {link}

🎁 Rewards:
➥ 3 Refers = 10 Points  
➥ 90 Points = 30 Days Premium 🚀  

💰 Your Stats:
👤 Referrals: {data['referrals']}
⭐ Points: {data['points']}

━━━━━━━━━━━━━━━
💸 Minimum Withdrawal: 90 Points
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")]
        ])
    )


# =========================
# 💸 WITHDRAW
# =========================
@Client.on_callback_query(filters.regex("withdraw"))
async def withdraw(client, query):

    user_id = query.from_user.id
    data = get_referral_data(user_id)

    if data["points"] < 90:
        return await query.answer("❌ Need 90 points!", show_alert=True)

    msg = await client.send_message(
        LOG_CHANNEL,
        f"""#withdrawal

👤 {query.from_user.mention}
🆔 `{user_id}`

⭐ Points: {data['points']}
👥 Referrals: {data['referrals']}""",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
            ]
        ])
    )

    await client.pin_chat_message(LOG_CHANNEL, msg.id)

    await query.message.reply_text("✅ Withdrawal request sent!")


# =========================
# ✅ APPROVE (AUTO PREMIUM)
# =========================
@Client.on_callback_query(filters.regex("approve_"))
async def approve(client, query):

    if query.from_user.id != OWNER_ID:
        return await query.answer("❌ Not allowed", show_alert=True)

    user_id = int(query.data.split("_")[1])

    # 🔥 RESET POINTS
    reset_points(user_id)

    # 🔥 GIVE PREMIUM (30 days / 4GB)
    uploadlimit(user_id, 4294967296)
    usertype(user_id, "Referral Premium")
    addpre(user_id)

    await client.send_message(
        user_id,
        "🎉 Your withdrawal approved!\n\n🚀 You got 30 Days Premium!"
    )

    await query.message.edit_text("✅ Approved & Premium Given")


# =========================
# ❌ REJECT
# =========================
@Client.on_callback_query(filters.regex("reject_"))
async def reject(client, query):

    if query.from_user.id != OWNER_ID:
        return await query.answer("❌ Not allowed", show_alert=True)

    await query.message.edit_text("❌ Withdrawal Rejected")
