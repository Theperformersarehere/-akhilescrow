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
    ADMIN_AWAIT_STATS_USER_ID,
    ADMIN_AWAIT_STATS_USER_LIST,
    ADMIN_AWAIT_STATS_USER_TRANS,
) = range(20)


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
            await _delete(update.message)
        return ConversationHandler.END

    if update.message:
        await _delete(update.message)

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
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🖼 *Send the new Main Menu photo:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_MAIN_PHOTO


async def receive_main_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    await Database.set_setting("main_menu_photo", file_id)
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)
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
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📝 *Send the new Main Menu text:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_MAIN_TEXT


async def receive_main_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await Database.set_setting("main_menu_text", update.message.text.strip())
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)
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
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="💳 *Send the new Buy Amount photo:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_PAY_PHOTO


async def receive_pay_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    await Database.set_setting("buy_photo", file_id)
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)
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
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📝 *Send the new Buy Menu text:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_PAY_TEXT


async def receive_pay_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await Database.set_setting("buy_text", update.message.text.strip())
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)
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
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📊 *Send the new Stats page photo:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_STATS_PHOTO


async def receive_stats_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    await Database.set_setting("stats_photo", file_id)
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)
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
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👤 *Send the new Profile page photo:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_PROFILE_PHOTO


async def receive_profile_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    await Database.set_setting("profile_photo", file_id)
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)
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
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📞 *Current support username:* `{cur}`\n\nSend the new username (e.g. `@mysupport`):",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_SUPPORT


async def receive_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    await Database.set_setting("support_username", val)
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)
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
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"💬 *Current rates popup message:*\n\n{cur}\n\n"
            f"Send the new message text (Markdown supported):"
        ),
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_CONV_MSG


async def receive_conv_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text
    await Database.set_setting("conversion_rate_message", val)
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)
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
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🏦 *{method.upper()} Settings*\n\nCurrent Text:\n`{text_val}`\n\nWhat would you like to update?",
        parse_mode="Markdown",
        reply_markup=markup,
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_PAY_INFO_ACTION


async def prompt_pay_info_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method = context.user_data.get("editing_pay_method", "")
    await _delete(query.message)
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🖼 *Send the payment photo for {method.upper()}:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_PAY_INFO_PHOTO


async def prompt_pay_info_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method = context.user_data.get("editing_pay_method", "")
    await _delete(query.message)
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📝 *Send the new payment details text for {method.upper()}:*",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_PAY_INFO_TEXT


async def receive_pay_info_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    method = context.user_data.get("editing_pay_method", "")
    file_id = update.message.photo[-1].file_id
    if method:
        await Database.set_setting(f"{method}_photo", file_id)
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)
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
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)
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

    msg = await context.bot.send_message(
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
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_RATES


async def receive_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    await _delete(update.message)
    
    # Clean up the previous bot prompt
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) != 3:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ *Please send exactly 3 lines in `min,max,rate` format.*",
            parse_mode="Markdown",
            reply_markup=admin_cancel_keyboard(),
        )
        context.user_data["admin_prompt_msg_id"] = msg.message_id
        return ADMIN_AWAIT_RATES

    try:
        tiers = []
        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            tiers.append((float(parts[0]), float(parts[1]), int(parts[2])))
    except Exception:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ *Invalid format. Use `min,max,rate` per line.*",
            parse_mode="Markdown",
            reply_markup=admin_cancel_keyboard(),
        )
        context.user_data["admin_prompt_msg_id"] = msg.message_id
        return ADMIN_AWAIT_RATES

    await Database.set_setting("rate_tier_1_min",  str(tiers[0][0]))
    await Database.set_setting("rate_tier_1_max",  str(tiers[0][1]))
    await Database.set_setting("rate_tier_1_rate", str(tiers[0][2]))
    await Database.set_setting("rate_tier_2_min",  str(tiers[1][0]))
    await Database.set_setting("rate_tier_2_max",  str(tiers[1][1]))
    await Database.set_setting("rate_tier_2_rate", str(tiers[1][2]))
    await Database.set_setting("rate_tier_3_min",  str(tiers[2][0]))
    await Database.set_setting("rate_tier_3_rate", str(tiers[2][2]))

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
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ *Enter the Order ID to approve:*\n\n_(e.g. `CRB-20260306-ABC123`)_",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_APPROVE


async def receive_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = update.message.text.strip().upper()
    order    = await Database.approve_order(order_id)
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)

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
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="❌ *Enter the Order ID to reject:*\n\n_(e.g. `CRB-20260306-ABC123`)_",
        parse_mode="Markdown",
        reply_markup=admin_cancel_keyboard(),
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_REJECT


async def receive_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = update.message.text.strip().upper()
    order    = await Database.reject_order(order_id)
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)

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


# ── User Stats ─────────────────────────────────────────────────────────────
# ── User Stats ─────────────────────────────────────────────────────────────
async def prompt_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    
    return await show_admin_user_list(update, context, page=0)

