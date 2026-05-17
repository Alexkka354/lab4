from typing import List, Optional
from moving_average import ma_calculator
import logging

logger = logging.getLogger(__name__)


class PriceOptimizer:

    def optimize(self, current_price: float,
                 sales_history: List[float],
                 views_history: List[float],
                 favorites_history: List[float]) -> dict:
        """
        Анализирует эластичность спроса и рекомендует оптимальную цену.
        """
        if not sales_history or not views_history:
            return {
                "recommended_price": current_price,
                "reason": "Недостаточно данных для анализа",
                "change_pct": 0.0
            }

        # Тренд продаж
        sales_trend  = ma_calculator.detect_trend(sales_history)
        views_trend  = ma_calculator.detect_trend(views_history)
        fav_trend    = ma_calculator.detect_trend(favorites_history) \
                       if favorites_history else {"direction": "стабильно"}

        # Средние показатели
        avg_sales    = sum(sales_history[-7:]) / min(7, len(sales_history))
        avg_views    = sum(views_history[-7:]) / min(7, len(views_history))

        # Конверсия просмотров в продажи
        conversion   = avg_sales / avg_views if avg_views > 0 else 0

        # Логика рекомендации цены
        change_pct   = 0.0
        reason       = ""

        if (sales_trend["direction"] == "рост" and
                views_trend["direction"] == "рост"):
            # Спрос растёт — можно поднять цену на 5%
            change_pct = 5.0
            reason     = "Высокий спрос — рекомендуем повысить цену"

        elif (sales_trend["direction"] == "падение" and
              views_trend["direction"] == "падение"):
            # Спрос падает — снизить цену на 5-10%
            change_pct = -7.0
            reason     = "Падение спроса — рекомендуем снизить цену"

        elif (views_trend["direction"] == "рост" and
              sales_trend["direction"] == "падение"):
            # Просмотры есть, но не покупают — цена завышена
            change_pct = -5.0
            reason     = "Низкая конверсия — цена может быть завышена"

        elif conversion > 0.1:
            # Высокая конверсия — можно поднять цену
            change_pct = 3.0
            reason     = "Высокая конверсия — есть потенциал повышения цены"

        else:
            reason = "Цена оптимальна — изменения не требуются"

        recommended_price = round(
            current_price * (1 + change_pct / 100), 2
        )

        return {
            "current_price":     current_price,
            "recommended_price": recommended_price,
            "change_pct":        change_pct,
            "reason":            reason,
            "sales_trend":       sales_trend["direction"],
            "views_trend":       views_trend["direction"]
        }


price_optimizer = PriceOptimizer()