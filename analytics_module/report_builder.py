from typing import List
from models import AnalyticsReport
import logging

logger = logging.getLogger(__name__)


class ReportBuilder:

    def build_telegram_message(self,
                               reports: List[AnalyticsReport]) -> str:
        """Формирует текстовый отчёт для вывода в Telegram"""

        if not reports:
            return "❌ Нет данных для анализа"

        lines = []
        lines.append("📊 *АНАЛИТИЧЕСКИЙ ОТЧЁТ*")
        lines.append(f"Товаров проанализировано: {len(reports)}\n")

        for r in reports[:10]:   # Показываем топ-5 товаров
            lines.append(f"                  ")
            lines.append(f"📦 *{r.product_name}*")
            lines.append(f"Артикул: {r.article or 'не указан'}")

            # Скользящие средние
            if r.sma_7_sales is not None:
                lines.append(
                    f"📈 SMA-7 продаж: {r.sma_7_sales:.1f} шт/день"
                )
            if r.sma_30_sales is not None:
                lines.append(
                    f"📈 SMA-30 продаж: {r.sma_30_sales:.1f} шт/день"
                )

            # Тренд
            trend_emoji = {
                "рост": "⬆️", "падение": "⬇️", "стабильно": "➡️"
            }.get(r.trend_direction, "❓")
            lines.append(
                f"Тренд: {trend_emoji} {r.trend_direction}"
            )

            # Авито
            if r.sma_7_views is not None:
                lines.append(
                    f"👁 Просмотры (SMA-7): {r.sma_7_views:.0f}/день"
                )
            if r.sma_7_contacts is not None:
                lines.append(
                    f"📞 Отклики (SMA-7): {r.sma_7_contacts:.1f}/день"
                )

            # Прогноз
            if r.forecast_7_days:
                forecast_str = ", ".join(
                    [str(round(v)) for v in r.forecast_7_days]
                )
                lines.append(f"🔮 Прогноз продаж (7 дней): {forecast_str}")
                if r.mape:
                    lines.append(f"Точность прогноза: {r.mape:.1f}% MAPE")

            # Скоринг
            if r.card_score is not None:
                grade_emoji = {
                    "A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴"
                }.get(r.card_grade, "⚪")
                lines.append(
                    f"Эффективность карточки: "
                    f"{grade_emoji} {r.card_grade} ({r.card_score:.0f}/100)"
                )

            # Рекомендации
            if r.recommendations:
                lines.append("💡 Рекомендации:")
                for rec in r.recommendations[:2]:
                    lines.append(f"  • {rec}")

            # Цена
            if r.recommended_price and r.current_price:
                if r.recommended_price != r.current_price:
                    diff = r.recommended_price - r.current_price
                    sign = "+" if diff > 0 else ""
                    lines.append(
                        f"💰 Рекомендуемая цена: "
                        f"{r.recommended_price:.0f} ₽ "
                        f"({sign}{diff:.0f} ₽)"
                    )

        if len(reports) > 5:
            lines.append(f"\n...и ещё {len(reports) - 5} товаров")

        return "\n".join(lines)

    def build_summary(self, reports: List[AnalyticsReport]) -> dict:
        """Сводная статистика по всем товарам"""
        if not reports:
            return {}

        growing   = len([r for r in reports
                         if r.trend_direction == "рост"])
        declining = len([r for r in reports
                         if r.trend_direction == "падение"])
        stable    = len([r for r in reports
                         if r.trend_direction == "стабильно"])

        grades    = [r.card_grade for r in reports if r.card_grade]
        avg_score = (sum(r.card_score for r in reports
                         if r.card_score) / len(reports)
                     if reports else 0)

        return {
            "total":          len(reports),
            "trend_growing":  growing,
            "trend_declining": declining,
            "trend_stable":   stable,
            "avg_card_score": round(avg_score, 1),
            "grade_A":        grades.count("A"),
            "grade_B":        grades.count("B"),
            "grade_C":        grades.count("C"),
            "grade_D":        grades.count("D"),
        }


report_builder = ReportBuilder()