import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters,
)

from database import Database
from utils.keyboards import (
    network_keyboard, amount_entry_keyboard, receipt_keyboard, back_to_main,
    channel_order_keyboard,
)
from utils.order_id import generate_order_id
from utils.exchange_rate import get_rate_for_amount
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

# ── Conversation states ────────────────────────────────────────────────────────
ENTER_AMOUNT, CHOOSE_NETWORK, ENTER_ADDRESS, AWAIT_TX_HASH = range(4)

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
    except Exception:
        pass


# ── Entry: user taps "Buy Crypto" ─────────────────────────────────────────────
async def buy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)

    buy_photo = await Database.get_setting("buy_photo", "")
    text = await Database.get_setting("buy_text", (
        "💰 *Buy Crypto*\n\n"
        "Enter amount in $"
    ))

    if buy_photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=buy_photo,
            caption=text,
            parse_mode="Markdown",
            reply_markup=amount_entry_keyboard(),
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode="Markdown",
            reply_markup=amount_entry_keyboard(),
        )
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

    try:
        amount_usd = float(raw)
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Invalid amount. Please enter a number (e.g. `50`).",
            parse_mode="Markdown",
            reply_markup=amount_entry_keyboard(),
        )
        return ENTER_AMOUNT

    if amount_usd < 10:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Minimum amount is *$10*. Please try again.",
            parse_mode="Markdown",
            reply_markup=amount_entry_keyboard(),
        )
        return ENTER_AMOUNT

    rate       = await get_rate_for_amount(amount_usd)
    amount_inr = round(amount_usd * rate, 2)
    
    context.user_data["amount_usd"] = amount_usd
    context.user_data["amount_inr"] = amount_inr
    context.user_data["rate_used"]  = rate

    # Now ask for network
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"🔗 *Choose Blockchain Network*\n\n"
            f"💰 Buying: *${amount_usd:,.2f}*\n"
            f"🇮🇳 You Pay: *₹{amount_inr:,.0f}* (@ ₹{rate})\n\n"
            f"Select the network you want to receive crypto on:"
        ),
        parse_mode="Markdown",
        reply_markup=network_keyboard(),
    )
    return CHOOSE_NETWORK


# ── Step 2: Network chosen ─────────────────────────────────────────────────────
async def choose_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)

    network = query.data.split("_")[1]          # "net_bep20" → "bep20"
    context.user_data["network"] = network

    net_label = NETWORK_LABELS.get(network, network.upper())
    
    # Prompt for Receiving Address
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"🏦 *Enter Receiving Details*\n\n"
            f"You selected: *{net_label}*\n\n"
            f"Please enter your *Crypto Wallet Address* where you want to receive the crypto:"
        ),
        parse_mode="Markdown",
        reply_markup=back_to_main(),
    )
    return ENTER_ADDRESS


# ── Step 3: Address entered ────────────────────────────────────────────────────
async def enter_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_address = update.message.text.strip()
    await _delete(update.message)

    context.user_data["user_address"] = user_address

    amount_usd = context.user_data.get("amount_usd")
    amount_inr = context.user_data.get("amount_inr")
    rate       = context.user_data.get("rate_used")
    network    = context.user_data.get("network")

    if not all([amount_usd, network]):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Session expired. Please /start again.",
            reply_markup=back_to_main(),
        )
        return ConversationHandler.END

    net_label = NETWORK_LABELS.get(network, network.upper())
    order_id  = generate_order_id()

    # Save order (status: awaiting_hash)
    await Database.create_order({
        "order_id":               order_id,
        "user_id":                update.effective_user.id,
        "network":                network.upper(),
        "user_receiving_address": user_address,
        "amount_usd":             amount_usd,
        "amount_inr":             amount_inr,
        "rate_used":              rate,
        "status":                 "awaiting_hash",
    })

    context.user_data["current_order_id"] = order_id

    qr_file_id  = await Database.get_setting(f"qr_{network}", "")
    qr_caption  = await Database.get_setting(f"qr_caption_{network}", f"Send {net_label} to the address below:")

    receipt = (
        f"{qr_caption}\n\n"
        f"📋 *Order Details*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Order ID:  `{order_id}`\n"
        f"💰 Receive:   *${amount_usd:,.2f}* ({net_label})\n"
        f"🇮🇳 Pay:       *₹{amount_inr:,.0f}*  (@ ₹{rate}/$)\n"
        f"🏦 To:        `{user_address}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ Tap *Submit UTR* after making the payment."
    )

    if qr_file_id:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=qr_file_id,
            caption=receipt,
            parse_mode="Markdown",
            reply_markup=receipt_keyboard(),
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=receipt,
            parse_mode="Markdown",
            reply_markup=receipt_keyboard(),
        )
    return AWAIT_TX_HASH


