from aiogram import Router
from aiogram.types import CallbackQuery, Message, BufferedInputFile
import aiohttp
import logging
from datetime import datetime

router = Router()
logger = logging.getLogger(__name__)

ANALYTICS_URL = "http://localhost:8004"


async def fetch_analytics_pdf() -> bytes | None:
    """Получает PDF из аналитического модуля"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ANALYTICS_URL}/api/v1/analytics/report/pdf",
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status == 200:
                    return await resp.read()
                else:
                    logger.error(
                        f"Аналитика вернула статус {resp.status}"
                    )
                    return None
    except aiohttp.ClientConnectorError:
        logger.error("Аналитический модуль не запущен (порт 8004)")
        return None
    except Exception as e:
        logger.error(f"Ошибка получения PDF: {e}")
        return None


async def send_analytics(message: Message):
    """Общая функция — формирует и отправляет PDF в чат"""
    await message.answer(
        "⏳ Формирую аналитический отчёт...\n"
        "Это займёт несколько секунд."
    )

    pdf_bytes = await fetch_analytics_pdf()

    if pdf_bytes is None:
        await message.answer(
            "⚠️ Не удалось получить отчёт.\n\n"
            "Проверьте что аналитический модуль запущен:\n"
            "cd analytics_module\n"
            "uvicorn main:app --port 8004 --reload"
        )
        return

    filename = (
        f"analytics_"
        f"{datetime.now().strftime('%d%m%Y_%H%M')}.pdf"
    )

    pdf_file = BufferedInputFile(pdf_bytes, filename=filename)

    await message.answer_document(
        document=pdf_file,
        caption=(
            f"📊 *Аналитический отчёт*\n"
            f"🗓 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            f"В отчёте:\n"
            f"📈 Графики продаж с прогнозом\n"
            f"👁 Статистика просмотров Авито\n"
            f"🎯 Скоринг карточек товаров\n"
            f"💰 Рекомендации по ценам"
        ),
        parse_mode="Markdown"
    )


@router.callback_query(lambda c: c.data == "analytics")
async def show_analytics_callback(callback: CallbackQuery):
    await callback.answer()
    await send_analytics(callback.message)


@router.message(lambda m: m.text == "📊 Аналитика")
async def show_analytics_message(message: Message):
    await send_analytics(message)