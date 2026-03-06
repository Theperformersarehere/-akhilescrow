import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import Database

logger = logging.getLogger(__name__)


import html

async def channel_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Processing approval...", show_alert=False)

    try:
        order_id = query.data[len("ch_approve_"):]
        logger.info(f"Channel approval triggered for Order ID: {order_id}")
        
        order = await Database.approve_order(order_id)

        if not order:
            await query.answer("❌ Order not found or already processed.", show_alert=True)
            return

        # Prepare fields
        o_id   = html.escape(str(order_id))
        method = html.escape(str(order.get('payment_method', '—')))
        addr   = html.escape(str(order.get('user_receiving_address', '—')))
        uid    = str(order['user_id'])
        amt    = float(order['amount_usd'])

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
        except Exception as e:
            logger.error(f"Failed to edit channel message on approve: {e}")

        # Notify user
        try:
            await context.bot.send_message(
                chat_id=order["user_id"],
                text=(
                    f"✅ <b>Payment Approved!</b>\n\n"
                    f"🆔 Order: <code>{o_id}</code>\n"
                    f"💰 ${amt:,.2f}\n\n"
                    f"Your crypto will be sent to your given details shortly. Thank you! 🙏"
                ),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to notify user on approve: {e}")
            
    except Exception as e:
        logger.error(f"Critical error in channel_approve: {e}", exc_info=True)
        await query.answer(f"❌ Error: {str(e)[:100]}", show_alert=True)


async def channel_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Processing rejection...", show_alert=False)

    try:
        order_id = query.data[len("ch_reject_"):]
        logger.info(f"Channel rejection triggered for Order ID: {order_id}")
        
        order = await Database.reject_order(order_id)

        if not order:
            await query.answer("❌ Order not found or already processed.", show_alert=True)
            return

        # Prepare fields
        o_id   = html.escape(str(order_id))
        method = html.escape(str(order.get('payment_method', '—')))
        addr   = html.escape(str(order.get('user_receiving_address', '—')))
        uid    = str(order['user_id'])
        amt    = float(order['amount_usd'])

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
        except Exception as e:
            logger.error(f"Failed to edit channel message on reject: {e}")

        # Notify user
        try:
            await context.bot.send_message(
                chat_id=order["user_id"],
                text=(
                    f"❌ <b>Payment Rejected</b>\n\n"
                    f"🆔 Order: <code>{o_id}</code>\n\n"
                    f"Your payment could not be verified. "
                    f"Please contact support for assistance."
                ),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to notify user on reject: {e}")
            
    except Exception as e:
        logger.error(f"Critical error in channel_reject: {e}", exc_info=True)
        await query.answer(f"❌ Error: {str(e)[:100]}", show_alert=True)


def get_handlers():
    return [
        CallbackQueryHandler(channel_approve, pattern=r"^ch_approve_.+"),
        CallbackQueryHandler(channel_reject,  pattern=r"^ch_reject_.+"),
    ]
