import asyncpg
import os
import logging
from typing import List
from datetime import datetime

logger = logging.getLogger(__name__)


class StatsCollector:

    async def _get_conn(self):
        return await asyncpg.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "automarket"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "1234")
        )

    async def get_all_products(self) -> List[dict]:
        conn = await self._get_conn()
        try:
            rows = await conn.fetch("""
                SELECT id, name, article, price, stock, category
                FROM products
                WHERE status = 'active'
                ORDER BY id
            """)
            return [dict(r) for r in rows]
        finally:
            await conn.close()

    async def get_sales_history(self, product_id: int,
                                days: int = 30) -> List[float]:
        conn = await self._get_conn()
        try:
            # Исправленный SQL — INTERVAL не принимает параметры напрямую
            rows = await conn.fetch(f"""
                SELECT sales_qty
                FROM sales_stats
                WHERE product_id = $1
                  AND stat_date >= NOW() - INTERVAL '{days} days'
                ORDER BY stat_date ASC
            """, product_id)

            if rows:
                return [float(r["sales_qty"]) for r in rows]

            # Если нет данных — генерируем тестовые
            import random
            return [float(random.randint(0, 10)) for _ in range(days)]
        finally:
            await conn.close()

    async def get_avito_stats_history(self, product_id: int,
                                      days: int = 30) -> dict:
        conn = await self._get_conn()
        try:
            rows = await conn.fetch(f"""
                SELECT views, favorites, contacts
                FROM avito_stats
                WHERE product_id = $1
                  AND stat_date >= NOW() - INTERVAL '{days} days'
                ORDER BY stat_date ASC
            """, product_id)

            if rows:
                return {
                    "views":     [float(r["views"]) for r in rows],
                    "favorites": [float(r["favorites"]) for r in rows],
                    "contacts":  [float(r["contacts"]) for r in rows],
                }

            # Тестовые данные если таблица пустая
            import random
            return {
                "views":     [float(random.randint(5, 100)) for _ in range(days)],
                "favorites": [float(random.randint(0, 10)) for _ in range(days)],
                "contacts":  [float(random.randint(0, 5)) for _ in range(days)],
            }
        finally:
            await conn.close()


stats_collector = StatsCollector()