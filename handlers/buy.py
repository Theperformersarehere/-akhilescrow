import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters,
)

from database import Database
from utils.keyboards import (
    main_menu_keyboard, network_keyboard, amount_entry_keyboard,
    payment_method_keyboard, payment_proof_keyboard,
    back_to_main, channel_order_keyboard
)
from utils.order_id import generate_order_id
from utils.exchange_rate import get_rate_for_amount
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

# ── Conversation states ────────────────────────────────────────────────────────
(
    ENTER_AMOUNT,
    CHOOSE_NETWORK,
    ENTER_ADDRESS,
    CHOOSE_PAYMENT_METHOD,
    AWAIT_PAYMENT_PROOF,
    AWAIT_SCREENSHOT,
    AWAIT_UTR,
) = range(7)

NETWORK_LABELS = {
    "bep20": "🟡 BEP20 (BSC)",
    "erc20": "🔷 ERC20 (Ethereum)",
    "ton":   "💎 TON",
    "trc20": "🔴 TRC20 (Tron)",
}


# ── Helper: delete a message silently ─────────────────────────────────────────
async def _delete(msg):
    try:
        await msg.delete()
    except Exception as e:
        logger.error(f"Failed to delete message {msg.message_id}: {e}")


# ── Entry: user taps "Buy Crypto" ─────────────────────────────────────────────
async def buy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    await Database.get_or_create_user(
        user.id,
        user.username or "",
        user.full_name or "",
    )

    await _delete(query.message)

    buy_photo = await Database.get_setting("buy_photo", "")
    text = await Database.get_setting("buy_text", (
        "💰 *Buy Crypto*\n\n"
        "ADD MIN $10\n\n"
        "Enter amount in $"
    ))

    if buy_photo:
        msg = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=buy_photo,
            caption=text,
            parse_mode="Markdown",
            reply_markup=amount_entry_keyboard(),
        )
    else:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode="Markdown",
            reply_markup=amount_entry_keyboard(),
        )
        
    context.user_data["last_bot_message_id"] = msg.message_id
    return ENTER_AMOUNT


# ── Conversion-rates popup (stays in ENTER_AMOUNT) ────────────────────────────
async def view_rates_popup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    rates_msg = await Database.get_setting(
        "conversion_rate_message",
        "🔹 Exchange Rates:\n\n🔹 10‑299$ → ₹98\n🔹 300‑1350$ → ₹97\n🔹 1351$+ → ₹96",
    )
    await query.answer(text=rates_msg, show_alert=True)
    return ENTER_AMOUNT


# ── Step 1: Amount entered ─────────────────────────────────────────────────────
async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = update.message.text.strip().replace("$", "").replace(",", "")
    await _delete(update.message)

    # Clean up the previous bot prompt (the photo/text asking for amount)
    last_bot_msg_id = context.user_data.get("last_bot_message_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("last_bot_message_id", None)

    try:
        amount_usd = float(raw)
    except ValueError:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ *Invalid amount. Please enter a number (e.g. `50`).*",
            parse_mode="Markdown",
            reply_markup=amount_entry_keyboard(),
        )
        context.user_data["last_bot_message_id"] = msg.message_id
        return ENTER_AMOUNT

    if amount_usd < 10:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ *Minimum amount is $10. Please try again.*",
            parse_mode="Markdown",
            reply_markup=amount_entry_keyboard(),
        )
        context.user_data["last_bot_message_id"] = msg.message_id
        return ENTER_AMOUNT

    rate       = await get_rate_for_amount(amount_usd)
    amount_inr = round(amount_usd * rate, 2)
    
    context.user_data["amount_usd"] = amount_usd
    context.user_data["amount_inr"] = amount_inr
    context.user_data["rate_used"]  = rate

    # Now ask for USDT network
    network_photo = await Database.get_setting("network_photo", "")
    network_text = (
        f"🔗 *Choose USDT Address*\n\n"
        f"💰 *Buying*: *${amount_usd:,.2f}*\n"
        f"🇮🇳 *You Pay*: *₹{amount_inr:,.0f}* (@ ₹{rate})\n\n"
        f"*Select the network you want to receive USDT on:*"
    )
    if network_photo:
        msg = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=network_photo,
            caption=network_text,
            parse_mode="Markdown",
            reply_markup=network_keyboard(),
        )
    else:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=network_text,
            parse_mode="Markdown",
            reply_markup=network_keyboard(),
        )
    context.user_data["last_bot_message_id"] = msg.message_id
    return CHOOSE_NETWORK


