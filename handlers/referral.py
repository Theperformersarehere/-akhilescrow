import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import Database

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

    # Fetch admin-configured settings
    referral_photo   = await Database.get_setting("referral_photo", "")
    referral_channel = await Database.get_setting("referral_channel", "")

    # Get this user's personal referral count
    referral_count = await Database.get_referral_count(user.id)

    # Build the user's personal referral link
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username
    personal_ref_link = f"https://t.me/{bot_username}?start=ref_{user.id}"

    text = (
        f"🎁 *Referral Program*\n\n"
        f"📣 Share your link — only *new* users count!\n\n"
        f"🔗 *Your Referral Link:*\n"
        f"`{personal_ref_link}`\n\n"
        f"👥 *People You've Referred:* *{referral_count}*\n"
    )
    if referral_channel:
        text += f"\n📢 *Updates Channel:* {referral_channel}\n"

    # Build keyboard
    rows = [
        [InlineKeyboardButton("🔗 Share Referral Link", url=f"https://t.me/share/url?url={personal_ref_link}&text=Join+via+my+link!")],
    ]
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