async def show_admin_user_list(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    limit = 10
    offset = page * limit
    users = await Database.get_users_list(offset=offset, limit=limit)
    total_users = await Database.get_users_count()
    
    buttons = []
    # User buttons
    for u in users:
        name = u.get("full_name") or u.get("username") or str(u.get("user_id"))
        buttons.append([InlineKeyboardButton(f"👤 {name}", callback_data=f"adm_stats_u_{u['user_id']}")])
    
    # Pagination row
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"adm_stats_p_{page-1}"))
    if offset + limit < total_users:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"adm_stats_p_{page+1}"))
    if nav:
        buttons.append(nav)
    
    buttons.append([InlineKeyboardButton("📝 Enter User ID Manually", callback_data="adm_stats_manual")])
    buttons.append([InlineKeyboardButton("↩️ Back to Admin", callback_data="adm_back")])
    
    text = f"📊 *User List (Page {page+1})*\nTotal Users: {total_users}\n\nSelect a user to view their transaction history:"
    
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_STATS_USER_LIST

async def admin_stats_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "adm_stats_manual":
        await _delete(query.message)
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📊 *Enter the User ID manually:*",
            parse_mode="Markdown",
            reply_markup=admin_cancel_keyboard()
        )
        context.user_data["admin_prompt_msg_id"] = msg.message_id
        return ADMIN_AWAIT_STATS_USER_ID

    if query.data.startswith("adm_stats_p_"):
        page = int(query.data.split("_")[-1])
        await _delete(query.message)
        return await show_admin_user_list(update, context, page=page)
    
    if query.data.startswith("adm_stats_u_"):
        user_id = int(query.data.split("_")[-1])
        await _delete(query.message)
        return await show_user_transactions(update, context, user_id, page=0)
    
    return ADMIN_AWAIT_STATS_USER_LIST

async def show_user_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, page: int = 0):
    limit = 5
    offset = page * limit
    orders = await Database.get_user_orders(user_id, limit=100)
    
    total_orders = len(orders)
    p_orders = orders[offset:offset+limit]
    
    user_data = await Database.get_user(user_id)
    if not user_data:
        name = str(user_id)
    else:
        name = user_data.get("full_name") or user_data.get("username") or str(user_id)
    
    if not p_orders and page == 0:
        text = f"📊 *User*: `{user_id}` ({name})\n\nNo transactions found."
    else:
        text = f"📊 *Transactions for {name}* (`{user_id}`)\n"
        text += f"Page {page+1} / {max(1, (total_orders-1)//limit + 1)}\n"
        text += "━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for o in p_orders:
            status_emoji = {"approved": "✅", "pending": "⏳", "rejected": "❌", "awaiting_payment": "🔘"}.get(o["status"], "❓")
            created = o.get("created_at", "—")
            if created != "—": created = created.split("T")[0]
            
            text += f"{status_emoji} `{o['order_id']}` ({created})\n"
            text += f"   💰 ${float(o['amount_usd']):g} | {o['network']} | 💳 {o.get('payment_method') or '—'}\n\n"
            
    buttons = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"adm_tr_p_{user_id}_{page-1}"))
    if offset + limit < total_orders:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"adm_tr_p_{user_id}_{page+1}"))
    if nav:
        buttons.append(nav)
        
    buttons.append([InlineKeyboardButton("↩️ Back to User List", callback_data="adm_stats_p_0")])
    buttons.append([InlineKeyboardButton("↩️ Back to Admin", callback_data="adm_back")])
    
    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_STATS_USER_TRANS

async def admin_trans_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("adm_tr_p_"):
        parts = query.data.split("_")
        user_id = int(parts[3])
        page = int(parts[4])
        await _delete(query.message)
        return await show_user_transactions(update, context, user_id, page=page)
    
    return ADMIN_AWAIT_STATS_USER_TRANS


async def receive_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_str = update.message.text.strip()
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception: pass
        context.user_data.pop("admin_prompt_msg_id", None)

    try:
        user_id = int(user_id_str)
    except ValueError:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ *Invalid User ID. Please send digits only.*",
            parse_mode="Markdown",
            reply_markup=admin_cancel_keyboard()
        )
        context.user_data["admin_prompt_msg_id"] = msg.message_id
        return ADMIN_AWAIT_STATS_USER_ID

    return await show_user_transactions(update, context, user_id, page=0)


