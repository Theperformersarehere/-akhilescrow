import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters,
)

from database import Database
from utils.keyboards import admin_home_keyboard, admin_cancel_keyboard
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

# ── States ─────────────────────────────────────────────────────────────────────
(
    ADMIN_HOME,
    ADMIN_AWAIT_MAIN_PHOTO,
    ADMIN_AWAIT_PAY_PHOTO,
    ADMIN_AWAIT_STATS_PHOTO,
    ADMIN_AWAIT_PROFILE_PHOTO,
    ADMIN_AWAIT_MAIN_TEXT,
    ADMIN_AWAIT_PAY_TEXT,
    ADMIN_AWAIT_SUPPORT,
    ADMIN_AWAIT_CONV_MSG,
    ADMIN_AWAIT_PAY_INFO_ACTION,
    ADMIN_AWAIT_PAY_INFO_PHOTO,
    ADMIN_AWAIT_PAY_INFO_TEXT,
    ADMIN_AWAIT_APPROVE,
    ADMIN_AWAIT_REJECT,
    ADMIN_AWAIT_RATES,
    ADMIN_VIEW_ORDERS,
    ADMIN_AWAIT_CHANNEL,
) = range(17)


# ── Guard ──────────────────────────────────────────────────────────────────────
def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def _delete(msg):
    try:
        await msg.delete()
    except Exception:
        pass


# ── Admin home ─────────────────────────────────────────────────────────────────
async def admin_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_admin(user.id):
        if update.message:
            await update.message.reply_text("⛔ You are not authorised to use this command.")
        return ConversationHandler.END

    await Database.get_or_create_user(
        user.id,
        user.username or "",
        user.full_name or "",
    )

    text = (
        "⚙️ *Admin Panel*\n\n"
        "Select an option to manage the bot:"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await _delete(update.callback_query.message)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── Photo setters ──────────────────────────────────────────────────────────────
async def prompt_main_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🖼 *Send the new Main Menu photo:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_MAIN_PHOTO


async def receive_main_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    await Database.set_setting("main_menu_photo", file_id)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Main menu photo updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


async def prompt_main_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📝 *Send the new Main Menu text:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_MAIN_TEXT


async def receive_main_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await Database.set_setting("main_menu_text", update.message.text.strip())
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Main menu text updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


async def prompt_pay_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="💳 *Send the new Buy Amount photo:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_PAY_PHOTO


async def receive_pay_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    await Database.set_setting("buy_photo", file_id)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Buy photo updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


async def prompt_pay_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📝 *Send the new Buy Menu text:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_PAY_TEXT


async def receive_pay_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await Database.set_setting("buy_text", update.message.text.strip())
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Buy menu text updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


async def prompt_stats_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📊 *Send the new Stats page photo:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_STATS_PHOTO


async def receive_stats_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    await Database.set_setting("stats_photo", file_id)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Stats photo updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


async def prompt_profile_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👤 *Send the new Profile page photo:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_PROFILE_PHOTO


async def receive_profile_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    await Database.set_setting("profile_photo", file_id)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Profile photo updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── Support username ───────────────────────────────────────────────────────────
async def prompt_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    cur = await Database.get_setting("support_username", "@support")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📞 *Current support username:* `{cur}`\n\nSend the new username (e.g. `@mysupport`):",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_SUPPORT


async def receive_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    await Database.set_setting("support_username", val)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ Support username set to `{val}`",
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── Conversion rates message ───────────────────────────────────────────────────
async def prompt_conv_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    cur = await Database.get_setting("conversion_rate_message", "")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"💬 *Current rates popup message:*\n\n{cur}\n\n"
            f"Send the new message text (Markdown supported):"
        ),
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_CONV_MSG


async def receive_conv_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text
    await Database.set_setting("conversion_rate_message", val)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Conversion rate message updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# Removed Wallet logic separately since selling bot gives user *their* crypto wallet within the QR logic.


