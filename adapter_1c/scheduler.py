import asyncio
import logging
import os
from client import OneCClient
from publisher import IntegrationPublisher

logger = logging.getLogger(__name__)
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", 300))

async def sync_loop():
    while True:
        try:
            logger.info("Плановая синхронизация с 1С...")
            client    = OneCClient()
            publisher = IntegrationPublisher()
            loop      = asyncio.get_event_loop()
            products  = await loop.run_in_executor(
                None, client.fetch_products
            )
            result = await publisher.send_products(products)
            logger.info(f"Синхронизировано: {result}")
        except Exception as e:
            logger.error(f"Ошибка: {e}")
        await asyncio.sleep(POLL_INTERVAL)