# ── Step 2: Network chosen ─────────────────────────────────────────────────────
async def choose_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)

    network = query.data.split("_")[1]          # "net_bep20" → "bep20"
    context.user_data["network"] = network

    net_label = NETWORK_LABELS.get(network, network.upper())
    
    # Prompt for Receiving Address — using network photo if set
    network_photo = await Database.get_setting("network_photo", "")
    address_text = (
        f"🏦 *Enter USDT Receiving Address*\n\n"
        f"You selected: *{net_label}*\n\n"
        f"Please enter your *USDT Wallet Address* where you want to receive:"
    )
    if network_photo:
        msg = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=network_photo,
            caption=address_text,
            parse_mode="Markdown",
            reply_markup=back_to_main(),
        )
    else:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=address_text,
            parse_mode="Markdown",
            reply_markup=back_to_main(),
        )
    context.user_data["last_bot_message_id"] = msg.message_id
    return ENTER_ADDRESS


# ── Step 3: Address entered ────────────────────────────────────────────────────
async def enter_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_address = update.message.text.strip()
    await _delete(update.message)

    # Clean up the previous bot prompt
    last_bot_msg_id = context.user_data.get("last_bot_message_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("last_bot_message_id", None)

    context.user_data["user_address"] = user_address

    amount_usd = context.user_data.get("amount_usd")
    amount_inr = context.user_data.get("amount_inr")
    rate       = context.user_data.get("rate_used")
    network    = context.user_data.get("network")

    if not all([amount_usd, network]):
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Session expired. Please /start again.",
            reply_markup=back_to_main(),
        )
        context.user_data["last_bot_message_id"] = msg.message_id
        return ConversationHandler.END

    net_label = NETWORK_LABELS.get(network, network.upper())
    order_id  = generate_order_id()

    # Save order (status: awaiting_hash)
    order = await Database.create_order({
        "order_id":               order_id,
        "user_id":                update.effective_user.id,
        "network":                network.upper(),
        "wallet_address":           user_address,
        "amount_usd":             amount_usd,
        "amount_inr":             amount_inr,
        "rate_used":              rate,
        "status":                 "awaiting_hash",
    })

    if not order or not order.get("order_id"):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ **Database Error**: Failed to initialize your order. Please try again later.",
            parse_mode="Markdown",
            reply_markup=back_to_main(),
        )
        return ConversationHandler.END

    context.user_data["current_order_id"] = order_id

    # Ask for Payment Method with optional photo
    pay_method_photo = await Database.get_setting("pay_method_photo", "")
    pay_method_text = (
        f"🏦 *Choose Payment Method*\n\n"
        f"*Please select how you'd like to pay* ₹{amount_inr:,.0f}:"
    )
    if pay_method_photo:
        msg = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=pay_method_photo,
            caption=pay_method_text,
            parse_mode="Markdown",
            reply_markup=payment_method_keyboard(),
        )
    else:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=pay_method_text,
            parse_mode="Markdown",
            reply_markup=payment_method_keyboard(),
        )
    context.user_data["last_bot_message_id"] = msg.message_id
    return CHOOSE_PAYMENT_METHOD


# ── Step 4: Payment Method chosen ──────────────────────────────────────────────
async def choose_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    method = query.data.split("_")[1]  # upi, imps, cdm
    
    if method == "cdm":
        await query.answer("Unavailable, please choose UPI or IMPS", show_alert=True)
        return CHOOSE_PAYMENT_METHOD

    await _delete(query.message)
    context.user_data["payment_method"] = method.upper()

    order_id     = context.user_data.get("current_order_id")
    amount_usd   = context.user_data.get("amount_usd")
    amount_inr   = context.user_data.get("amount_inr")
    rate         = context.user_data.get("rate_used")
    network      = context.user_data.get("network")
    user_address = context.user_data.get("user_address")
    net_label    = NETWORK_LABELS.get(network, network.upper())

    pay_photo = await Database.get_setting(f"{method}_photo", "")
    pay_text  = await Database.get_setting(f"{method}_text", "Payment Details")

    # Clean up the previous bot prompt
    last_bot_msg_id = context.user_data.get("last_bot_message_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("last_bot_message_id", None)

    receipt = (
        f"💳 *PAYMENT DETAILS (TAP TO COPY)*\n"
        f"```\n{pay_text}\n```\n\n"
        f"📋 *Order Details*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Order ID:  `{order_id}`\n"
        f"💰 Receive:   *${amount_usd:,.2f}* ({net_label})\n"
        f"🇮🇳 Pay:       *₹{amount_inr:,.0f}*  (@ ₹{rate}/$)\n"
        f"🏦 To:        `{user_address}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ Tap *Confirm Payment* after making the payment."
    )

    if pay_photo:
        msg = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=pay_photo,
            caption=receipt,
            parse_mode="Markdown",
            reply_markup=payment_proof_keyboard(),
        )
    else:
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=receipt,
            parse_mode="Markdown",
            reply_markup=payment_proof_keyboard(),
        )
    context.user_data["last_bot_message_id"] = msg.message_id
    return AWAIT_PAYMENT_PROOF


