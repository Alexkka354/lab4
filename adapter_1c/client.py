import subprocess
import json
import os
import time
import logging

logger = logging.getLogger(__name__)

class OneCClient:
    def __init__(self):
        self.onec_path   = os.getenv(
            "ONEC_PATH",
            r"C:\Program Files (x86)\1cv8t\8.3.27.1508\bin\1cv8t.exe"
        )
        self.base_path   = os.getenv("ONEC_BASE_PATH")
        self.login       = os.getenv("ONEC_LOGIN", "")
        self.password    = os.getenv("ONEC_PASSWORD", "")
        self.export_path = os.getenv(
            "ONEC_EXPORT_PATH",
            r"C:\Users\bojce\Desktop\products.json"
        )
        self.epf_path    = os.getenv(
            "ONEC_EPF_PATH",
            r"C:\Users\bojce\Desktop\Telegramm_bot\adapter_1c\ExportProducts.epf"
        )

    def fetch_products(self) -> list:
        if os.path.exists(self.export_path):
            os.remove(self.export_path)

        subprocess.Popen([
            self.onec_path,
            "ENTERPRISE",
            "/F", self.base_path,
            "/N", self.login,
            "/P", self.password,
            "/Execute", self.epf_path,
        ])

        logger.info("Ожидаем выгрузку из 1С...")
        timeout = 300
        elapsed = 0
        while elapsed < timeout:
            time.sleep(3)
            elapsed += 3
            if os.path.exists(self.export_path):
                if os.path.getsize(self.export_path) > 10:
                    time.sleep(2)
                    break
            logger.info(f"Ждём файл... {elapsed} сек")

        if not os.path.exists(self.export_path):
            raise Exception("Файл не создан — нажмите кнопку в 1С")

        with open(self.export_path, "r", encoding="utf-8") as f:
            products = json.load(f)

        os.remove(self.export_path)
        logger.info(f"Получено товаров: {len(products)}")
        return products