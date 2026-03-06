import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import Database
from utils.keyboards import back_to_main

logger = logging.getLogger(__name__)


async def _delete(msg):
    try:
        await msg.delete()
    except Exception:
        pass


async def referral_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    await Database.get_or_create_user(
        user.id,
        user.username or "",
        user.full_name or "",
    )

    # Fetch settings from DB
    referral_photo   = await Database.get_setting("referral_photo", "")
    referral_link    = await Database.get_setting("referral_link", "")
    referral_channel = await Database.get_setting("referral_channel", "")

    text = (
        f"🎁 *Referral Program*\n\n"
        f"Share your referral link and earn rewards!\n\n"
    )
    if referral_link:
        text += f"🔗 *Referral Link:*\n`{referral_link}`\n\n"
    if referral_channel:
        text += f"📢 *Updates Channel:*\n{referral_channel}\n\n"
    if not referral_link and not referral_channel:
        text += "_Referral program details coming soon!_"

    # Build keyboard
    rows = []
    if referral_link:
        rows.append([InlineKeyboardButton("🔗 Open Referral Link", url=referral_link)])
    if referral_channel:
        channel_url = referral_channel if referral_channel.startswith("http") else f"https://t.me/{referral_channel.lstrip('@')}"
        rows.append([InlineKeyboardButton("📢 Join Updates Channel", url=channel_url)])
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="main_menu")])
    keyboard = InlineKeyboardMarkup(rows)

    try:
        await _delete(query.message)
    except Exception:
        pass

    if referral_photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=referral_photo,
            caption=text,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )


def get_handlers():
    return [
        CallbackQueryHandler(referral_callback, pattern="^referral$"),
    ]
