-- ============================================================
-- Crypto Buy Bot — Supabase Schema
-- Run this in your Supabase SQL Editor
-- ============================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id     BIGINT PRIMARY KEY,
    username    TEXT DEFAULT '',
    full_name   TEXT DEFAULT '',
    joined_at   TIMESTAMPTZ DEFAULT NOW(),
    total_buys  NUMERIC DEFAULT 0,
    successful_payments INTEGER DEFAULT 0,
    rejected_payments   INTEGER DEFAULT 0,
    total_orders        INTEGER DEFAULT 0
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id              SERIAL PRIMARY KEY,
    order_id        TEXT UNIQUE NOT NULL,
    user_id         BIGINT REFERENCES users(user_id),
    network         TEXT NOT NULL,
    wallet_address   TEXT NOT NULL,
    amount_usd      NUMERIC NOT NULL,
    amount_inr      NUMERIC NOT NULL,
    rate_used       NUMERIC NOT NULL,
    payment_method  TEXT DEFAULT '',
    screenshot_id   TEXT DEFAULT '',
    status          TEXT DEFAULT 'awaiting_payment',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Bot settings table (key-value store)
CREATE TABLE IF NOT EXISTS bot_settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL DEFAULT '',
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Default settings
INSERT INTO bot_settings (key, value) VALUES
    ('main_menu_photo',       ''),
    ('main_menu_text',        '🏠 *Welcome to Crypto Buy Bot*\n\n💎 Buy crypto instantly with INR\n🔒 Secure & Fast transactions\n\nChoose an option below 👇'),
    ('buy_photo',             ''),
    ('buy_text',              '💰 *Choose Crypto Network*\n\nPlease select the network you want to receive your crypto on:'),
    ('stats_photo',           ''),
    ('profile_photo',         ''),
    ('support_username',      '@support'),
    ('proof_channel_id',      ''),
    ('conversion_rate_message',
     '🔹 *Exchange Rates*

🔹 10 - 299$    ➜   💰 Rate: ₹98
🔹 300 - 1350$  ➜   💵 Rate: ₹97
🔹 1351$+       ➜   📈 Rate: ₹96'),
    ('upi_photo',             ''),
    ('upi_text',              'UPI Details:\nUPI ID: test@okicici'),
    ('imps_photo',            ''),
    ('imps_text',             'IMPS Details:\nA/C: 1234567890\nIFSC: ABCD0001234'),
    ('qr_trc20',              ''),
    ('qr_caption_bep20',      '🟡 Send BEP20 to the address below'),
    ('qr_caption_erc20',      '🔷 Send ERC20 to the address below'),
    ('qr_caption_ton',        '💎 Send TON to the address below'),
    ('qr_caption_trc20',      '🔴 Send TRC20 to the address below'),
    ('rate_tier_1_min',       '10'),
    ('rate_tier_1_max',       '299'),
    ('rate_tier_1_rate',      '98'),
    ('rate_tier_2_min',       '300'),
    ('rate_tier_2_max',       '1350'),
    ('rate_tier_2_rate',      '97'),
    ('rate_tier_3_min',       '1351'),
    ('rate_tier_3_rate',      '96')
ON CONFLICT (key) DO NOTHING;

-- Index for fast order lookups
CREATE INDEX IF NOT EXISTS idx_orders_user_id  ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status   ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
