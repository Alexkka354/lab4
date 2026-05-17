from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class MovingAverageCalculator:

    def sma(self, values: List[float], window: int) -> Optional[float]:
        if not values:
            return None
        if len(values) < window:
            return sum(values) / len(values)
        last_k = values[-window:]
        return sum(last_k) / window

    def wma(self, values: List[float], window: int) -> Optional[float]:
        if not values:
            return None
        if len(values) < window:
            window = len(values)
        last_k  = values[-window:]
        weights = list(range(1, window + 1))
        weighted_sum = sum(w * x for w, x in zip(weights, last_k))
        return weighted_sum / sum(weights)

    def ema(self, values: List[float], window: int) -> Optional[float]:
        if not values:
            return None
        alpha   = 2 / (window + 1)
        ema_val = values[0]
        for x in values[1:]:
            ema_val = alpha * x + (1 - alpha) * ema_val
        return ema_val

    def sma_series(self, values: List[float],
                   window: int) -> List[Optional[float]]:
        result = []
        for i in range(len(values)):
            if i < window - 1:
                result.append(None)
            else:
                result.append(
                    self.sma(values[i - window + 1:i + 1], window)
                )
        return result

    def detect_trend(self, values: List[float],
                     window: int = 7) -> dict:
        if len(values) < window * 2:
            return {"direction": "недостаточно данных", "slope": 0.0}

        sma_s = self.sma_series(values, window)
        valid = [v for v in sma_s if v is not None]

        if len(valid) < 4:
            return {"direction": "недостаточно данных", "slope": 0.0}

        half     = len(valid) // 2
        first_h  = sum(valid[:half]) / half
        second_h = sum(valid[half:]) / (len(valid) - half)
        slope    = second_h - first_h
        pct      = (slope / first_h * 100) if first_h > 0 else 0

        if pct > 5:
            direction = "рост"
        elif pct < -5:
            direction = "падение"
        else:
            direction = "стабильно"

        return {"direction": direction, "slope": round(slope, 4)}


ma_calculator = MovingAverageCalculator()