import numpy as np
from typing import List, Optional, Tuple
from moving_average import ma_calculator
import logging

logger = logging.getLogger(__name__)


class DemandForecaster:

    def forecast(self, values: List[float],
                 horizon: int = 7,
                 window: int = 7) -> dict:
        """
        Прогноз спроса на horizon дней вперёд.
        Метод: линейная регрессия по ряду SMA (формулы 10-13 диплома).
        """
        if len(values) < window:
            return {
                "forecast":  [],
                "mape":      None,
                "slope":     None,
                "intercept": None,
                "quality":   "недостаточно данных"
            }

        # Строим ряд SMA
        sma_series = ma_calculator.sma_series(values, window)
        valid_sma  = [(i, v) for i, v in enumerate(sma_series)
                      if v is not None]

        if len(valid_sma) < 3:
            return {"forecast": [], "mape": None,
                    "slope": None, "intercept": None,
                    "quality": "недостаточно данных"}

        times = np.array([t for t, _ in valid_sma], dtype=float)
        smas  = np.array([v for _, v in valid_sma], dtype=float)
        m     = len(times)

        # b = (m×Σtᵢ×SMAᵢ − Σtᵢ×ΣSMAᵢ) / (m×Σtᵢ² − (Σtᵢ)²)
        sum_t    = np.sum(times)
        sum_sma  = np.sum(smas)
        sum_t2   = np.sum(times ** 2)
        sum_tsma = np.sum(times * smas)

        denom = m * sum_t2 - sum_t ** 2
        if abs(denom) < 1e-10:
            b = 0.0
        else:
            b = (m * sum_tsma - sum_t * sum_sma) / denom

        # a = (ΣSMAᵢ − b×Σtᵢ) / m
        a = (sum_sma - b * sum_t) / m

        # Прогноз на horizon дней (формула 13)
        t0       = times[-1]
        forecast = []
        for tau in range(1, horizon + 1):
            y_pred = a + b * (t0 + tau)
            y_pred = max(0.0, y_pred)   # не может быть отрицательным
            forecast.append(round(y_pred, 2))

        # MAPE — формула 14 из диплома
        mape = self._calculate_mape(values[-m:], times, a, b)

        # Качество прогноза по MAPE
        if mape is None:
            quality = "неизвестно"
        elif mape < 10:
            quality = "высокая точность (MAPE < 10%)"
        elif mape < 20:
            quality = "приемлемая точность (MAPE < 20%)"
        else:
            quality = "низкая точность (MAPE > 20%)"

        return {
            "forecast":  forecast,
            "mape":      round(mape, 2) if mape else None,
            "slope":     round(float(b), 4),
            "intercept": round(float(a), 4),
            "quality":   quality
        }

    def _calculate_mape(self, actual: List[float],
                        times: np.ndarray,
                        a: float, b: float) -> Optional[float]:
        """
        MAPE = (100/m) × Σ|xᵢ − ŷᵢ| / xᵢ  (формула 14 диплома)
        """
        errors = []
        for i, t in enumerate(times):
            if i >= len(actual):
                break
            y_pred = a + b * t
            x_i    = actual[i]
            if x_i and x_i != 0:
                errors.append(abs(x_i - y_pred) / abs(x_i))

        if not errors:
            return None

        return 100 * sum(errors) / len(errors)


forecaster = DemandForecaster()