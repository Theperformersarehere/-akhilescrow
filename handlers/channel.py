import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import Database

logger = logging.getLogger(__name__)


async def channel_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # We answer immediately to satisfy Telegram, but don't show alert yet unless it's a slow process
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
            logger.warning(f"Order {order_id} not found in DB during appproval.")
            await query.answer("❌ Order not found in database.", show_alert=True)
            return

        # Prepare fields
        o_id   = html.escape(str(order_id))
        method = html.escape(str(order.get('payment_method', '—')))
        addr   = html.escape(str(order.get('user_receiving_address', '—')))
        uid    = str(order.get('user_id', 'Unknown'))
        amt    = 0
        try: amt = float(order.get('amount_usd', 0))
        except: pass

        logger.info(f"Order {order_id} fetched successfully. Attempting to edit channel message...")

        # Edit channel message to show approved status
        try:
            await query.edit_message_caption(
                caption=(
                    f"✅ <b>APPROVED</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 Order ID:  <code>{o_id}</code>\n"
                    f"💰 Amount:   <b>${amt:,.2f}</b>\n"
                    f"🏦 Details:  <code>{addr}</code>\n"
                    f"💳 Method:   <b>{method}</b>\n"
                    f"👤 User ID:  <code>{uid}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ Approved and user notified."
                ),
                parse_mode="HTML",
            )
            logger.info(f"Channel message for {order_id} edited successfully.")
        except Exception as edit_err:
            logger.error(f"Failed to edit channel message on approve: {edit_err}")

        # Notify user
        try:
            target_id = order.get("user_id")
            if target_id:
                await context.bot.send_message(
                    chat_id=target_id,
                    text=(
                        f"✅ <b>Payment Approved!</b>\n\n"
                        f"🆔 Order: <code>{o_id}</code>\n"
                        f"💰 ${amt:,.2f}\n\n"
                        f"Your crypto will be sent to your given details shortly. Thank you! 🙏"
                    ),
                    parse_mode="HTML",
                )
                logger.info(f"User {target_id} notified for order {order_id}.")
            else:
                logger.error(f"No user_id found for order {order_id}, cannot notify user.")
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
        o_id   = html.escape(str(order_id))
        method = html.escape(str(order.get('payment_method', '—')))
        addr   = html.escape(str(order.get('user_receiving_address', '—')))
        uid    = str(order.get('user_id', 'Unknown'))
        amt    = 0
        try: amt = float(order.get('amount_usd', 0))
        except: pass

        logger.info(f"Order {order_id} fetched successfully. Attempting to edit channel message...")

        # Edit channel message to show rejected status
        try:
            await query.edit_message_caption(
                caption=(
                    f"❌ <b>REJECTED</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 Order ID:  <code>{o_id}</code>\n"
                    f"💰 Amount:   <b>${amt:,.2f}</b>\n"
                    f"🏦 Details:  <code>{addr}</code>\n"
                    f"💳 Method:   <b>{method}</b>\n"
                    f"👤 User ID:  <code>{uid}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"❌ Rejected and user notified."
                ),
                parse_mode="HTML",
            )
            logger.info(f"Channel message for {order_id} edited successfully.")
        except Exception as edit_err:
            logger.error(f"Failed to edit channel message on reject: {edit_err}")

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
                logger.info(f"User {target_id} notified for rejection of order {order_id}.")
            else:
                logger.error(f"No user_id found for order {order_id}, cannot notify user.")
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