# ── Step 5: "I HAVE PAID" button tapped ─────────────────────────────────────────
async def prompt_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)

    method = context.user_data.get("payment_method", "UPI")
    order_id = context.user_data.get("current_order_id", "N/A")

    if method == "IMPS":
        context.user_data["awaiting_screenshot"] = True
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"🖼 *Send Payment Screenshot*\n\n"
                f"🆔 Order: `{order_id}`\n\n"
                f"Please upload the **screenshot** of your IMPS payment now:"
            ),
            parse_mode="Markdown",
            reply_markup=back_to_main(),
        )
        context.user_data["last_bot_message_id"] = msg.message_id
        return AWAIT_SCREENSHOT
    else:
        # UPI - Ask for 12-digit UTR
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"📝 *Submit UTR Number*\n\n"
                f"🆔 Order: `{order_id}`\n\n"
                f"Please enter your **12-digit UTR number** from your UPI transaction:"
            ),
            parse_mode="Markdown",
            reply_markup=back_to_main(),
        )
        context.user_data["last_bot_message_id"] = msg.message_id
        return AWAIT_UTR


# ── Step 6: Screenshot photo received ────────────────────────────────────────────
async def save_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _delete(update.message)

    # Clean up the previous bot prompt
    last_bot_msg_id = context.user_data.get("last_bot_message_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("last_bot_message_id", None)

    if not context.user_data.get("awaiting_screenshot"):
        msg = await update.message.reply_text(
            "Please tap ✅ *I HAVE PAID* button first.",
            parse_mode="Markdown",
            reply_markup=payment_proof_keyboard(),
        )
        context.user_data["last_bot_message_id"] = msg.message_id
        return AWAIT_PAYMENT_PROOF

    file_id  = update.message.photo[-1].file_id
    order_id = context.user_data.get("current_order_id")
    method   = context.user_data.get("payment_method", "UNKNOWN")

    if not order_id:
        msg = await update.message.reply_text(
            "❌ Session expired. Please /start again.",
            reply_markup=back_to_main(),
        )
        context.user_data["last_bot_message_id"] = msg.message_id
        context.user_data.clear()
        return ConversationHandler.END

    success = await Database.update_order_payment(order_id, method, file_id)
    if not success:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ **Error**: Failed to update order status. Please contact support.",
            parse_mode="Markdown",
            reply_markup=back_to_main(),
        )
        return ConversationHandler.END

    amount_usd   = context.user_data.get("amount_usd", 0)
    amount_inr   = context.user_data.get("amount_inr", 0)
    network      = context.user_data.get("network", "?").upper()
    user_address = context.user_data.get("user_address", "Unknown")
    user         = update.effective_user
    
    # Escape markdown characters to prevent parsing errors
    _raw_name = user.username if user.username else user.full_name
    _clean_name = str(_raw_name).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
    username_str = f"@{_clean_name}" if user.username else _clean_name

    proof_text = (
        f"🔔 *New Buy Order Proof*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Order ID:   `{order_id}`\n"
        f"🔗 Network:    *{network}*\n"
        f"💰 User Recv:  *${amount_usd:,.2f}*\n"
        f"🏦 User Addr:  `{user_address}`\n"
        f"🇮🇳 User Paid:  *₹{amount_inr:,.0f}*\n"
        f"💳 Method:     *{method}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User:       {username_str}\n"
        f"🪪 User ID:    `{user.id}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Use buttons below to approve or reject."
    )

    # ── Post to proof channel ──────────────────────────────────────────────────
    proof_channel = await Database.get_setting("proof_channel_id", "")
    if proof_channel:
        try:
            await context.bot.send_photo(
                chat_id=proof_channel,
                photo=file_id,
                caption=proof_text,
                parse_mode="Markdown",
                reply_markup=channel_order_keyboard(order_id),
            )
        except Exception as e:
            logger.error(f"Failed to post to proof channel: {e}")

    # context.user_data.clear() -- Removed redundant DM notifications to admins

    context.user_data.clear()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"✅ **Verification successfully submitted**\n"
            f"**wait 15-20 minutes the payment will be checked and done**"
        ),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def receive_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utr = update.message.text.strip()
    await _delete(update.message)

    # Clean up the previous bot prompt
    last_bot_msg_id = context.user_data.get("last_bot_message_id")
    if last_bot_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_bot_msg_id)
        except Exception:
            pass
        context.user_data.pop("last_bot_message_id", None)

    order_id = context.user_data.get("current_order_id")
    amount   = context.user_data.get("amount_usd")
    address  = context.user_data.get("user_address")
    
    if not order_id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Session expired. Please /start again.",
            reply_markup=back_to_main(),
        )
        return ConversationHandler.END

    if not (utr.isdigit() and len(utr) == 12):
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ *Invalid UTR Number*. Please enter exactly 12 digits.",
            parse_mode="Markdown",
            reply_markup=back_to_main(),
        )
        context.user_data["last_bot_message_id"] = msg.message_id
        return AWAIT_UTR

    success = await Database.update_order_payment(order_id, "UPI", f"UTR: {utr}")
    if not success:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ **Error**: Failed to update order status. Please contact support.",
            parse_mode="Markdown",
            reply_markup=back_to_main(),
        )
        return ConversationHandler.END

    # Escape markdown characters
    user = update.effective_user
    _raw_name = user.username if user.username else user.full_name
    _clean_name = str(_raw_name).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
    username_str = f"@{_clean_name}" if user.username else _clean_name

    proof_text = (
        f"🆕 *NEW UPI ORDER PENDING*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Order ID:  `{order_id}`\n"
        f"💰 Amount:   *${amount:,.2f}*\n"
        f"🏦 Details:  `{address}`\n"
        f"💳 Method:   *UPI*\n"
        f"📝 UTR:      `{utr}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User:      {username_str}\n"
        f"🪪 User ID:   `{user.id}`\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    # Save to DB so channel approve/reject can see it
    await Database.update_order_payment(order_id, "UPI", utr)

    proof_channel = await Database.get_setting("proof_channel_id", "")
    if proof_channel:
        try:
            await context.bot.send_message(chat_id=proof_channel, text=proof_text, parse_mode="Markdown", reply_markup=channel_order_keyboard(order_id))
        except Exception: pass

    # Silenced individual admin DMs
    # for admin_id in ADMIN_IDS:
    #     try:
    #         await context.bot.send_message(chat_id=admin_id, text=proof_text, parse_mode="Markdown", reply_markup=channel_order_keyboard(order_id))
    #     except Exception: pass

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"✅ *Verification Submitted!*\n\n"
            f"Our team will verify your payment within 10-20 minutes. "
            f"You will be notified once crypto is sent."
        ),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