# ── Proof channel ──────────────────────────────────────────────────
async def prompt_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)
    cur = await Database.get_setting("proof_channel_id", "Not set")
    msg = await context.bot.send_message(
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
    context.user_data["admin_prompt_msg_id"] = msg.message_id
    return ADMIN_AWAIT_CHANNEL


async def receive_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    await Database.set_setting("proof_channel_id", val)
    await _delete(update.message)
    last_bot_msg_id = context.user_data.get("admin_prompt_msg_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("admin_prompt_msg_id", None)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ Proof channel set to `{val}`",
        parse_mode="Markdown",
        reply_markup=admin_home_keyboard(),
    )
    return ADMIN_HOME


# ── Admin Reply ───────────────────────────────────────────────────────────────
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_admin(user.id):
        return

    # Usage: /reply <id|@username> [message]
    # If photo is attached, it sends as a photo with caption.
    args = context.args
    msg = update.effective_message
    
    if not args:
        await msg.reply_text(
            "❌ *Usage:*\n`/reply <user_id|@username> [message]`\n\n"
            "You can also attach an image to send a screenshot.",
            parse_mode="Markdown"
        )
        return

    target = args[0]
    reply_text = " ".join(args[1:])

    # Find target ID
    target_id = None
    if target.isdigit():
        target_id = int(target)
    elif target.startswith("@"):
        u = await Database.get_user_by_username(target)
        if u:
            target_id = u["user_id"]
    
    if not target_id:
        await msg.reply_text(f"❌ User `{target}` not found in database.")
        return

    # Detect photo
    photo_id = None
    if msg.photo:
        photo_id = msg.photo[-1].file_id
    elif msg.reply_to_message and msg.reply_to_message.photo:
        photo_id = msg.reply_to_message.photo[-1].file_id

    try:
        header = "💬 *Message from Admin:*\n\n"
        if photo_id:
            await context.bot.send_photo(
                chat_id=target_id,
                photo=photo_id,
                caption=f"{header}{reply_text}" if reply_text else header,
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"{header}{reply_text}",
                parse_mode="Markdown"
            )
        await msg.reply_text(f"✅ Message sent to `{target}`.")
    except Exception as e:
        await msg.reply_text(f"❌ Failed to send: {e}")


# ── Admin Broadcast ────────────────────────────────────────────────────────────
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_admin(user.id):
        return

    msg = update.effective_message
    
    # Extract text from command
    text = ""
    if msg.text:
        text = msg.text[len("/broadcast "):].strip()
    elif msg.caption:
        text = msg.caption[len("/broadcast "):].strip()

    if not text and not msg.photo:
        await msg.reply_text("❌ *Usage:* `/broadcast <message>` (or attach a photo with caption).")
        return

    all_user_ids = await Database.get_all_users_ids()
    if not all_user_ids:
        await msg.reply_text("❌ No users found in database.")
        return

    status_msg = await msg.reply_text(
        f"⏳ *Broadcast in progress...*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: `{len(all_user_ids)}`\n"
        f"✅ Sent: `0`\n"
        f"❌ Failed: `0` (Blocked/Deleted)",
        parse_mode="Markdown"
    )

    sent = 0
    failed = 0
    photo_id = msg.photo[-1].file_id if msg.photo else None

    for i, uid in enumerate(all_user_ids):
        try:
            if photo_id:
                await context.bot.send_photo(chat_id=uid, photo=photo_id, caption=text, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=uid, text=text, parse_mode="Markdown")
            sent += 1
        except Exception:
            failed += 1
        
        if (i + 1) % 5 == 0 or (i + 1) == len(all_user_ids):
            try:
                await status_msg.edit_text(
                    f"⌛ *Broadcast Progress:*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👥 Total Users: `{len(all_user_ids)}`\n"
                    f"✅ Sent: `{sent}`\n"
                    f"❌ Failed: `{failed}`\n"
                    f"📊 Progress: `{(i+1)/len(all_user_ids)*100:.1f}%`",
                    parse_mode="Markdown"
                )
            except Exception: pass
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"📢 *Broadcast Completed!*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: `{len(all_user_ids)}`\n"
        f"✅ Successfully Sent: `{sent}`\n"
        f"❌ Failed: `{failed}`",
        parse_mode="Markdown"
    )


# ── ConversationHandler factory ───────────────────────────────────────────────
def get_admin_handlers():
    return [
        CommandHandler("reply", admin_reply),
        CommandHandler("broadcast", admin_broadcast),
        MessageHandler(filters.PHOTO & filters.CaptionRegex(r"^/broadcast"), admin_broadcast),
    ]


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
                CallbackQueryHandler(prompt_user_stats,    pattern="^adm_user_stats$"),
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
            ADMIN_AWAIT_STATS_USER_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_stats), 
                back_btn
            ],
            ADMIN_AWAIT_STATS_USER_LIST: [
                CallbackQueryHandler(admin_stats_pagination, pattern="^adm_stats_"),
                back_btn
            ],
            ADMIN_AWAIT_STATS_USER_TRANS: [
                CallbackQueryHandler(admin_trans_pagination, pattern="^adm_tr_p_"),
                CallbackQueryHandler(show_admin_user_list, pattern="^adm_stats_p_0$"),
                back_btn
            ],
            ADMIN_AWAIT_RATES:       [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_rates), back_btn],
            ADMIN_AWAIT_CHANNEL:     [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_channel), back_btn],
            ADMIN_VIEW_ORDERS:       [back_btn],
        },
        fallbacks=[CommandHandler("admin", admin_home)],
        allow_reentry=True,
        per_message=False,
    )
