import asyncio
import logging
import os
import random
import string
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

# Unique ID for this specific running instance to distinguish in logs
INSTANCE_ID = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def _run(fn):
    """Run a blocking Supabase call in a thread so we don't block the event loop."""
    return await asyncio.to_thread(fn)


class Database:

    @staticmethod
    async def verify_connection():
        """Verify we can actually talk to the DB on startup."""
        def _query():
            try:
                # Mask credentials for logging
                masked_url = f"{SUPABASE_URL[:15]}..." if SUPABASE_URL else "MISSING"
                masked_key = f"{SUPABASE_KEY[:5]}...{SUPABASE_KEY[-5:]}" if SUPABASE_KEY else "MISSING"
                
                logger.info(f"[{INSTANCE_ID}] 🔄 Verifying DB connection...")
                logger.info(f"[{INSTANCE_ID}] 🌐 URL: {masked_url} | 🔑 Key: {masked_key}")
                
                if not SUPABASE_URL or "your-project" in SUPABASE_URL:
                    logger.error(f"[{INSTANCE_ID}] ❌ CRITICAL: SUPABASE_URL is not set correctly!")
                    return False

                # Verify all three main tables and their required columns
                schema_check = {
                    "users": ["user_id", "total_orders"],
                    "orders": ["order_id", "wallet_address", "payment_method", "screenshot_id"],
                    "bot_settings": ["key", "value"]
                }
                
                missing_tables = []
                missing_cols = []

                for table, cols in schema_check.items():
                    try:
                        # Fetch 0 rows but get the column info from the response
                        res = _client.table(table).select("*").limit(0).execute()
                        logger.info(f"[{INSTANCE_ID}] ✅ Table '{table}' verified.")
                        
                        # Check columns if possible (PostgREST usually doesn't return keys if 0 rows, 
                        # but we can try to find them in the response metadata or just try a dummy select)
                        for col in cols:
                            try:
                                _client.table(table).select(col).limit(0).execute()
                            except Exception:
                                missing_cols.append(f"{table}.{col}")
                    except Exception as e:
                        logger.error(f"[{INSTANCE_ID}] ❌ Table '{table}' check error: {e}")
                        missing_tables.append(table)
                
                if missing_tables or missing_cols:
                    if missing_tables: logger.error(f"[{INSTANCE_ID}] 🛑 Missing tables: {missing_tables}")
                    if missing_cols: logger.error(f"[{INSTANCE_ID}] 🛑 Missing columns: {missing_cols}")
                    return False

                logger.info(f"[{INSTANCE_ID}] ✅ DB Connection, Schema & Columns Verified.")
                return True
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] ❌ DB Connection Error: {e}")
                return False
        return await _run(_query)

    # ── Users ──────────────────────────────────────────────────────────────

    @staticmethod
    async def get_or_create_user(user_id: int, username: str, full_name: str) -> dict:
        def _query():
            try:
                _client.table("users").upsert({
                    "user_id": user_id,
                    "username": username,
                    "full_name": full_name
                }, on_conflict="user_id").execute()
                
                res = _client.table("users").select("*").eq("user_id", user_id).execute()
                return res.data[0] if res and res.data else {}
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_or_create_user error: {e}")
                return {}
        return await _run(_query)

    @staticmethod
    async def get_user(user_id: int) -> dict | None:
        def _query():
            try:
                res = _client.table("users").select("*").eq("user_id", user_id).execute()
                return res.data[0] if res and res.data else None
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_user error: {e}")
                return None
        return await _run(_query)

    @staticmethod
    async def get_user_by_username(username: str) -> dict | None:
        def _query():
            try:
                clean_username = username.lstrip("@")
                res = _client.table("users").select("*").eq("username", clean_username).execute()
                return res.data[0] if res and res.data else None
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_user_by_username error: {e}")
                return None
        return await _run(_query)

    @staticmethod
    async def get_all_users_ids() -> list:
        def _query():
            try:
                res = _client.table("users").select("user_id").execute()
                return [row["user_id"] for row in res.data] if res and res.data else []
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_all_users_ids error: {e}")
                return []
        return await _run(_query)

    # ── Orders ─────────────────────────────────────────────────────────────

    @staticmethod
    async def create_order(data: dict) -> dict:
        def _query():
            order_id = data.get('order_id')
            user_id = data.get('user_id')
            logger.info(f"[{INSTANCE_ID}] Database: Attempting to create order {order_id} for user {user_id}")
            
            try:
                # 1. Ensure user exists first (Foreign Key protection)
                u_check = _client.table("users").select("user_id").eq("user_id", user_id).execute()
                if not u_check.data:
                    logger.info(f"[{INSTANCE_ID}] User {user_id} not in DB. Creating minimal record first.")
                    _client.table("users").upsert({"user_id": user_id}).execute()

                # 2. Insert order
                res = _client.table("orders").insert(data).execute()
                
                if not res or not res.data:
                    logger.error(f"[{INSTANCE_ID}] Database: create_order returned NO DATA. Response: {res}")
                    return {}
                
                order = res.data[0]
                logger.info(f"[{INSTANCE_ID}] Database: Order {order_id} saved successfully with DB ID: {order.get('id')}")

                # 3. Increment total_orders on user
                try:
                    _client.rpc('increment_total_orders', {'u_id': user_id}).execute()
                except Exception:
                    # Fallback to manual update if RPC missing
                    try:
                        u_res = _client.table("users").select("total_orders").eq("user_id", user_id).execute()
                        if u_res and u_res.data:
                            curr = u_res.data[0].get("total_orders") or 0
                            _client.table("users").update({"total_orders": curr + 1}).eq("user_id", user_id).execute()
                    except Exception as u_err:
                        logger.error(f"[{INSTANCE_ID}] Database: User counter update failed: {u_err}")

                return order
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] Database: create_order CRITICAL exception: {e}", exc_info=True)
                # Check for RLS issues or missing columns
                if "contains both an update and an insert" in str(e):
                    logger.error(f"[{INSTANCE_ID}] Potential upsert conflict or schema issue.")
                return {}
        return await _run(_query)

    @staticmethod
    async def update_order_payment(order_id: str, payment_method: str, screenshot_id: str) -> bool:
        def _query():
            logger.info(f"[{INSTANCE_ID}] Database: Updating payment for {order_id} (Method: {payment_method})")
            try:
                res = _client.table("orders").update(
                    {"payment_method": payment_method, "screenshot_id": screenshot_id, "status": "pending"}
                ).eq("order_id", order_id).execute()
                
                success = bool(res and res.data)
                if not success:
                    logger.warning(f"[{INSTANCE_ID}] Database: update_order_payment NO DATA returned for {order_id}")
                return success
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] Database: update_order_payment error: {e}")
                return False
        return await _run(_query)

    @staticmethod
    async def approve_order(order_id: str) -> dict | None:
        def _query():
            try:
                res_f = _client.table("orders").select("*").eq("order_id", order_id).execute()
                if not res_f or not res_f.data:
                    logger.warning(f"[{INSTANCE_ID}] approve_order: Order {order_id} not found.")
                    try:
                        rcnt = _client.table("orders").select("order_id").order("created_at", desc=True).limit(5).execute()
                        ids = [o['order_id'] for o in rcnt.data] if rcnt and rcnt.data else []
                        logger.info(f"[{INSTANCE_ID}] Recent IDs in DB: {ids}")
                    except: pass
                    return None
                
                order = res_f.data[0]
                _client.table("orders").update({"status": "approved"}).eq("order_id", order_id).execute()
                order["status"] = "approved"

                try:
                    uid = order.get("user_id")
                    if uid:
                        u_res = _client.table("users").select("*").eq("user_id", uid).execute()
                        if u_res and u_res.data:
                            user_data = u_res.data[0]
                            succ = (user_data.get("successful_payments") or 0) + 1
                            prev_buys = 0
                            try: prev_buys = float(user_data.get("total_buys") or 0)
                            except: pass
                            curr_amt = 0
                            try: curr_amt = float(order.get("amount_usd") or 0)
                            except: pass
                            _client.table("users").update({
                                "successful_payments": succ,
                                "total_buys": prev_buys + curr_amt,
                            }).eq("user_id", uid).execute()
                except Exception as user_err:
                    logger.error(f"[{INSTANCE_ID}] User stats update failed: {user_err}")
                
                return order
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] approve_order CRITICAL error for {order_id}: {e}", exc_info=True)
                return None
        return await _run(_query)

    @staticmethod
    async def reject_order(order_id: str) -> dict | None:
        def _query():
            try:
                res_f = _client.table("orders").select("*").eq("order_id", order_id).execute()
                if not res_f or not res_f.data:
                    logger.warning(f"[{INSTANCE_ID}] reject_order: Order {order_id} not found.")
                    try:
                        rcnt = _client.table("orders").select("order_id").order("created_at", desc=True).limit(5).execute()
                        ids = [o['order_id'] for o in rcnt.data] if rcnt and rcnt.data else []
                        logger.info(f"[{INSTANCE_ID}] Recent IDs in DB: {ids}")
                    except: pass
                    return None
                
                order = res_f.data[0]
                _client.table("orders").update({"status": "rejected"}).eq("order_id", order_id).execute()
                order["status"] = "rejected"

                try:
                    uid = order.get("user_id")
                    if uid:
                        u_res = _client.table("users").select("rejected_payments").eq("user_id", uid).execute()
                        if u_res and u_res.data:
                            rejs = (u_res.data[0].get("rejected_payments") or 0) + 1
                            _client.table("users").update({"rejected_payments": rejs}).eq("user_id", uid).execute()
                except Exception as user_err:
                    logger.error(f"[{INSTANCE_ID}] User stats update failed: {user_err}")
                
                return order
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] reject_order CRITICAL error for {order_id}: {e}", exc_info=True)
                return None
        return await _run(_query)

    @staticmethod
    async def get_pending_orders(limit: int = 15) -> list:
        def _query():
            try:
                res = _client.table("orders").select("*").eq("status", "pending").order("created_at", desc=True).limit(limit).execute()
                return res.data or []
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_pending_orders error: {e}")
                return []
        return await _run(_query)

    @staticmethod
    async def get_user_orders(user_id: int, limit: int = 50) -> list:
        def _query():
            try:
                res = _client.table("orders").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
                return res.data or []
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_user_orders error: {e}")
                return []
        return await _run(_query)

    @staticmethod
    async def get_all_orders(limit: int = 15) -> list:
        def _query():
            try:
                res = _client.table("orders").select("*").order("created_at", desc=True).limit(limit).execute()
                return res.data or []
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_all_orders error: {e}")
                return []
        return await _run(_query)

    @staticmethod
    async def get_order_by_id(order_id: str) -> dict | None:
        def _query():
            try:
                res = _client.table("orders").select("*").eq("order_id", order_id).execute()
                return res.data[0] if res and res.data else None
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_order_by_id error: {e}")
                return None
        return await _run(_query)

    @staticmethod
    async def get_setting(key: str, default: str = "") -> str:
        def _query():
            try:
                res = _client.table("bot_settings").select("value").eq("key", key).execute()
                return res.data[0]["value"] if res and res.data else default
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_setting({key}) error: {e}")
                return default
        return await _run(_query)

    @staticmethod
    async def set_setting(key: str, value: str) -> bool:
        def _query():
            try:
                _client.table("bot_settings").upsert({"key": key, "value": value}).execute()
                return True
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] set_setting({key}) error: {e}")
                return False
        return await _run(_query)

    @staticmethod
    async def get_stats() -> dict:
        def _query():
            try:
                u_res = _client.table("users").select("user_id", count="exact").execute()
                o_res = _client.table("orders").select("amount_usd,status", count="exact").execute()
                total_usd = 0.0
                succ = pend = rej = 0
                for o in (o_res.data or []):
                    status = o.get("status")
                    if status == "approved":
                        succ += 1
                        total_usd += float(o.get("amount_usd") or 0)
                    elif status == "pending":
                        pend += 1
                    elif status == "rejected":
                        rej += 1
                return {
                    "total_users": u_res.count or 0,
                    "total_orders": o_res.count or 0,
                    "total_usd": total_usd,
                    "successful": succ,
                    "pending": pend,
                    "rejected": rej,
                }
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_stats error: {e}")
                return {}
        return await _run(_query)

    @staticmethod
    async def get_users_list(offset: int = 0, limit: int = 10) -> list:
        def _query():
            try:
                res = _client.table("users").select("*").order("joined_at", desc=True).range(offset, offset + limit - 1).execute()
                return res.data or []
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_users_list error: {e}")
                return []
        return await _run(_query)

    @staticmethod
    async def get_users_count() -> int:
        def _query():
            try:
                res = _client.table("users").select("user_id", count="exact").execute()
                return res.count or 0
            except Exception as e:
                logger.error(f"[{INSTANCE_ID}] get_users_count error: {e}")
                return 0
        return await _run(_query)