# ── Cancel / fallback back to main menu ───────────────────────────────────────
async def cancel_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    if update.callback_query:
        await update.callback_query.answer()
        await _delete(update.callback_query.message)
    from handlers.start import send_main_menu
    await send_main_menu(update, context, delete_prev=False)
    return ConversationHandler.END


async def cancel_sell_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    from handlers.start import send_main_menu
    await send_main_menu(update, context, delete_prev=False)
    return ConversationHandler.END


# ── ConversationHandler factory ───────────────────────────────────────────────
def get_buy_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(buy_start, pattern="^buy$")],  # Kept "buy" callback to avoid changing start.py keyboards if unnecessary
        states={
            ENTER_AMOUNT: [
                CallbackQueryHandler(view_rates_popup, pattern="^view_rates$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount),
            ],
            CHOOSE_NETWORK: [
                CallbackQueryHandler(choose_network, pattern="^net_(bep20|erc20|ton|trc20)$"),
            ],
            ENTER_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_address),
            ],
            CHOOSE_PAYMENT_METHOD: [
                CallbackQueryHandler(choose_payment_method, pattern="^pay_(upi|imps|cdm)$"),
            ],
            AWAIT_PAYMENT_PROOF: [
                CallbackQueryHandler(prompt_payment_proof, pattern="^submit_proof$"),
            ],
            AWAIT_SCREENSHOT: [
                MessageHandler(filters.PHOTO, save_screenshot),
            ],
            AWAIT_UTR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_utr),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_sell, pattern="^main_menu$"),
            CommandHandler("start", cancel_sell_cmd),
        ],
        allow_reentry=True,
        per_message=False,
    )
