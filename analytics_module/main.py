import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import Response
from dotenv import load_dotenv

from models import AnalyticsReport, BulkAnalyticsReport
from stats_collector import stats_collector
from moving_average import ma_calculator
from forecaster import forecaster
from scorer import card_scorer
from price_optimizer import price_optimizer
from report_builder import report_builder
from pdf_builder import pdf_builder

load_dotenv(dotenv_path=Path(__file__).parent / ".env")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Analytics Module", lifespan=lifespan)


async def analyze_product(product: dict) -> AnalyticsReport:
    """Полный анализ одного товара"""
    product_id = product["id"]

    sales_h = await stats_collector.get_sales_history(product_id, 30)
    avito_h = await stats_collector.get_avito_stats_history(product_id, 30)

    views_h = avito_h["views"]
    fav_h   = avito_h["favorites"]
    cont_h  = avito_h["contacts"]

    sma_7_s  = ma_calculator.sma(sales_h, 7)
    sma_30_s = ma_calculator.sma(sales_h, 30)
    ema_s    = ma_calculator.ema(sales_h, 7)

    sma_7_v  = ma_calculator.sma(views_h, 7)
    sma_7_f  = ma_calculator.sma(fav_h, 7)
    sma_7_c  = ma_calculator.sma(cont_h, 7)

    trend    = ma_calculator.detect_trend(sales_h, window=7)
    forecast = forecaster.forecast(sales_h, horizon=7, window=7)

    score    = card_scorer.score(
        views=sma_7_v or 0,
        favorites=sma_7_f or 0,
        contacts=sma_7_c or 0,
        sales=sma_7_s or 0,
        price=float(product.get("price", 0))
    )

    price_rec = price_optimizer.optimize(
        current_price=float(product.get("price", 0)),
        sales_history=sales_h,
        views_history=views_h,
        favorites_history=fav_h
    )

    return AnalyticsReport(
        product_id=product_id,
        product_name=product["name"],
        article=product.get("article"),
        sma_7_sales=round(sma_7_s, 2) if sma_7_s else None,
        sma_30_sales=round(sma_30_s, 2) if sma_30_s else None,
        ema_sales=round(ema_s, 2) if ema_s else None,
        sma_7_views=round(sma_7_v, 1) if sma_7_v else None,
        sma_7_favorites=round(sma_7_f, 1) if sma_7_f else None,
        sma_7_contacts=round(sma_7_c, 1) if sma_7_c else None,
        trend_direction=trend["direction"],
        trend_slope=trend["slope"],
        forecast_7_days=forecast["forecast"],
        mape=forecast["mape"],
        card_score=score["score"],
        card_grade=score["grade"],
        recommendations=score["recommendations"],
        recommended_price=price_rec["recommended_price"],
        current_price=price_rec["current_price"]
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "analytics_module"}


@app.get("/api/v1/analytics/report")
async def full_report():
    products = await stats_collector.get_all_products()
    reports  = []

    for product in products:
        try:
            report = await analyze_product(product)
            reports.append(report)
        except Exception as e:
            logger.error(f"Ошибка анализа {product['name']}: {e}")

    summary = report_builder.build_summary(reports)

    return BulkAnalyticsReport(
        generated_at=datetime.now().strftime("%d.%m.%Y %H:%M"),
        total_products=len(reports),
        reports=reports,
        summary=summary
    )


@app.get("/api/v1/analytics/telegram")
async def telegram_report():
    products = await stats_collector.get_all_products()
    reports  = []

    for product in products:
        try:
            report = await analyze_product(product)
            reports.append(report)
        except Exception as e:
            logger.error(f"Ошибка анализа {product['name']}: {e}")

    return {"text": report_builder.build_telegram_message(reports)}


# ВАЖНО: маршрут /report/pdf должен быть ДО /{product_id}
# иначе FastAPI воспринимает "pdf" как product_id
@app.get("/api/v1/analytics/report/pdf")
async def analytics_pdf():
    """PDF-отчёт с графиками — отправляется в Telegram"""
    products        = await stats_collector.get_all_products()
    reports         = []
    sales_histories = {}
    avito_histories = {}

    for product in products:
        try:
            pid     = product["id"]
            sales_h = await stats_collector.get_sales_history(pid, 30)
            avito_h = await stats_collector.get_avito_stats_history(pid, 30)

            sales_histories[pid] = sales_h
            avito_histories[pid] = avito_h

            report = await analyze_product(product)
            reports.append(report)
        except Exception as e:
            logger.error(f"Ошибка {product['name']}: {e}")

    pdf_bytes = pdf_builder.build_pdf(
        reports, sales_histories, avito_histories
    )

    filename = f"analytics_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@app.get("/api/v1/analytics/{product_id}")
async def analyze_one(product_id: int):
    products = await stats_collector.get_all_products()
    product  = next(
        (p for p in products if p["id"] == product_id), None
    )
    if not product:
        return {"error": "Товар не найден"}
    return await analyze_product(product)