# ── Payment Methods Info ───────────────────────────────────────────────────────
async def prompt_pay_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # "adm_upi" or "adm_imps"
    method = query.data.split("_")[1]
    context.user_data["editing_pay_method"] = method
    await _delete(query.message)
    
    from utils.keyboards import payment_info_action_keyboard
    markup = payment_info_action_keyboard()
    
    text_val = await Database.get_setting(f"{method}_text", "Not set")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🏦 *{method.upper()} Settings*\n\nCurrent Text:\n`{text_val}`\n\nWhat would you like to update?",
        parse_mode="Markdown",
        reply_markup=markup,
    )
    return ADMIN_AWAIT_PAY_INFO_ACTION


async def prompt_pay_info_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method = context.user_data.get("editing_pay_method", "")
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🖼 *Send the payment photo for {method.upper()}:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_PAY_INFO_PHOTO


async def prompt_pay_info_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method = context.user_data.get("editing_pay_method", "")
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📝 *Send the new payment details text for {method.upper()}:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_PAY_INFO_TEXT


async def receive_pay_info_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    method = context.user_data.get("editing_pay_method", "")
    file_id = update.message.photo[-1].file_id
    if method:
        await Database.set_setting(f"{method}_photo", file_id)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ {method.upper()} photo updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


async def receive_pay_info_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    method = context.user_data.get("editing_pay_method", "")
    val = update.message.text
    if method:
        await Database.set_setting(f"{method}_text", val)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ {method.upper()} text updated!",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── Exchange rate tiers ────────────────────────────────────────────────────────
async def prompt_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)

    t1_min  = await Database.get_setting("rate_tier_1_min",  "10")
    t1_max  = await Database.get_setting("rate_tier_1_max",  "299")
    t1_rate = await Database.get_setting("rate_tier_1_rate", "98")
    t2_min  = await Database.get_setting("rate_tier_2_min",  "300")
    t2_max  = await Database.get_setting("rate_tier_2_max",  "1350")
    t2_rate = await Database.get_setting("rate_tier_2_rate", "97")
    t3_min  = await Database.get_setting("rate_tier_3_min",  "1351")
    t3_rate = await Database.get_setting("rate_tier_3_rate", "96")

    cur = (
        f"Tier 1: ${t1_min}–${t1_max} → ₹{t1_rate}\n"
        f"Tier 2: ${t2_min}–${t2_max} → ₹{t2_rate}\n"
        f"Tier 3: ${t3_min}+ → ₹{t3_rate}"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"📈 *Current Exchange Rate Tiers:*\n\n`{cur}`\n\n"
            f"Send the new rates in this exact format:\n"
            f"```\n"
            f"10,299,98\n"
            f"300,1350,97\n"
            f"1351,0,96\n"
            f"```\n"
            f"Format: `min,max,rate` (use `0` as max for the last tier)"
        ),
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_RATES


