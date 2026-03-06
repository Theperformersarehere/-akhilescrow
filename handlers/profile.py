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
    data = await Database.get_or_create_user(
        user.id,
        user.username or "",
        user.full_name or "",
    )

    # Format join date
    joined_raw = data.get("joined_at", "")
    try:
        dt = datetime.fromisoformat(joined_raw.replace("Z", "+00:00"))
        joined = dt.strftime("%d %b %Y")
    except Exception:
        joined = "N/A"

    username_raw = data.get("username")
    username = f"@{username_raw}".replace("_", "\\_") if username_raw else "—"
    
    full_name_raw = str(data.get("full_name") or "—")
    full_name = full_name_raw.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
    
    total_buys = float(data.get("total_buys") or 0)

    text = (
        f"👤 *Your Profile*\n\n"
        f"*🆔 User ID:*            `{data.get('user_id', user.id)}`\n"
        f"*👤 Username:*          {username}\n"
        f"*📛 Name:*               {full_name}\n"
        f"*📅 Member Since:*    *{joined}*\n\n"
        f"*💰 Total Crypto Bought:*  *${total_buys:,.2f}*\n"
        f"*✅ Successful Payments:*  *{data.get('successful_payments') or 0}*"
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
