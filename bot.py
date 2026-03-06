import logging
from telegram.ext import Application

from config import BOT_TOKEN
from handlers.start import get_handlers as start_handlers
from handlers.buy import get_buy_conversation
from handlers.profile import get_handlers as profile_handlers
from handlers.stats import get_handlers as stats_handlers
from handlers.support import get_handlers as support_handlers
from handlers.admin import get_admin_conversation
from handlers.channel import get_handlers as channel_handlers

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_app() -> Application:
    app = Application.builder().token(BOT_TOKEN).build()

    # 1. Channel approve/reject (Highest priority)
    for handler in channel_handlers():
        app.add_handler(handler)

    # 2. Admin conversation
    app.add_handler(get_admin_conversation())

    # 3. Buy conversation
    app.add_handler(get_buy_conversation())

    # Simple callback handlers
    for handler in start_handlers():
        app.add_handler(handler)
    for handler in profile_handlers():
        app.add_handler(handler)
    for handler in stats_handlers():
        app.add_handler(handler)
    for handler in support_handlers():
        app.add_handler(handler)

    logger.info("All handlers registered.")
    return app