async def receive_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) != 3:
        await update.message.reply_text(
            "❌ Please send exactly 3 lines in `min,max,rate` format.",
            parse_mode="Markdown",
        )
        return ADMIN_AWAIT_RATES

    try:
        tiers = []
        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            tiers.append((float(parts[0]), float(parts[1]), int(parts[2])))
    except Exception:
        await update.message.reply_text("❌ Invalid format. Use `min,max,rate` per line.")
        return ADMIN_AWAIT_RATES

    await Database.set_setting("rate_tier_1_min",  str(tiers[0][0]))
    await Database.set_setting("rate_tier_1_max",  str(tiers[0][1]))
    await Database.set_setting("rate_tier_1_rate", str(tiers[0][2]))
    await Database.set_setting("rate_tier_2_min",  str(tiers[1][0]))
    await Database.set_setting("rate_tier_2_max",  str(tiers[1][1]))
    await Database.set_setting("rate_tier_2_rate", str(tiers[1][2]))
    await Database.set_setting("rate_tier_3_min",  str(tiers[2][0]))
    await Database.set_setting("rate_tier_3_rate", str(tiers[2][2]))

    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"✅ *Exchange rates updated!*\n\n"
            f"Tier 1: ${tiers[0][0]:g}–${tiers[0][1]:g} → ₹{tiers[0][2]}\n"
            f"Tier 2: ${tiers[1][0]:g}–${tiers[1][1]:g} → ₹{tiers[1][2]}\n"
            f"Tier 3: ${tiers[2][0]:g}+ → ₹{tiers[2][2]}"
        ),
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── View orders ─────────────────────────────────────────────────────────────────
def _format_orders(orders: list, title: str) -> str:
    if not orders:
        return f"{title}\n\n_No orders found._"
    lines = [title, ""]
    for o in orders:
        status_emoji = {"approved": "✅", "pending": "⏳", "rejected": "❌", "awaiting_payment": "🔘"}.get(o["status"], "❓")
        lines.append(
            f"{status_emoji} `{o['order_id']}`\n"
            f"   💰 ${float(o['amount_usd']):,.2f}  |  {o['network']}\n"
            f"   💳 Method: `{o.get('payment_method') or '—'}`\n"
        )
    return "\n".join(lines)


async def view_all_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)

    orders = await Database.get_all_orders(limit=10)
    text   = _format_orders(orders, "📦 *Last 10 Orders*")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("↩️ Admin Menu", callback_data="adm_back")],
        ]),
    )
    return ADMIN_VIEW_ORDERS


async def view_pending_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)

    orders = await Database.get_pending_orders(limit=10)
    text   = _format_orders(orders, "⏳ *Pending Orders*")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("↩️ Admin Menu", callback_data="adm_back")],
        ]),
    )
    return ADMIN_VIEW_ORDERS


# ── Approve / Reject ──────────────────────────────────────────────────────────
async def prompt_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ *Enter the Order ID to approve:*\n\n_(e.g. `CRB-20260306-ABC123`)_",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_APPROVE


async def receive_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = update.message.text.strip().upper()
    order    = await Database.approve_order(order_id)
    await _delete(update.message)

    if not order:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Order `{order_id}` not found or already processed.",
            parse_mode="Markdown",
            reply_markup=admin_home_keyboard(),
        )
        return ADMIN_HOME

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                f"✅ *Payment Approved!*\n\n"
                f"🆔 Order: `{order_id}`\n"
                f"💰 ${float(order['amount_usd']):,.2f}\n\n"
                f"Your crypto will be sent shortly. Thank you! 🙏"
            ),
            parse_mode="Markdown",
        )
    except Exception:
        pass

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ Order `{order_id}` approved and user notified.",
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


async def prompt_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="❌ *Enter the Order ID to reject:*\n\n_(e.g. `CRB-20260306-ABC123`)_",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_REJECT


async def receive_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = update.message.text.strip().upper()
    order    = await Database.reject_order(order_id)
    await _delete(update.message)

    if not order:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Order `{order_id}` not found or already processed.",
            parse_mode="Markdown",
            reply_markup=admin_home_keyboard(),
        )
        return ADMIN_HOME

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                f"❌ *Payment Rejected*\n\n"
                f"🆔 Order: `{order_id}`\n\n"
                f"Your payment was rejected. Please contact support for assistance."
            ),
            parse_mode="Markdown",
        )
    except Exception:
        pass

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"❌ Order `{order_id}` rejected and user notified.",
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── Proof channel ──────────────────────────────────────────────────
async def prompt_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    cur = await Database.get_setting("proof_channel_id", "Not set")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"📢 *Proof Channel*\n\n"
            f"Current: `{cur}`\n\n"
            f"Send the channel ID where payment proofs will be posted.\n"
            f"Format: `-1001234567890` (use a negative number for channels)\n\n"
            f"⚠️ Make sure this bot is an *admin* in that channel before setting it."
        ),
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    return ADMIN_AWAIT_CHANNEL


