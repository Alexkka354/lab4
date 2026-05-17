from typing import List
import logging

logger = logging.getLogger(__name__)


class CardScorer:

    def score(self, views: float, favorites: float,
              contacts: float, sales: float,
              price: float) -> dict:
        """
        Скоринг эффективности карточки товара (0-100 баллов).
        Оценивает: конверсию просмотров, активность, продажи.
        """
        score = 0.0
        recommendations = []

        # 1. Конверсия просмотров в отклики (0-30 баллов)
        if views > 0:
            ctr = contacts / views * 100
            if ctr >= 5:
                score += 30
            elif ctr >= 2:
                score += 20
            elif ctr >= 0.5:
                score += 10
            else:
                score += 0
                recommendations.append(
                    "Низкая конверсия просмотров — улучшите описание и фото"
                )
        else:
            recommendations.append(
                "Нет просмотров — проверьте публикацию объявления"
            )

        # 2. Добавления в избранное (0-25 баллов)
        if views > 0:
            fav_rate = favorites / views * 100
            if fav_rate >= 3:
                score += 25
            elif fav_rate >= 1:
                score += 15
            elif fav_rate >= 0.3:
                score += 8
            else:
                score += 0
                recommendations.append(
                    "Мало добавлений в избранное — цена может быть завышена"
                )

        # 3. Продажи (0-30 баллов)
        if sales >= 10:
            score += 30
        elif sales >= 5:
            score += 20
        elif sales >= 1:
            score += 10
        else:
            score += 0
            recommendations.append(
                "Нет продаж — проверьте цену и описание товара"
            )

        # 4. Соотношение откликов к просмотрам (0-15 баллов)
        if views > 0 and contacts > 0:
            ratio = contacts / views
            if ratio >= 0.1:
                score += 15
            elif ratio >= 0.05:
                score += 10
            else:
                score += 5

        # Определяем оценку
        if score >= 80:
            grade = "A"
            grade_text = "Отличная карточка"
        elif score >= 60:
            grade = "B"
            grade_text = "Хорошая карточка"
        elif score >= 40:
            grade = "C"
            grade_text = "Требует улучшений"
        else:
            grade = "D"
            grade_text = "Низкая эффективность"

        if not recommendations:
            recommendations.append("Карточка товара в хорошем состоянии")

        return {
            "score":           round(score, 1),
            "grade":           grade,
            "grade_text":      grade_text,
            "recommendations": recommendations
        }


card_scorer = CardScorer()