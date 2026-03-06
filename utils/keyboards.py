from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard(support_username: str = "@owner", community_url: str = "") -> InlineKeyboardMarkup:
    support_url = f"https://t.me/{support_username.replace('@', '')}"
    rows = [
        [InlineKeyboardButton("💰 BUY CRYPTO", callback_data="buy")],
        [
            InlineKeyboardButton("🎁 Referral",  callback_data="referral"),
            InlineKeyboardButton("📊 Stats",     callback_data="stats"),
            InlineKeyboardButton("👤 Profile",  callback_data="profile"),
        ],
    ]
    if community_url:
        rows.append([InlineKeyboardButton("👥 Community", url=community_url)])
    rows.append([InlineKeyboardButton("🆘 Support", url=support_url)])
    return InlineKeyboardMarkup(rows)


def network_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟡 BEP20", callback_data="net_bep20"),
            InlineKeyboardButton("🔷 ERC20",  callback_data="net_erc20"),
        ],
        [
            InlineKeyboardButton("💎 TON",   callback_data="net_ton"),
            InlineKeyboardButton("🔴 TRC20", callback_data="net_trc20"),
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")],
    ])


def amount_entry_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 View Exchange Rates", callback_data="view_rates")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")],
    ])


def payment_method_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏛 UPI", callback_data="pay_upi"),
            InlineKeyboardButton("🏦 IMPS", callback_data="pay_imps"),
            InlineKeyboardButton("🏧 CDM", callback_data="pay_cdm"),
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")],
    ])


def payment_proof_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm Payment", callback_data="submit_proof")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")],
    ])


def back_to_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")],
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
            InlineKeyboardButton("🌐 Network Photo",       callback_data="adm_network_photo"),
            InlineKeyboardButton("💳 Pay Method Photo",   callback_data="adm_pay_method_photo"),
        ],
        [
            InlineKeyboardButton("📞 Support Username", callback_data="adm_support"),
            InlineKeyboardButton("💬 Rates Message",    callback_data="adm_conv_msg"),
        ],
        [
            InlineKeyboardButton("🏦 UPI Info",  callback_data="adm_upi"),
            InlineKeyboardButton("🏦 IMPS Info", callback_data="adm_imps"),
        ],
        [
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
            InlineKeyboardButton("🎁 Referral Photo",    callback_data="adm_referral_photo"),
            InlineKeyboardButton("🔗 Referral Link",     callback_data="adm_referral_link"),
        ],
        [
            InlineKeyboardButton("📢 Referral Channel", callback_data="adm_referral_channel"),
        ],
        [
            InlineKeyboardButton("📊 User Stats",    callback_data="adm_user_stats"),
        ],
    ])


def payment_info_action_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼 Set Photo", callback_data="setpay_photo"),
            InlineKeyboardButton("📝 Set Text", callback_data="setpay_text"),
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
