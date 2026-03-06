import logging
import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import Database

logger = logging.getLogger(__name__)


async def _edit_message(query, caption: str):
    """Try edit_message_caption (photo), fall back to edit_message_text."""
    try:
        await query.edit_message_caption(caption=caption, parse_mode="HTML")
        return True
    except Exception as cap_err:
        logger.warning(f"edit_message_caption failed ({cap_err}), trying edit_message_text...")
    try:
        await query.edit_message_text(text=caption, parse_mode="HTML")
        return True
    except Exception as txt_err:
        logger.error(f"edit_message_text also failed: {txt_err}")
        return False


async def channel_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Processing approval...", show_alert=False)

    try:
        data = query.data
        if not data.startswith("ch_approve_"):
            logger.error(f"Invalid callback data for channel_approve: {data}")
            return

        order_id = data[len("ch_approve_"):]
        logger.info(f"--- CHANNEL APPROVE START: {order_id} ---")
        
        order = await Database.approve_order(order_id)

        if not order:
            logger.warning(f"Order {order_id} not found in DB during approval.")
            await query.answer("❌ Order not found in database.", show_alert=True)
            return

        # Prepare fields
        o_id    = html.escape(str(order_id))
        method  = html.escape(str(order.get('payment_method', '—')))
        addr    = html.escape(str(order.get('wallet_address', '—')))
        utr     = html.escape(str(order.get('screenshot_id', '—')))
        uid     = str(order.get('user_id', 'Unknown'))
        amt     = 0
        amt_inr = 0
        try:
            amt     = float(order.get('amount_usd', 0))
            amt_inr = float(order.get('amount_inr', 0))
        except Exception:
            pass

        logger.info(f"Order {order_id} fetched. Editing channel message...")

        receipt = (
            f"✅ <b>APPROVED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 Order ID:  <code>{o_id}</code>\n"
            f"💰 Amount:   <b>${amt:,.2f}</b>\n"
            f"🇮🇳 Paid:     <b>₹{amt_inr:,.0f}</b>\n"
            f"🏦 Details:  <code>{addr}</code>\n"
            f"💳 Method:   <b>{method}</b>\n"
            f"✍️ UTR:      <b>{utr}</b>\n"
            f"👤 User ID:  <code>{uid}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Approved and user notified."
        )

        edited = await _edit_message(query, receipt)
        if edited:
            logger.info(f"Channel message for {order_id} edited successfully.")
        else:
            logger.error(f"Could not edit channel message for {order_id}.")

        # Notify user
        try:
            target_id = order.get("user_id")
            if target_id:
                await context.bot.send_message(
                    chat_id=target_id,
                    text=(
                        f"✅ <b>Payment Approved!</b>\n\n"
                        f"🆔 Order: <code>{o_id}</code>\n"
                        f"💰 Amount: <b>${amt:,.2f}</b>\n"
                        f"🇮🇳 Paid: <b>₹{amt_inr:,.0f}</b>\n\n"
                        f"Your crypto will be sent to your given details shortly. Thank you! 🙏"
                    ),
                    parse_mode="HTML",
                )
                logger.info(f"User {target_id} notified for order {order_id}.")
            else:
                logger.error(f"No user_id found for order {order_id}.")
        except Exception as notify_err:
            logger.error(f"Failed to notify user on approve: {notify_err}")

    except Exception as e:
        logger.error(f"CRITICAL error in channel_approve: {e}", exc_info=True)
        await query.answer(f"❌ System Error: {str(e)[:50]}", show_alert=True)


async def channel_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Processing rejection...", show_alert=False)

    try:
        data = query.data
        if not data.startswith("ch_reject_"):
            logger.error(f"Invalid callback data for channel_reject: {data}")
            return

        order_id = data[len("ch_reject_"):]
        logger.info(f"--- CHANNEL REJECT START: {order_id} ---")

        order = await Database.reject_order(order_id)

        if not order:
            logger.warning(f"Order {order_id} not found in DB during rejection.")
            await query.answer("❌ Order not found in database.", show_alert=True)
            return

        # Prepare fields
        o_id    = html.escape(str(order_id))
        method  = html.escape(str(order.get('payment_method', '—')))
        addr    = html.escape(str(order.get('wallet_address', '—')))
        utr     = html.escape(str(order.get('screenshot_id', '—')))
        uid     = str(order.get('user_id', 'Unknown'))
        amt     = 0
        amt_inr = 0
        try:
            amt     = float(order.get('amount_usd', 0))
            amt_inr = float(order.get('amount_inr', 0))
        except Exception:
            pass

        logger.info(f"Order {order_id} fetched. Editing channel message...")

        receipt = (
            f"❌ <b>REJECTED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 Order ID:  <code>{o_id}</code>\n"
            f"💰 Amount:   <b>${amt:,.2f}</b>\n"
            f"🇮🇳 Paid:     <b>₹{amt_inr:,.0f}</b>\n"
            f"🏦 Details:  <code>{addr}</code>\n"
            f"💳 Method:   <b>{method}</b>\n"
            f"✍️ UTR:      <b>{utr}</b>\n"
            f"👤 User ID:  <code>{uid}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ Rejected and user notified."
        )

        edited = await _edit_message(query, receipt)
        if edited:
            logger.info(f"Channel message for {order_id} edited successfully.")
        else:
            logger.error(f"Could not edit channel message for {order_id}.")

        # Notify user
        try:
            target_id = order.get("user_id")
            if target_id:
                await context.bot.send_message(
                    chat_id=target_id,
                    text=(
                        f"❌ <b>Payment Rejected</b>\n\n"
                        f"🆔 Order: <code>{o_id}</code>\n\n"
                        f"Your payment could not be verified. "
                        f"Please contact support for assistance."
                    ),
                    parse_mode="HTML",
                )
                logger.info(f"User {target_id} notified for rejection of {order_id}.")
            else:
                logger.error(f"No user_id found for order {order_id}.")
        except Exception as notify_err:
            logger.error(f"Failed to notify user on reject: {notify_err}")

    except Exception as e:
        logger.error(f"CRITICAL error in channel_reject: {e}", exc_info=True)
        await query.answer(f"❌ System Error: {str(e)[:50]}", show_alert=True)


def get_handlers():
    return [
        CallbackQueryHandler(channel_approve, pattern=r"^ch_approve_.+"),
        CallbackQueryHandler(channel_reject,  pattern=r"^ch_reject_.+"),
    ]
