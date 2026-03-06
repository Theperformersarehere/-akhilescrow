import asyncio
import logging
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def _run(fn):
    """Run a blocking Supabase call in a thread so we don't block the event loop."""
    return await asyncio.to_thread(fn)


class Database:

    # ── Users ──────────────────────────────────────────────────────────────

    @staticmethod
    async def get_or_create_user(user_id: int, username: str, full_name: str) -> dict:
        def _query():
            try:
                # Upsert user info
                res = _client.table("users").upsert({
                    "user_id": user_id,
                    "username": username,
                    "full_name": full_name
                }, on_conflict="user_id").execute()
                
                # Fetch the full record to ensure all defaults and joined_at are present
                fresh = _client.table("users").select("*").eq("user_id", user_id).maybe_single().execute()
                return fresh.data or {}
            except Exception as e:
                logger.error(f"get_or_create_user error: {e}")
                return {}
        return await _run(_query)

    @staticmethod
    async def get_user(user_id: int) -> dict | None:
        def _query():
            try:
                res = _client.table("users").select("*").eq("user_id", user_id).maybe_single().execute()
                return res.data
            except Exception as e:
                logger.error(f"get_user error: {e}")
                return None
        return await _run(_query)

    @staticmethod
    async def get_user_by_username(username: str) -> dict | None:
        def _query():
            try:
                # Remove @ if present
                clean_username = username.lstrip("@")
                res = _client.table("users").select("*").eq("username", clean_username).maybe_single().execute()
                return res.data
            except Exception as e:
                logger.error(f"get_user_by_username error: {e}")
                return None
        return await _run(_query)

    @staticmethod
    async def get_all_users_ids() -> list:
        def _query():
            try:
                res = _client.table("users").select("user_id").execute()
                return [row["user_id"] for row in res.data] if res.data else []
            except Exception as e:
                logger.error(f"get_all_users_ids error: {e}")
                return []
        return await _run(_query)

    # ── Orders ─────────────────────────────────────────────────────────────

    @staticmethod
    async def create_order(data: dict) -> dict:
        def _query():
            try:
                res = _client.table("orders").insert(data).execute()
                # Increment total_orders on user
                _client.table("users").rpc  # placeholder
                u = _client.table("users").select("total_orders").eq("user_id", data["user_id"]).maybe_single().execute()
                if u.data is not None:
                    _client.table("users").update(
                        {"total_orders": (u.data.get("total_orders") or 0) + 1}
                    ).eq("user_id", data["user_id"]).execute()
                return res.data[0] if res.data else {}
            except Exception as e:
                logger.error(f"create_order error: {e}")
                return {}
        return await _run(_query)

    @staticmethod
    async def update_order_payment(order_id: str, payment_method: str, screenshot_id: str) -> bool:
        def _query():
            try:
                _client.table("orders").update(
                    {"payment_method": payment_method, "screenshot_id": screenshot_id, "status": "pending"}
                ).eq("order_id", order_id).execute()
                return True
            except Exception as e:
                logger.error(f"update_order_payment error: {e}")
                return False
        return await _run(_query)

    @staticmethod
    async def approve_order(order_id: str) -> dict | None:
        def _query():
            try:
                # 1. Fetch order using standard list query
                res_f = _client.table("orders").select("*").eq("order_id", order_id).execute()
                if not res_f or not hasattr(res_f, 'data') or not res_f.data:
                    logger.warning(f"approve_order: Order {order_id} not found.")
                    return None
                
                order = res_f.data[0]
                
                # 2. Update status
                _client.table("orders").update({"status": "approved"}).eq("order_id", order_id).execute()
                order["status"] = "approved"

                # 3. Update user stats
                try:
                    uid = order.get("user_id")
                    if uid:
                        u_res = _client.table("users").select("*").eq("user_id", uid).execute()
                        if u_res and hasattr(u_res, 'data') and u_res.data:
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
                    logger.error(f"User stats update failed: {user_err}")
                
                return order
            except Exception as e:
                logger.error(f"approve_order CRITICAL error for {order_id}: {e}", exc_info=True)
                return None
        return await _run(_query)

    @staticmethod
    async def reject_order(order_id: str) -> dict | None:
        def _query():
            try:
                # 1. Fetch order
                res_f = _client.table("orders").select("*").eq("order_id", order_id).execute()
                if not res_f or not hasattr(res_f, 'data') or not res_f.data:
                    logger.warning(f"reject_order: Order {order_id} not found.")
                    return None
                
                order = res_f.data[0]
                
                # 2. Update status
                _client.table("orders").update({"status": "rejected"}).eq("order_id", order_id).execute()
                order["status"] = "rejected"

                # 3. Update user stats
                try:
                    uid = order.get("user_id")
                    if uid:
                        u_res = _client.table("users").select("rejected_payments").eq("user_id", uid).execute()
                        if u_res and hasattr(u_res, 'data') and u_res.data:
                            rejs = (u_res.data[0].get("rejected_payments") or 0) + 1
                            _client.table("users").update({"rejected_payments": rejs}).eq("user_id", uid).execute()
                except Exception as user_err:
                    logger.error(f"User stats update failed: {user_err}")
                
                return order
            except Exception as e:
                logger.error(f"reject_order CRITICAL error for {order_id}: {e}", exc_info=True)
                return None
        return await _run(_query)

    @staticmethod
    async def get_pending_orders(limit: int = 15) -> list:
        def _query():
            try:
                res = _client.table("orders").select("*").eq(
                    "status", "pending"
                ).order("created_at", desc=True).limit(limit).execute()
                return res.data or []
            except Exception as e:
                logger.error(f"get_pending_orders error: {e}")
                return []
        return await _run(_query)

    @staticmethod
    async def get_user_orders(user_id: int, limit: int = 50) -> list:
        def _query():
            try:
                res = _client.table("orders").select("*").eq(
                    "user_id", user_id
                ).order("created_at", desc=True).limit(limit).execute()
                return res.data or []
            except Exception as e:
                logger.error(f"get_user_orders error: {e}")
                return []
        return await _run(_query)

    @staticmethod
    async def get_all_orders(limit: int = 15) -> list:
        def _query():
            try:
                res = _client.table("orders").select("*").order(
                    "created_at", desc=True
                ).limit(limit).execute()
                return res.data or []
            except Exception as e:
                logger.error(f"get_all_orders error: {e}")
                return []
        return await _run(_query)

    @staticmethod
    async def get_order_by_id(order_id: str) -> dict | None:
        def _query():
            try:
                res = _client.table("orders").select("*").eq(
                    "order_id", order_id
                ).maybe_single().execute()
                return res.data
            except Exception as e:
                logger.error(f"get_order_by_id error: {e}")
                return None
        return await _run(_query)

    # ── Settings ───────────────────────────────────────────────────────────

    @staticmethod
    async def get_setting(key: str, default: str = "") -> str:
        def _query():
            try:
                res = _client.table("bot_settings").select("value").eq(
                    "key", key
                ).maybe_single().execute()
                return res.data["value"] if res.data else default
            except Exception as e:
                logger.error(f"get_setting({key}) error: {e}")
                return default
        return await _run(_query)

    @staticmethod
    async def set_setting(key: str, value: str) -> bool:
        def _query():
            try:
                _client.table("bot_settings").upsert(
                    {"key": key, "value": value}
                ).execute()
                return True
            except Exception as e:
                logger.error(f"set_setting({key}) error: {e}")
                return False
        return await _run(_query)

    # ── Stats ──────────────────────────────────────────────────────────────

    @staticmethod
    async def get_stats() -> dict:
        def _query():
            try:
                users_res = _client.table("users").select("user_id", count="exact").execute()
                orders_res = _client.table("orders").select(
                    "amount_usd,status", count="exact"
                ).execute()

                total_usd = 0.0
                successful = pending = rejected = 0
                for o in (orders_res.data or []):
                    total_usd += float(o.get("amount_usd") or 0)
                    s = o.get("status", "")
                    if s == "approved":
                        successful += 1
                    elif s == "pending":
                        pending += 1
                    elif s == "rejected":
                        rejected += 1

                return {
                    "total_users": users_res.count or 0,
                    "total_orders": orders_res.count or 0,
                    "total_usd": total_usd,
                    "successful": successful,
                    "pending": pending,
                    "rejected": rejected,
                }
            except Exception as e:
                logger.error(f"get_stats error: {e}")
                return {}
        return await _run(_query)

    @staticmethod
    async def get_users_list(offset: int = 0, limit: int = 10) -> list:
        def _query():
            try:
                res = _client.table("users").select("*").order("joined_at", desc=True).range(offset, offset + limit - 1).execute()
                return res.data or []
            except Exception as e:
                logger.error(f"get_users_list error: {e}")
                return []
        return await _run(_query)

    @staticmethod
    async def get_users_count() -> int:
        def _query():
            try:
                res = _client.table("users").select("user_id", count="exact").execute()
                return res.count or 0
            except Exception as e:
                logger.error(f"get_users_count error: {e}")
                return 0
        return await _run(_query)
