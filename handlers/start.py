import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from database import Database
from utils.keyboards import main_menu_keyboard

logger = logging.getLogger(__name__)


async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, delete_prev: bool = False):
    """Send main menu, optionally deleting the previous message first."""
    user = update.effective_user
    await Database.get_or_create_user(
        user.id,
        user.username or "",
        user.full_name or "",
    )

    photo = await Database.get_setting("main_menu_photo", "")
    caption = await Database.get_setting("main_menu_text", (
        "🏠 *Welcome to Crypto Buy Bot*\n\n"
        "💎 Buy crypto instantly with INR\n"
        "🔒 Secure & Fast transactions\n\n"
        "Choose an option below 👇"
    ))
    support_username = await Database.get_setting("support_username", "@owner")
    referral_channel = await Database.get_setting("referral_channel", "")
    community_url = ""
    if referral_channel:
        community_url = referral_channel if referral_channel.startswith("http") else f"https://t.me/{referral_channel.lstrip('@')}"
    keyboard = main_menu_keyboard(support_username, community_url=community_url)


    if delete_prev and update.callback_query:
        try:
            await update.callback_query.message.delete()
        except Exception:
            pass

    chat_id = update.effective_chat.id
    if photo:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=caption,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message:
            await update.message.delete()
    except Exception:
        pass

    user = update.effective_user

    # ── Referral tracking ──────────────────────────────────────────────────
    # Check if this user was referred: /start ref_12345678
    referrer_id = None
    args = context.args  # list of words after /start
    if args:
        arg = args[0]
        if arg.startswith("ref_"):
            try:
                referrer_id = int(arg[4:])
            except ValueError:
                referrer_id = None

    # Register user. If they are brand-new AND came via a referral link,
    # get_or_create_user will credit the referrer automatically.
    await Database.get_or_create_user(
        user.id,
        user.username or "",
        user.full_name or "",
        referrer_id=referrer_id,
    )

    await send_main_menu(update, context, delete_prev=False)


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    # Clear any stale buy/state data so re-entry works cleanly
    context.user_data.clear()
    await send_main_menu(update, context, delete_prev=True)


def get_handlers():
    return [
        CommandHandler("start", start_command),
        CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"),
    ]
