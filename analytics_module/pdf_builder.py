import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os


def register_fonts():
    font_paths = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\Arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont('Arial', path))
            return 'Arial'
    return 'Helvetica'


class PDFReportBuilder:

    def __init__(self):
        self.font = register_fonts()
        self.colors = {
            'primary': colors.HexColor('#2E75B6'),
            'success': colors.HexColor('#70AD47'),
            'warning': colors.HexColor('#FFC000'),
            'danger':  colors.HexColor('#FF0000'),
            'light':   colors.HexColor('#F2F2F2'),
            'dark':    colors.HexColor('#1F3864'),
            'text':    colors.HexColor('#404040'),
        }

    def _style(self, size=10, color=None, align='LEFT'):
        return ParagraphStyle(
            name='custom_' + str(size) + str(align),
            fontName=self.font,
            fontSize=size,
            textColor=color or self.colors['text'],
            alignment={'LEFT': 0, 'CENTER': 1, 'RIGHT': 2}[align],
            leading=size * 1.4,
            spaceAfter=4
        )

    def _make_sales_chart(self, sales, sma7, forecast, name):
        fig, ax = plt.subplots(figsize=(14, 4))
        fig.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#FAFAFA')

        x_sales = list(range(len(sales)))
        x_fore  = list(range(len(sales), len(sales) + len(forecast)))

        ax.bar(x_sales, sales, color='#BDD7EE',
               alpha=0.7, label='Продажи факт', width=0.8)

        if sma7:
            sma_full = [None] * 6 + list(sma7)
            ax.plot(x_sales, sma_full[:len(x_sales)],
                    color='#2E75B6', linewidth=2.5,
                    label='SMA-7', zorder=5)

        if forecast:
            ax.plot(x_fore, forecast, color='#70AD47', linewidth=2.5,
                    linestyle='--', marker='o', markersize=4,
                    label='Прогноз 7 дней', zorder=5)
            ax.fill_between(x_fore, 0, forecast,
                            color='#70AD47', alpha=0.1)
            ax.axvline(x=len(sales) - 0.5,
                       color='#404040', linestyle=':', alpha=0.5)

        ax.set_title(f'Продажи: {name[:50]}', fontsize=11,
                     pad=10, color='#1F3864')
        ax.set_xlabel('Дни', fontsize=9)
        ax.set_ylabel('Кол-во, шт.', fontsize=9)
        ax.legend(fontsize=8, loc='upper left')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def _make_avito_chart(self, views, favorites, contacts, name):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 5))
        fig.patch.set_facecolor('#FAFAFA')

        x = list(range(len(views)))

        ax1.fill_between(x, views, color='#BDD7EE', alpha=0.4)
        ax1.plot(x, views, color='#2E75B6',
                 linewidth=2, label='Просмотры')
        ax1.set_title('Активность на Авито', fontsize=10,
                      color='#1F3864')
        ax1.set_ylabel('Просмотры', fontsize=8)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        ax2.plot(x, favorites, color='#FFC000',
                 linewidth=2, label='Избранное', marker='.')
        ax2.plot(x, contacts, color='#70AD47',
                 linewidth=2, label='Отклики', marker='.')
        ax2.set_ylabel('Кол-во', fontsize=8)
        ax2.set_xlabel('Дни', fontsize=8)
        ax2.legend(fontsize=8, loc='upper left')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def _make_summary_chart(self, reports):
        if not reports:
            return None

        sorted_r = sorted(
            [r for r in reports if r.sma_7_sales],
            key=lambda x: x.sma_7_sales,
            reverse=True
        )[:10]

        if not sorted_r:
            return None

        names  = [r.product_name[:25] + '...'
                  if len(r.product_name) > 25
                  else r.product_name
                  for r in sorted_r]
        values = [r.sma_7_sales for r in sorted_r]
        grades = [r.card_grade  for r in sorted_r]

        color_map = {
            'A': '#70AD47', 'B': '#FFC000',
            'C': '#FF7F00', 'D': '#FF0000'
        }
        bar_colors = [color_map.get(g, '#BDD7EE') for g in grades]

        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#FAFAFA')

        bars = ax.barh(names, values, color=bar_colors,
                       edgecolor='white', linewidth=0.5)

        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 0.05,
                    bar.get_y() + bar.get_height() / 2,
                    f'{val:.1f}', va='center', fontsize=8)

        ax.set_title('ТОП товаров по продажам (SMA-7)',
                     fontsize=12, color='#1F3864', pad=10)
        ax.set_xlabel('Продажи в день (шт.)', fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--', axis='x')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        patches = [mpatches.Patch(color=c, label=f'Оценка {g}')
                   for g, c in color_map.items()]
        ax.legend(handles=patches, fontsize=8, loc='lower right')

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    def _tbl_style(self):
        return TableStyle([
            ('BACKGROUND',     (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR',      (0, 0), (-1, 0), colors.white),
            ('FONTNAME',       (0, 0), (-1, -1), self.font),
            ('FONTSIZE',       (0, 0), (-1, -1), 9),
            ('ALIGN',          (1, 1), (1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [self.colors['light'], colors.white]),
            ('GRID',           (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('TOPPADDING',     (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING',  (0, 0), (-1, -1), 5),
        ])

    def build_pdf(self, reports, sales_histories=None,
                  avito_histories=None) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )
        story = []

        story.append(Spacer(1, 2 * cm))
        story.append(Paragraph(
            'АНАЛИТИЧЕСКИЙ ОТЧЁТ',
            self._style(22, color=self.colors['dark'], align='CENTER')
        ))
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(
            'AutoMarket Integration System',
            self._style(14, color=self.colors['primary'], align='CENTER')
        ))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(
            f"Дата формирования: "
            f"{datetime.now().strftime('%d.%m.%Y %H:%M')}",
            self._style(10, align='CENTER')
        ))
        story.append(Spacer(1, 1 * cm))

        story.append(Paragraph(
            'СВОДНЫЕ ПОКАЗАТЕЛИ',
            self._style(13, color=self.colors['dark'])
        ))
        story.append(Spacer(1, 0.3 * cm))

        total     = len(reports)
        grade_a   = sum(1 for r in reports if r.card_grade == 'A')
        grade_b   = sum(1 for r in reports if r.card_grade == 'B')
        grade_cd  = total - grade_a - grade_b
        avg_score = (sum(r.card_score for r in reports if r.card_score)
                     / total if total else 0)
        trend_up  = sum(1 for r in reports if r.trend_direction == 'рост')
        trend_dn  = sum(1 for r in reports if r.trend_direction == 'падение')

        summary_data = [
            ['Показатель',                    'Значение'],
            ['Товаров проанализировано',       str(total)],
            ['Средний балл карточки',          f'{avg_score:.0f}/100'],
            ['Оценка A (отлично)',             str(grade_a)],
            ['Оценка B (хорошо)',              str(grade_b)],
            ['Оценка C/D (требует внимания)',  str(grade_cd)],
            ['Товаров с растущим трендом',    str(trend_up)],
            ['Товаров с падающим трендом',    str(trend_dn)],
        ]

        tbl = Table(summary_data, colWidths=[10 * cm, 6 * cm])
        tbl.setStyle(self._tbl_style())
        story.append(tbl)
        story.append(Spacer(1, 1 * cm))

        summary_chart = self._make_summary_chart(reports)
        if summary_chart:
            story.append(Paragraph(
                'ТОП ТОВАРОВ ПО ПРОДАЖАМ',
                self._style(12, color=self.colors['dark'])
            ))
            story.append(Spacer(1, 0.3 * cm))
            story.append(Image(summary_chart,
                               width=17 * cm, height=6 * cm))

        story.append(PageBreak())

        trend_labels = {
            'рост':      'Рост',
            'падение':   'Падение',
            'стабильно': 'Стабильно',
        }
        grade_label = {
            'A': 'A - Отлично',
            'B': 'B - Хорошо',
            'C': 'C - Требует улучшений',
            'D': 'D - Низкая эффективность',
        }

        for i, report in enumerate(reports):
            pid = report.product_id

            story.append(Paragraph(
                f'{i + 1}. {report.product_name}',
                self._style(13, color=self.colors['dark'])
            ))
            if report.article:
                story.append(Paragraph(
                    f'Артикул: {report.article}',
                    self._style(9, color=colors.grey)
                ))
            story.append(Spacer(1, 0.3 * cm))

            story.append(Paragraph(
                f'Оценка карточки: '
                f'{grade_label.get(report.card_grade, "-")} '
                f'({report.card_score:.0f}/100 баллов)',
                self._style(11)
            ))
            story.append(Spacer(1, 0.3 * cm))

            metrics = [
                ['Показатель',             'Значение'],
                ['SMA-7 продажи',
                 f'{report.sma_7_sales:.1f} шт/день'
                 if report.sma_7_sales else '-'],
                ['SMA-30 продажи',
                 f'{report.sma_30_sales:.1f} шт/день'
                 if report.sma_30_sales else '-'],
                ['EMA-7 продажи',
                 f'{report.ema_sales:.1f} шт/день'
                 if report.ema_sales else '-'],
                ['Тренд продаж',
                 trend_labels.get(report.trend_direction, '-')],
                ['SMA-7 просмотры',
                 f'{report.sma_7_views:.0f}/день'
                 if report.sma_7_views else '-'],
                ['SMA-7 избранное',
                 f'{report.sma_7_favorites:.1f}/день'
                 if report.sma_7_favorites else '-'],
                ['SMA-7 отклики',
                 f'{report.sma_7_contacts:.1f}/день'
                 if report.sma_7_contacts else '-'],
                ['Текущая цена',
                 f'{report.current_price:,.0f} руб.'
                 if report.current_price else '-'],
                ['Рекомендуемая цена',
                 f'{report.recommended_price:,.0f} руб.'
                 if report.recommended_price else '-'],
                ['Точность прогноза (MAPE)',
                 f'{report.mape:.1f}%'
                 if report.mape else '-'],
            ]

            mt = Table(metrics, colWidths=[9 * cm, 8 * cm])
            mt.setStyle(self._tbl_style())
            story.append(mt)
            story.append(Spacer(1, 0.4 * cm))

            if report.forecast_7_days:
                fc_str = ', '.join(
                    str(int(v)) for v in report.forecast_7_days
                )
                story.append(Paragraph(
                    f'Прогноз продаж на 7 дней: {fc_str} шт.',
                    self._style(9, color=self.colors['primary'])
                ))
                story.append(Spacer(1, 0.2 * cm))

            if report.recommendations:
                story.append(Paragraph(
                    'Рекомендации:', self._style(9)
                ))
                for rec in report.recommendations:
                    story.append(Paragraph(
                        f'- {rec}', self._style(9)
                    ))
                story.append(Spacer(1, 0.3 * cm))

            sales_h = (sales_histories or {}).get(pid, [])
            avito_h = (avito_histories or {}).get(pid, {})

            if sales_h:
                sma7_list = [
                    sum(sales_h[j - 6:j + 1]) / 7
                    for j in range(6, len(sales_h))
                ]
                fc    = list(report.forecast_7_days or [])
                chart = self._make_sales_chart(
                    sales_h, sma7_list, fc, report.product_name
                )
                story.append(Image(chart,
                                   width=17 * cm, height=4.5 * cm))
                story.append(Spacer(1, 0.3 * cm))

            if avito_h and avito_h.get('views'):
                ac = self._make_avito_chart(
                    avito_h.get('views', []),
                    avito_h.get('favorites', []),
                    avito_h.get('contacts', []),
                    report.product_name
                )
                story.append(Image(ac,
                                   width=17 * cm, height=5 * cm))

            if i < len(reports) - 1:
                story.append(PageBreak())

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()


pdf_builder = PDFReportBuilder()