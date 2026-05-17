import aiohttp
import os
import logging

logger = logging.getLogger(__name__)

class IntegrationPublisher:
    def __init__(self):
        self.url = os.getenv(
            "INTEGRATION_MODULE_URL",
            "http://localhost:8000"
        )

    async def send_products(self, products: list) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.url}/api/v1/products/sync",
                json=products
            ) as resp:
                resp.raise_for_status()
                return await resp.json()