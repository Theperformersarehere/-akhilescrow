import logging
from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import Database
from utils.keyboards import back_to_main

logger = logging.getLogger(__name__)

async def _delete(msg):
    try:
        await msg.delete()
    except Exception:
        pass


async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    data = await Database.get_user(user.id)

    if not data:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Profile not found. Please /start the bot first.",
            reply_markup=back_to_main(),
        )
        return

    # Format join date
    joined_raw = data.get("joined_at", "")
    try:
        dt = datetime.fromisoformat(joined_raw.replace("Z", "+00:00"))
        joined = dt.strftime("%d %b %Y")
    except Exception:
        joined = "N/A"

    username = f"@{data.get('username')}" if data.get("username") else "—"
    total_buys = float(data.get("total_buys") or 0)

    text = (
        f"👤 *Your Profile*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 User ID:            `{data['user_id']}`\n"
        f"👤 Username:          {username}\n"
        f"📛 Name:               {data.get('full_name') or '—'}\n"
        f"📅 Member Since:    *{joined}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Total Crypto Bought:  *${total_buys:,.2f}*\n"
        f"✅ Successful Payments:  *{data.get('successful_payments') or 0}*\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    try:
        await _delete(query.message)
    except Exception:
        pass

    profile_photo = await Database.get_setting("profile_photo", "")

    if profile_photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=profile_photo,
            caption=text,
            parse_mode="Markdown",
            reply_markup=back_to_main(),
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode="Markdown",
            reply_markup=back_to_main(),
        )


def get_handlers():
    return [
        CallbackQueryHandler(profile_callback, pattern="^profile$"),
    ]
