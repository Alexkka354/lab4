from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Base(DeclarativeBase):
    pass


# Таблица статистики продаж из 1С
class SalesStat(Base):
    __tablename__ = "sales_stats"

    id         = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False)
    article    = Column(String(100))
    sales_qty  = Column(Integer, default=0)   # количество продаж за день
    revenue    = Column(Float, default=0.0)   # выручка за день
    stat_date  = Column(DateTime, default=func.now())


# Таблица статистики с Авито
class AvitoStat(Base):
    __tablename__ = "avito_stats"

    id          = Column(Integer, primary_key=True)
    product_id  = Column(Integer, nullable=False)
    article     = Column(String(100))
    views       = Column(Integer, default=0)    # просмотры
    favorites   = Column(Integer, default=0)    # добавления в избранное
    contacts    = Column(Integer, default=0)    # отклики/контакты
    stat_date   = Column(DateTime, default=func.now())


# Pydantic схемы для API
class AnalyticsReport(BaseModel):
    product_id:        int
    product_name:      str
    article:           Optional[str]

    # Скользящие средние продаж
    sma_7_sales:       Optional[float]   # 7-дневная SMA продаж
    sma_30_sales:      Optional[float]   # 30-дневная SMA продаж
    ema_sales:         Optional[float]   # EMA продаж

    # Скользящие средние Авито
    sma_7_views:       Optional[float]   # 7-дневная SMA просмотров
    sma_7_favorites:   Optional[float]   # 7-дневная SMA избранного
    sma_7_contacts:    Optional[float]   # 7-дневная SMA откликов

    # Тренд
    trend_direction:   str               # "рост", "падение", "стабильно"
    trend_slope:       Optional[float]   # наклон тренда

    # Прогноз на 7 дней
    forecast_7_days:   List[float]
    mape:              Optional[float]   # точность прогноза %

    # Скоринг карточки
    card_score:        Optional[float]   # 0-100
    card_grade:        Optional[str]     # A, B, C, D
    recommendations:   List[str]

    # Оптимальная цена
    recommended_price: Optional[float]
    current_price:     Optional[float]


class BulkAnalyticsReport(BaseModel):
    generated_at:   str
    total_products: int
    reports:        List[AnalyticsReport]
    summary:        dict