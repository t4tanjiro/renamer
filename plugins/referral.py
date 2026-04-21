from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from helper.database import (
    get_referral_data,
    update_referral,
    reset_points
)
# ===== Mongo =====

LOG_CHANNEL = LOG_CHANNEL
ADMIN_IDS = OWNER if isinstance(OWNER, list) else [OWNER]


# ===== DB FUNC =====
async def get_user(user_id):
    user = await ref_users.find_one({"_id": user_id})
    if not user:
        user = {
            "_id": user_id,
            "referrals": 0,
            "points": 0,
            "referred_by": None
        }
        await ref_users.insert_one(user)
    return user


# ===== START HOOK (IMPORTANT) =====
@Client.on_message(filters.command("start"))
async def start_ref(client, message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if len(message.command) > 1:
        try:
            referrer_id = int(message.command[1])
        except:
            referrer_id = None

        if referrer_id and referrer_id != user_id and user["referred_by"] is None:

            await ref_users.update_one(
                {"_id": user_id},
                {"$set": {"referred_by": referrer_id}}
            )

            ref_user = await get_user(referrer_id)

            new_refs = ref_user["referrals"] + 1
            new_points = (new_refs // 3) * 10

            await ref_users.update_one(
                {"_id": referrer_id},
                {"$set": {
                    "referrals": new_refs,
                    "points": new_points
                }}
            )


# ===== REFER COMMAND =====
@Client.on_message(filters.command("refer") & filters.private)
async def refer(client, message):

    user_id = message.from_user.id
    user = await get_user(user_id)

    bot = await client.get_me()
    link = f"https://t.me/{bot.username}?start={user_id}"

    text = f"""
👥 Referral System

🔗 {link}

🎁 Rewards:
➥ 3 Refers = 10 Points  
➥ 90 Points = Withdrawal 🚀  

💰 Your Stats:
👤 Referrals: {user['referrals']}
⭐ Points: {user['points']}

━━━━━━━━━━━━━━━
💸 Minimum Withdrawal: 90 Points
"""

    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")]
        ])
    )


# ===== WITHDRAW =====
@Client.on_callback_query(filters.regex("withdraw"))
async def withdraw(client, query):

    user_id = query.from_user.id
    user = await get_user(user_id)

    if user["points"] < 90:
        return await query.answer("❌ Minimum 90 points required!", show_alert=True)

    msg = await client.send_message(
        LOG_CHANNEL,
        f"""#withdrawal

👤 {query.from_user.mention}
🆔 `{user_id}`

⭐ Points: {user['points']}
👥 Referrals: {user['referrals']}""",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
            ]
        ])
    )

    await client.pin_chat_message(LOG_CHANNEL, msg.id)

    await query.message.reply_text("✅ Withdrawal request sent!")


# ===== ADMIN =====
@Client.on_callback_query(filters.regex("approve_"))
async def approve(client, query):

    if query.from_user.id not in ADMIN_IDS:
        return await query.answer("❌ Not allowed", show_alert=True)

    user_id = int(query.data.split("_")[1])

    await ref_users.update_one(
        {"_id": user_id},
        {"$set": {"points": 0}}
    )

    await query.message.edit_text("✅ Withdrawal Approved")


@Client.on_callback_query(filters.regex("reject_"))
async def reject(client, query):

    if query.from_user.id not in ADMIN_IDS:
        return await query.answer("❌ Not allowed", show_alert=True)

    await query.message.edit_text("❌ Withdrawal Rejected")