async def receive_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    await Database.set_setting("proof_channel_id", val)
    await _delete(update.message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ Proof channel set to `{val}`",
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── ConversationHandler factory ───────────────────────────────────────────────
def get_admin_conversation() -> ConversationHandler:
    back_btn = CallbackQueryHandler(admin_home, pattern="^adm_back$")

    return ConversationHandler(
        entry_points=[CommandHandler("admin", admin_home)],
        states={
            ADMIN_HOME: [
                CallbackQueryHandler(prompt_main_photo,    pattern="^adm_main_photo$"),
                CallbackQueryHandler(prompt_main_text,     pattern="^adm_main_text$"),
                CallbackQueryHandler(prompt_pay_photo,     pattern="^adm_pay_photo$"),
                CallbackQueryHandler(prompt_pay_text,      pattern="^adm_pay_text$"),
                CallbackQueryHandler(prompt_stats_photo,   pattern="^adm_stats_photo$"),
                CallbackQueryHandler(prompt_profile_photo, pattern="^adm_profile_photo$"),
                CallbackQueryHandler(prompt_support,       pattern="^adm_support$"),
                CallbackQueryHandler(prompt_conv_msg,      pattern="^adm_conv_msg$"),
                CallbackQueryHandler(prompt_pay_info,      pattern="^adm_(upi|imps)$"),
                CallbackQueryHandler(prompt_rates,         pattern="^adm_rates$"),
                CallbackQueryHandler(prompt_channel,       pattern="^adm_channel$"),
                CallbackQueryHandler(view_all_orders,      pattern="^adm_orders$"),
                CallbackQueryHandler(view_pending_orders,  pattern="^adm_pending$"),
                CallbackQueryHandler(prompt_approve,       pattern="^adm_approve$"),
                CallbackQueryHandler(prompt_reject,        pattern="^adm_reject$"),
            ],
            ADMIN_AWAIT_MAIN_PHOTO:  [MessageHandler(filters.PHOTO, receive_main_photo), back_btn],
            ADMIN_AWAIT_MAIN_TEXT:   [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_main_text), back_btn],
            ADMIN_AWAIT_PAY_PHOTO:   [MessageHandler(filters.PHOTO, receive_pay_photo),  back_btn],
            ADMIN_AWAIT_PAY_TEXT:    [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_pay_text), back_btn],
            ADMIN_AWAIT_STATS_PHOTO: [MessageHandler(filters.PHOTO, receive_stats_photo),back_btn],
            ADMIN_AWAIT_PROFILE_PHOTO:[MessageHandler(filters.PHOTO, receive_profile_photo),back_btn],
            ADMIN_AWAIT_SUPPORT:     [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_support), back_btn],
            ADMIN_AWAIT_CONV_MSG:    [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_conv_msg), back_btn],
            ADMIN_AWAIT_PAY_INFO_ACTION: [
                CallbackQueryHandler(prompt_pay_info_photo, pattern="^setpay_photo$"),
                CallbackQueryHandler(prompt_pay_info_text, pattern="^setpay_text$"),
                back_btn,
            ],
            ADMIN_AWAIT_PAY_INFO_PHOTO:  [MessageHandler(filters.PHOTO, receive_pay_info_photo), back_btn],
            ADMIN_AWAIT_PAY_INFO_TEXT:   [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_pay_info_text), back_btn],
            ADMIN_AWAIT_APPROVE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_approve), back_btn],
            ADMIN_AWAIT_REJECT:      [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_reject), back_btn],
            ADMIN_AWAIT_RATES:       [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_rates), back_btn],
            ADMIN_AWAIT_CHANNEL:     [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_channel), back_btn],
            ADMIN_VIEW_ORDERS:       [back_btn],
        },
        fallbacks=[CommandHandler("admin", admin_home)],
        allow_reentry=True,
        per_message=False,
    )
