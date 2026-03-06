"""
Crypto Buy Bot — Entry Point
Run with: python main.py
"""

import logging
import asyncio
import sys
from bot import build_app
from database import Database, INSTANCE_ID

logger = logging.getLogger(__name__)


def main():
    # 1. Verify DB connection BEFORE starting bot
    loop = asyncio.get_event_loop()
    connected = loop.run_until_complete(Database.verify_connection())
    
    if not connected:
        logger.error(f"[{INSTANCE_ID}] 🛑 Bot cannot start: Database connection failed!")
        sys.exit(1)

    app = build_app()
    logger.info(f"[{INSTANCE_ID}] Bot starting — polling for updates...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