# ── Step 4a: "Submit UTR" button tapped ───────────────────────────────────────
async def prompt_tx_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _delete(query.message)

    order_id = context.user_data.get("current_order_id", "N/A")
    context.user_data["awaiting_hash_text"] = True

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"💳 *Enter Your UTR / Transaction Hash*\n\n"
            f"🆔 Order: `{order_id}`\n\n"
            f"Please type your UTR, TxHash, or transaction reference number:"
        ),
        parse_mode="Markdown",
        reply_markup=back_to_main(),
    )
    return AWAIT_TX_HASH


# ── Step 4b: TX Hash text received ────────────────────────────────────────────
async def save_tx_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_hash_text"):
        await update.message.reply_text(
            "Please tap ✅ *Submit UTR* button first.",
            parse_mode="Markdown",
            reply_markup=receipt_keyboard(),
        )
        return AWAIT_TX_HASH

    tx_hash  = update.message.text.strip()
    order_id = context.user_data.get("current_order_id")

    if not order_id:
        await update.message.reply_text(
            "❌ Session expired. Please /start again.",
            reply_markup=back_to_main(),
        )
        context.user_data.clear()
        return ConversationHandler.END

    await _delete(update.message)
    await Database.update_order_utr(order_id, tx_hash)

    amount_usd   = context.user_data.get("amount_usd", 0)
    amount_inr   = context.user_data.get("amount_inr", 0)
    network      = context.user_data.get("network", "?").upper()
    user_address = context.user_data.get("user_address", "Unknown")
    user         = update.effective_user
    username_str = f"@{user.username}" if user.username else f"{user.full_name}"

    proof_text = (
        f"🔔 *New Buy Order Proof*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Order ID:   `{order_id}`\n"
        f"🔗 Network:    *{network}*\n"
        f"💰 User Recv:  *${amount_usd:,.2f}*\n"
        f"🏦 User Addr:  `{user_address}`\n"
        f"🇮🇳 User Paid:  *₹{amount_inr:,.0f}*\n"
        f"🔢 UTR:        `{tx_hash}`\n"
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
            await context.bot.send_message(
                chat_id=proof_channel,
                text=proof_text,
                parse_mode="Markdown",
                reply_markup=channel_order_keyboard(order_id),
            )
        except Exception as e:
            logger.error(f"Failed to post to proof channel: {e}")

    # ── Notify individual admins (DM) ─────────────────────────────────────────
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=proof_text,
                parse_mode="Markdown",
                reply_markup=channel_order_keyboard(order_id),
            )
        except Exception:
            pass

    context.user_data.clear()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"**Utr successfully submitted**\n"
            f"**wait 15-20 minutes the payment will be checked and done**"
        ),
        parse_mode="Markdown",
        reply_markup=back_to_main(),
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
            AWAIT_TX_HASH: [
                CallbackQueryHandler(prompt_tx_hash, pattern="^submit_utr$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_tx_hash),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_sell, pattern="^main_menu$"),
            CommandHandler("start", cancel_sell_cmd),
        ],
        allow_reentry=True,
        per_message=False,
    )
