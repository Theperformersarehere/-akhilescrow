from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard(support_username: str = "@owner") -> InlineKeyboardMarkup:
    support_url = f"https://t.me/{support_username.replace('@', '')}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 𝗕𝗨𝗬 𝗖𝗥𝗬𝗣𝗧𝗢", callback_data="buy")],
        [
            InlineKeyboardButton("📊 𝗦𝗧𝗔𝗧𝗦",   callback_data="stats"),
            InlineKeyboardButton("👤 𝗣𝗥𝗢𝗙𝗜𝗟𝗘", callback_data="profile"),
        ],
        [InlineKeyboardButton("🆘 𝗦𝗨𝗣𝗣𝗢𝗥𝗧", url=support_url)],
    ])


def network_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟡 𝗕𝗘𝗣𝟮𝟬", callback_data="net_bep20"),
            InlineKeyboardButton("🔷 𝗘𝗥𝗖𝟮𝟬",  callback_data="net_erc20"),
        ],
        [
            InlineKeyboardButton("💎 𝗧𝗢𝗡",   callback_data="net_ton"),
            InlineKeyboardButton("🔴 𝗧𝗥𝗖𝟮𝟬", callback_data="net_trc20"),
        ],
        [InlineKeyboardButton("🏠 𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨", callback_data="main_menu")],
    ])


def amount_entry_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 𝗩𝗜𝗘𝗪 𝗘𝗫𝗖𝗛𝗔𝗡𝗚𝗘 𝗥𝗔𝗧𝗘𝗦", callback_data="view_rates")],
        [InlineKeyboardButton("🏠 𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨", callback_data="main_menu")],
    ])


def receipt_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ 𝗦𝗨𝗕𝗠𝗜𝗧 𝗨𝗧𝗥", callback_data="submit_utr")],
        [InlineKeyboardButton("🏠 𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨", callback_data="main_menu")],
    ])


def back_to_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨", callback_data="main_menu")],
    ])


# ── Admin keyboards ────────────────────────────────────────────────────────────

def admin_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼 Main Photo",  callback_data="adm_main_photo"),
            InlineKeyboardButton("📝 Main Text",   callback_data="adm_main_text"),
        ],
        [
            InlineKeyboardButton("💳 Buy Photo",   callback_data="adm_pay_photo"),
            InlineKeyboardButton("📝 Buy Text",    callback_data="adm_pay_text"),
        ],
        [
            InlineKeyboardButton("📊 Stats Photo",      callback_data="adm_stats_photo"),
            InlineKeyboardButton("👤 Profile Photo",    callback_data="adm_profile_photo"),
        ],
        [
            InlineKeyboardButton("📞 Support Username", callback_data="adm_support"),
            InlineKeyboardButton("💬 Rates Message",    callback_data="adm_conv_msg"),
        ],
        [
            InlineKeyboardButton("📷 QR Codes & Msgs",  callback_data="adm_qr"),
            InlineKeyboardButton("📢 Proof Channel",    callback_data="adm_channel"),
        ],
        [
            InlineKeyboardButton("📈 Exchange Rate Tiers", callback_data="adm_rates"),
        ],
        [
            InlineKeyboardButton("📦 All Orders",    callback_data="adm_orders"),
            InlineKeyboardButton("⏳ Pending Only",  callback_data="adm_pending"),
        ],
        [
            InlineKeyboardButton("✅ Approve Order", callback_data="adm_approve"),
            InlineKeyboardButton("❌ Reject Order",  callback_data="adm_reject"),
        ],
    ])


def network_choice_keyboard(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("BEP20", callback_data=f"{prefix}_bep20"),
            InlineKeyboardButton("ERC20", callback_data=f"{prefix}_erc20"),
        ],
        [
            InlineKeyboardButton("TON",   callback_data=f"{prefix}_ton"),
            InlineKeyboardButton("TRC20", callback_data=f"{prefix}_trc20"),
        ],
        [InlineKeyboardButton("↩️ Admin Menu", callback_data="adm_back")],
    ])


def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Cancel", callback_data="adm_back")],
    ])


def channel_order_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Approve / Reject buttons posted to the proof channel."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"ch_approve_{order_id}"),
            InlineKeyboardButton("❌ Reject",  callback_data=f"ch_reject_{order_id}"),
        ]
    ])
