"""
Script para generar la presentación PDF de Clinical Copilot NLP.

Uso:
    uv run python slides/create_slides.py

Genera: slides/clinical_copilot_nlp_slides.pdf
"""

import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ---------------------------------------------------------------------------
# Registro de fuentes TTF con soporte Unicode (tildes, ñ, ¿, ¡)
# ---------------------------------------------------------------------------
_FONT_PATHS = [
    ("Arial", r"C:\Windows\Fonts\arial.ttf"),
    ("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"),
    ("Arial-Italic", r"C:\Windows\Fonts\ariali.ttf"),
]

for _font_name, _font_path in _FONT_PATHS:
    if os.path.exists(_font_path):
        pdfmetrics.registerFont(TTFont(_font_name, _font_path))

# Determinar qué familia de fuentes usar según disponibilidad
try:
    pdfmetrics.getFont("Arial")
    FONT_REGULAR = "Arial"
    FONT_BOLD = "Arial-Bold"
    FONT_ITALIC = "Arial-Italic"
except KeyError:
    # Fallback a Helvetica si Arial no está disponible
    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    FONT_ITALIC = "Helvetica-Oblique"


# ---------------------------------------------------------------------------
# Configuración de página — A4 Landscape
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = A4[1], A4[0]  # swap for landscape: 841.9 x 595.3 pt

# ---------------------------------------------------------------------------
# Paleta de colores
# ---------------------------------------------------------------------------
C_DARK_BLUE = colors.HexColor("#0D2B55")  # Header backgrounds
C_MID_BLUE = colors.HexColor("#1A4A8A")  # Accent lines / sub-headers
C_LIGHT_BLUE = colors.HexColor("#D6E4F7")  # Light fill for boxes
C_ACCENT = colors.HexColor("#2196F3")  # Flow-diagram accents
C_WHITE = colors.white
C_TEXT = colors.HexColor("#1A1A2E")  # Body text
C_SUBTLE = colors.HexColor("#6B7C93")  # Captions / page numbers

C_CRITICAL = colors.HexColor("#D32F2F")  # CRÍTICO — deep red
C_HIGH = colors.HexColor("#E64A19")  # ALTO — deep orange
C_SEVERE = colors.HexColor("#8B0000")  # SEVERO — dark red

C_IMPLEMENTED = colors.HexColor("#1B5E20")  # implemented badge
C_FUTURE = colors.HexColor("#4A4A4A")  # future badge


# ---------------------------------------------------------------------------
# Helper: dibujar el fondo de header con rectángulo sólido
# ---------------------------------------------------------------------------
def draw_header(c: canvas.Canvas, title: str, subtitle: str | None = None) -> float:
    """Dibuja el encabezado oscuro y devuelve la Y donde termina el header."""
    header_h = 3.8 * cm if subtitle else 2.8 * cm
    top_y = PAGE_H
    header_y = top_y - header_h

    # Rectángulo de fondo
    c.setFillColor(C_DARK_BLUE)
    c.rect(0, header_y, PAGE_W, header_h, fill=1, stroke=0)

    # Línea inferior del header
    c.setStrokeColor(C_ACCENT)
    c.setLineWidth(3)
    c.line(0, header_y, PAGE_W, header_y)

    # Título
    title_y = top_y - 1.4 * cm if subtitle else top_y - 1.6 * cm
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 24)
    c.drawString(1.5 * cm, title_y, title)

    if subtitle:
        c.setFont(FONT_ITALIC, 13)
        c.setFillColor(colors.HexColor("#90CAF9"))
        c.drawString(1.5 * cm, title_y - 0.8 * cm, subtitle)

    return header_y  # Y inferior del header (punto de inicio del cuerpo)


# ---------------------------------------------------------------------------
# Helper: número de página
# ---------------------------------------------------------------------------
def draw_page_number(c: canvas.Canvas, page_num: int, total: int) -> None:
    c.setFont(FONT_REGULAR, 9)
    c.setFillColor(C_SUBTLE)
    label = f"{page_num} / {total}"
    c.drawRightString(PAGE_W - 1 * cm, 0.6 * cm, label)

    # Línea footer
    c.setStrokeColor(C_LIGHT_BLUE)
    c.setLineWidth(0.5)
    c.line(1 * cm, 1.1 * cm, PAGE_W - 1 * cm, 1.1 * cm)

    # Branding footer
    c.setFont(FONT_REGULAR, 8)
    c.setFillColor(C_SUBTLE)
    c.drawString(
        1 * cm, 0.6 * cm, "Clinical Copilot NLP  —  Asistente Inteligente para Historias Clínicas"
    )


# ---------------------------------------------------------------------------
# Helper: rectángulo redondeado (emulado con rect normal en reportlab canvas)
# ---------------------------------------------------------------------------
def rounded_rect(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    fill_color: colors.Color,
    stroke_color: colors.Color | None = None,
    radius: float = 6,
    line_width: float = 1,
) -> None:
    c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(line_width)
        c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    else:
        c.roundRect(x, y, w, h, radius, fill=1, stroke=0)


# ---------------------------------------------------------------------------
# Helper: badge de severidad
# ---------------------------------------------------------------------------
def severity_badge(
    c: canvas.Canvas, x: float, y: float, label: str, badge_color: colors.Color
) -> None:
    badge_w = 3.2 * cm
    badge_h = 0.75 * cm
    rounded_rect(c, x, y, badge_w, badge_h, badge_color, radius=4)
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 11)
    c.drawCentredString(x + badge_w / 2, y + 0.22 * cm, label)


# ---------------------------------------------------------------------------
# Helper: texto multilinea simple (wrap manual)
# ---------------------------------------------------------------------------
def draw_wrapped_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    font: str = FONT_REGULAR,
    size: float = 11,
    leading: float = 14,
    color: colors.Color = C_TEXT,
) -> float:
    """Dibuja texto con wrap manual. Devuelve la Y final (bajando)."""
    c.setFont(font, size)
    c.setFillColor(color)

    words = text.split()
    line = ""
    current_y = y

    for word in words:
        test = f"{line} {word}".strip()
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            c.drawString(x, current_y, line)
            current_y -= leading
            line = word

    if line:
        c.drawString(x, current_y, line)
        current_y -= leading

    return current_y


# ---------------------------------------------------------------------------
# Helper: flecha horizontal
# ---------------------------------------------------------------------------
def draw_arrow(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float) -> None:
    c.setStrokeColor(C_ACCENT)
    c.setLineWidth(1.5)
    c.line(x1, y1, x2, y2)
    # Cabeza de flecha
    ah = 5
    aw = 4
    c.setFillColor(C_ACCENT)
    path = c.beginPath()
    path.moveTo(x2, y2)
    path.lineTo(x2 - ah, y2 + aw)
    path.lineTo(x2 - ah, y2 - aw)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


# ===========================================================================
# SLIDES
# ===========================================================================


def slide_1_title(c: canvas.Canvas) -> None:
    """Slide 1 — Title slide."""
    # Fondo degradado visual: dos rectángulos
    c.setFillColor(C_DARK_BLUE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Rectángulo decorativo derecho
    c.setFillColor(C_MID_BLUE)
    c.rect(PAGE_W * 0.62, 0, PAGE_W * 0.38, PAGE_H, fill=1, stroke=0)

    # Línea de acento vertical
    c.setStrokeColor(C_ACCENT)
    c.setLineWidth(4)
    c.line(PAGE_W * 0.62, 0, PAGE_W * 0.62, PAGE_H)

    # Icono decorativo: círculos concéntricos (lado derecho)
    cx = PAGE_W * 0.81
    cy = PAGE_H * 0.5
    for r, alpha in [(130, 0.06), (95, 0.10), (65, 0.16), (40, 0.25)]:
        c.setFillColor(colors.HexColor("#FFFFFF"))
        c.setFillAlpha(alpha)
        c.circle(cx, cy, r, fill=1, stroke=0)
    c.setFillAlpha(1)

    # Cruz médica simplificada (lado derecho)
    cross_x = cx - 18
    cross_y = cy - 30
    c.setFillColor(colors.HexColor("#FFFFFF"))
    c.setFillAlpha(0.35)
    c.rect(cross_x + 12, cross_y, 12, 60, fill=1, stroke=0)
    c.rect(cross_x, cross_y + 24, 36, 12, fill=1, stroke=0)
    c.setFillAlpha(1)

    # Contenido textual
    # Etiqueta superior
    c.setFillColor(C_ACCENT)
    c.setFont(FONT_BOLD, 10)
    c.drawString(2.5 * cm, PAGE_H - 2 * cm, "PRESENTACIÓN DEL PROYECTO")

    # Línea separadora
    c.setStrokeColor(C_ACCENT)
    c.setLineWidth(2)
    c.line(2.5 * cm, PAGE_H - 2.4 * cm, 14 * cm, PAGE_H - 2.4 * cm)

    # Título principal
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 48)
    c.drawString(2.5 * cm, PAGE_H * 0.55, "Clinical Copilot")

    c.setFont(FONT_BOLD, 48)
    c.setFillColor(colors.HexColor("#64B5F6"))
    c.drawString(2.5 * cm, PAGE_H * 0.55 - 1.5 * cm, "NLP")

    # Subtítulo
    c.setFillColor(C_WHITE)
    c.setFont(FONT_REGULAR, 18)
    c.drawString(2.5 * cm, PAGE_H * 0.55 - 3 * cm, "Asistente Inteligente para Historias Clínicas")

    # Tagline
    c.setFillColor(colors.HexColor("#90CAF9"))
    c.setFont(FONT_ITALIC, 13)
    c.drawString(
        2.5 * cm, PAGE_H * 0.55 - 4 * cm, "Transformando datos clínicos en decisiones médicas"
    )

    # Línea decorativa inferior
    c.setStrokeColor(colors.HexColor("#64B5F6"))
    c.setLineWidth(1)
    c.line(2.5 * cm, 2.5 * cm, 13 * cm, 2.5 * cm)

    # Fase
    c.setFillColor(colors.HexColor("#90CAF9"))
    c.setFont(FONT_REGULAR, 10)
    c.drawString(2.5 * cm, 2 * cm, "Fase 1  |  Infraestructura y Pipeline Base")

    draw_page_number(c, 1, 8)


def slide_2_problema(c: canvas.Canvas) -> None:
    """Slide 2 — El Problema."""
    body_top = draw_header(
        c,
        "Barreras Críticas en el Sistema de Historias Clínicas",
        subtitle="Impactando la calidad de atención médica",
    )

    # Texto intro
    intro = (
        "El sistema actual de historias clínicas presenta tres desafíos críticos que afectan "
        "directamente la eficiencia médica y la seguridad del paciente:"
    )
    draw_wrapped_text(
        c,
        intro,
        x=1.5 * cm,
        y=body_top - 1.2 * cm,
        max_width=PAGE_W - 3 * cm,
        size=12,
        leading=16,
        color=C_TEXT,
    )

    # Tres tarjetas de desafío
    card_y = body_top - 4 * cm
    card_h = 3.8 * cm
    card_w = (PAGE_W - 4 * cm) / 3
    gap = 0.75 * cm
    start_x = 1.5 * cm

    challenges = [
        {
            "num": "01",
            "title": "Inercia Clínica",
            "desc": "Sobrecarga de lectura de notas previas que retrasa la atención directa al paciente.",
            "color": C_CRITICAL,
        },
        {
            "num": "02",
            "title": "Dispersión de Datos",
            "desc": "Información crítica (alergias, cambios de conducta) diluida en párrafos extensos.",
            "color": C_HIGH,
        },
        {
            "num": "03",
            "title": "Riesgo de Omisión",
            "desc": "Presión asistencial que puede llevar a omitir observaciones vitales para el tratamiento.",
            "color": C_SEVERE,
        },
    ]

    for i, ch in enumerate(challenges):
        x = start_x + i * (card_w + gap)

        # Sombra sutil
        c.setFillColor(colors.HexColor("#CCCCCC"))
        c.roundRect(x + 3, card_y - 3, card_w, card_h, 8, fill=1, stroke=0)

        # Tarjeta
        rounded_rect(c, x, card_y, card_w, card_h, C_WHITE, C_LIGHT_BLUE, radius=8, line_width=1)

        # Borde izquierdo de color
        c.setFillColor(ch["color"])
        c.roundRect(x, card_y, 0.35 * cm, card_h, 4, fill=1, stroke=0)

        # Número
        c.setFont(FONT_BOLD, 28)
        c.setFillColor(ch["color"])
        c.drawString(x + 0.7 * cm, card_y + card_h - 1.2 * cm, ch["num"])

        # Título de la tarjeta
        c.setFont(FONT_BOLD, 12)
        c.setFillColor(C_DARK_BLUE)
        c.drawString(x + 0.7 * cm, card_y + card_h - 1.9 * cm, ch["title"])

        # Descripción
        draw_wrapped_text(
            c,
            ch["desc"],
            x=x + 0.7 * cm,
            y=card_y + card_h - 2.6 * cm,
            max_width=card_w - 1.2 * cm,
            size=9.5,
            leading=13,
            color=C_TEXT,
        )

    draw_page_number(c, 2, 8)


def _challenge_slide(
    c: canvas.Canvas,
    page_num: int,
    challenge_num: str,
    title: str,
    severity_label: str,
    severity_color: colors.Color,
    description: str,
    impacto: str,
    icon_letter: str = "!",
) -> None:
    """Plantilla reutilizable para los slides de desafíos."""
    body_top = draw_header(c, f"Desafío {challenge_num}: {title}")

    body_w = PAGE_W - 3 * cm
    body_x = 1.5 * cm
    body_y = body_top - 0.8 * cm

    # Badge de severidad
    severity_badge(c, body_x, body_y - 0.1 * cm, severity_label, severity_color)

    # Descripción — caja grande
    desc_box_y = body_y - 2.4 * cm
    desc_box_h = 5.5 * cm
    desc_box_w = body_w * 0.65

    rounded_rect(
        c,
        body_x,
        desc_box_y,
        desc_box_w,
        desc_box_h,
        C_LIGHT_BLUE,
        C_MID_BLUE,
        radius=8,
        line_width=1,
    )

    # Etiqueta descripción
    c.setFont(FONT_BOLD, 9)
    c.setFillColor(C_MID_BLUE)
    c.drawString(body_x + 0.4 * cm, desc_box_y + desc_box_h - 0.5 * cm, "DESCRIPCIÓN")

    # Línea bajo etiqueta
    c.setStrokeColor(C_MID_BLUE)
    c.setLineWidth(0.5)
    c.line(
        body_x + 0.4 * cm,
        desc_box_y + desc_box_h - 0.65 * cm,
        body_x + desc_box_w - 0.4 * cm,
        desc_box_y + desc_box_h - 0.65 * cm,
    )

    draw_wrapped_text(
        c,
        description,
        x=body_x + 0.5 * cm,
        y=desc_box_y + desc_box_h - 1.2 * cm,
        max_width=desc_box_w - 1 * cm,
        size=11,
        leading=15,
        color=C_TEXT,
    )

    # Panel derecho — Impacto
    impact_x = body_x + desc_box_w + 0.8 * cm
    impact_w = body_w - desc_box_w - 0.8 * cm
    impact_h = desc_box_h

    rounded_rect(
        c,
        impact_x,
        desc_box_y,
        impact_w,
        impact_h,
        severity_color,
        None,
        radius=8,
    )

    # Ícono circular
    c_ix = impact_x + impact_w / 2
    c_iy = desc_box_y + impact_h - 1.4 * cm
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.2))
    c.circle(c_ix, c_iy, 0.55 * cm, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 20)
    c.drawCentredString(c_ix, c_iy - 0.2 * cm, icon_letter)

    c.setFont(FONT_BOLD, 10)
    c.setFillColor(C_WHITE)
    c.drawCentredString(c_ix, desc_box_y + impact_h - 2.3 * cm, "IMPACTO")

    # Línea separadora
    c.setStrokeColor(colors.Color(1, 1, 1, alpha=0.4))
    c.setLineWidth(0.5)
    c.line(
        impact_x + 0.4 * cm,
        desc_box_y + impact_h - 2.55 * cm,
        impact_x + impact_w - 0.4 * cm,
        desc_box_y + impact_h - 2.55 * cm,
    )

    draw_wrapped_text(
        c,
        impacto,
        x=impact_x + 0.4 * cm,
        y=desc_box_y + impact_h - 3.0 * cm,
        max_width=impact_w - 0.8 * cm,
        size=10,
        leading=13,
        color=C_WHITE,
    )

    draw_page_number(c, page_num, 8)


def slide_3_desafio1(c: canvas.Canvas) -> None:
    """Slide 3 — Desafío 1: Inercia Clínica."""
    _challenge_slide(
        c,
        page_num=3,
        challenge_num="1",
        title="Inercia Clínica por Sobrecarga",
        severity_label="CRÍTICO",
        severity_color=C_CRITICAL,
        description=(
            "El médico dedica la mayor parte del tiempo de consulta a leer notas previas, "
            "retrasando la interacción directa con el paciente y causando demoras "
            "en la toma de decisiones."
        ),
        impacto="Reducción del tiempo efectivo con el paciente",
        icon_letter="T",
    )


def slide_4_desafio2(c: canvas.Canvas) -> None:
    """Slide 4 — Desafío 2: Dispersión de la Información."""
    _challenge_slide(
        c,
        page_num=4,
        challenge_num="2",
        title="Dispersión de la Información",
        severity_label="ALTO",
        severity_color=C_HIGH,
        description=(
            "Hitos clave como cambios de conducta, alergias y motivos de descompensación "
            "se diluyen en párrafos extensos y repetitivos, dificultando "
            "su identificación rápida."
        ),
        impacto="Dificultad para identificar datos críticos",
        icon_letter="?",
    )


def slide_5_desafio3(c: canvas.Canvas) -> None:
    """Slide 5 — Desafío 3: Riesgo de Omisión."""
    _challenge_slide(
        c,
        page_num=5,
        challenge_num="3",
        title="Riesgo de Omisión",
        severity_label="SEVERO",
        severity_color=C_SEVERE,
        description=(
            "La presión asistencial y la lectura rápida pueden llevar a pasar por alto "
            "observaciones subjetivas vitales (ej: intolerancia a dosis) "
            "para el ajuste del tratamiento."
        ),
        impacto="Riesgo para la seguridad del paciente",
        icon_letter="!",
    )


def slide_6_solucion(c: canvas.Canvas) -> None:
    """Slide 6 — Nuestra Solución."""
    body_top = draw_header(
        c,
        "Clinical Copilot NLP  —  La Solución",
        subtitle="Pipeline inteligente de procesamiento clínico",
    )

    # ---------------------------------------------------------------------------
    # Diagrama de flujo
    # ---------------------------------------------------------------------------
    flow_y = body_top - 1.8 * cm
    box_h = 1.35 * cm
    box_w = 5.2 * cm
    gap_arrow = 0.7 * cm
    total_flow = 4 * box_w + 3 * (gap_arrow + 0.6 * cm)
    start_flow_x = (PAGE_W - total_flow) / 2

    flow_items = [
        ("Historia Clínica", "(texto libre)", C_MID_BLUE),
        ("API FastAPI", "(endpoint /api/analyze)", C_ACCENT),
        ("LLM GPT-4o", "(via Strategy Pattern)", colors.HexColor("#7B1FA2")),
        ("Resumen Ejecutivo", "(estructurado)", C_IMPLEMENTED),
    ]

    box_centers = []
    cx = start_flow_x
    for label, sublabel, color in flow_items:
        rounded_rect(c, cx, flow_y - box_h / 2, box_w, box_h, color, None, radius=6)
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(C_WHITE)
        c.drawCentredString(cx + box_w / 2, flow_y + 0.18 * cm, label)
        c.setFont(FONT_REGULAR, 8)
        c.setFillColor(colors.Color(1, 1, 1, alpha=0.8))
        c.drawCentredString(cx + box_w / 2, flow_y - 0.32 * cm, sublabel)
        box_centers.append((cx + box_w, flow_y))
        cx += box_w + gap_arrow + 0.6 * cm

    # Flechas entre boxes
    for i in range(len(flow_items) - 1):
        ax1 = box_centers[i][0]
        ax2 = ax1 + gap_arrow + 0.6 * cm
        ay = flow_y
        draw_arrow(c, ax1, ay, ax2 - 0.1 * cm, ay)

    # ---------------------------------------------------------------------------
    # Tres resultados del resumen
    # ---------------------------------------------------------------------------
    results_title_y = flow_y - 1.8 * cm
    c.setFont(FONT_BOLD, 12)
    c.setFillColor(C_DARK_BLUE)
    c.drawCentredString(PAGE_W / 2, results_title_y, "El Resumen Ejecutivo Técnico incluye:")

    result_w = (PAGE_W - 4 * cm) / 3
    result_gap = 0.75 * cm
    result_h = 2.8 * cm
    result_start_x = 1.5 * cm
    result_y = results_title_y - 3.2 * cm

    results = [
        {
            "icon": "D",
            "title": "Dominios Clínicos",
            "desc": "Categorización estructurada por áreas médicas (cardiología, neurología, etc.)",
            "color": C_MID_BLUE,
        },
        {
            "icon": "L",
            "title": "Línea Temporal",
            "desc": "Cronología de eventos clínicos relevantes ordenados en el tiempo.",
            "color": colors.HexColor("#7B1FA2"),
        },
        {
            "icon": "A",
            "title": "Alertas",
            "desc": "Identificación automática de riesgos, alergias y datos críticos.",
            "color": C_CRITICAL,
        },
    ]

    for i, res in enumerate(results):
        rx = result_start_x + i * (result_w + result_gap)

        # Sombra
        c.setFillColor(colors.HexColor("#CCCCCC"))
        c.roundRect(rx + 2, result_y - 2, result_w, result_h, 8, fill=1, stroke=0)

        # Card
        rounded_rect(
            c, rx, result_y, result_w, result_h, C_WHITE, res["color"], radius=8, line_width=1.5
        )

        # Badge circular con letra
        circle_cx = rx + 0.9 * cm
        circle_cy = result_y + result_h - 0.8 * cm
        c.setFillColor(res["color"])
        c.circle(circle_cx, circle_cy, 0.45 * cm, fill=1, stroke=0)
        c.setFillColor(C_WHITE)
        c.setFont(FONT_BOLD, 14)
        c.drawCentredString(circle_cx, circle_cy - 0.15 * cm, res["icon"])

        # Título
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(C_DARK_BLUE)
        c.drawString(rx + 1.6 * cm, result_y + result_h - 0.95 * cm, res["title"])

        # Descripción
        draw_wrapped_text(
            c,
            res["desc"],
            x=rx + 0.4 * cm,
            y=result_y + result_h - 1.6 * cm,
            max_width=result_w - 0.8 * cm,
            size=9.5,
            leading=13,
            color=C_TEXT,
        )

    draw_page_number(c, 6, 8)


def slide_7_arquitectura(c: canvas.Canvas) -> None:
    """Slide 7 — Arquitectura del Sistema."""
    body_top = draw_header(
        c,
        "Arquitectura del Sistema",
        subtitle="Diseño por capas con patrón Strategy para proveedores LLM",
    )

    # ---------------------------------------------------------------------------
    # Columna izquierda: Capas apiladas
    # ---------------------------------------------------------------------------
    left_x = 1.5 * cm
    left_w = PAGE_W * 0.55 - 1 * cm
    layer_h = 2.0 * cm
    layer_gap = 0.4 * cm
    layers_top = body_top - 1.0 * cm

    layers = [
        {
            "label": "API Layer",
            "detail": "FastAPI  |  GET /health  |  POST /api/analyze",
            "color": C_ACCENT,
        },
        {
            "label": "Service Layer",
            "detail": "ClinicalSummarizerService  |  Orquestación de prompt + LLM",
            "color": C_MID_BLUE,
        },
        {
            "label": "Infrastructure Layer",
            "detail": "LLMProvider ABC  |  Patrón Strategy  |  Factory",
            "color": C_DARK_BLUE,
        },
    ]

    current_y = layers_top
    for layer in layers:
        rounded_rect(
            c,
            left_x,
            current_y - layer_h,
            left_w,
            layer_h,
            layer["color"],
            None,
            radius=6,
        )
        c.setFont(FONT_BOLD, 12)
        c.setFillColor(C_WHITE)
        c.drawString(left_x + 0.5 * cm, current_y - 0.85 * cm, layer["label"])
        c.setFont(FONT_REGULAR, 9)
        c.setFillColor(colors.Color(1, 1, 1, alpha=0.85))
        c.drawString(left_x + 0.5 * cm, current_y - 1.45 * cm, layer["detail"])
        current_y -= layer_h + layer_gap

    # Flechas verticales entre capas
    arrow_x = left_x + left_w / 2
    for i in range(len(layers) - 1):
        ay_start = layers_top - (i + 1) * layer_h - i * layer_gap + 0.05 * cm
        ay_end = ay_start - layer_gap + 0.05 * cm
        # Línea
        c.setStrokeColor(C_LIGHT_BLUE)
        c.setLineWidth(1.5)
        c.line(arrow_x, ay_start, arrow_x, ay_end + 0.2 * cm)
        # Cabeza abajo
        c.setFillColor(C_LIGHT_BLUE)
        path = c.beginPath()
        path.moveTo(arrow_x, ay_end)
        path.lineTo(arrow_x - 4, ay_end + 6)
        path.lineTo(arrow_x + 4, ay_end + 6)
        path.close()
        c.drawPath(path, fill=1, stroke=0)

    # ---------------------------------------------------------------------------
    # Columna derecha: Proveedores LLM
    # ---------------------------------------------------------------------------
    right_x = PAGE_W * 0.55 + 0.5 * cm
    right_w = PAGE_W - right_x - 1 * cm
    prov_top = body_top - 1.0 * cm

    c.setFont(FONT_BOLD, 12)
    c.setFillColor(C_DARK_BLUE)
    c.drawString(right_x, prov_top - 0.3 * cm, "Proveedores LLM")

    # Línea separadora
    c.setStrokeColor(C_ACCENT)
    c.setLineWidth(2)
    c.line(right_x, prov_top - 0.55 * cm, right_x + right_w, prov_top - 0.55 * cm)

    providers = [
        {
            "name": "OpenAI GPT-4o",
            "status": "IMPLEMENTADO",
            "color": C_IMPLEMENTED,
            "detail": "Completamente funcional",
        },
        {
            "name": "Ollama",
            "status": "FUTURO",
            "color": C_FUTURE,
            "detail": "Stub — NotImplementedError",
        },
        {
            "name": "HuggingFace",
            "status": "FUTURO",
            "color": C_FUTURE,
            "detail": "Stub — NotImplementedError",
        },
    ]

    prov_y = prov_top - 1.3 * cm
    prov_h = 1.55 * cm
    prov_gap = 0.4 * cm

    for prov in providers:
        rounded_rect(
            c,
            right_x,
            prov_y - prov_h,
            right_w,
            prov_h,
            C_LIGHT_BLUE,
            C_MID_BLUE,
            radius=6,
            line_width=0.8,
        )

        # Badge status
        badge_w = 2.8 * cm
        badge_h = 0.55 * cm
        c.setFillColor(prov["color"])
        c.roundRect(
            right_x + right_w - badge_w - 0.3 * cm,
            prov_y - 0.9 * cm,
            badge_w,
            badge_h,
            3,
            fill=1,
            stroke=0,
        )
        c.setFont(FONT_BOLD, 7.5)
        c.setFillColor(C_WHITE)
        c.drawCentredString(
            right_x + right_w - badge_w / 2 - 0.3 * cm,
            prov_y - 0.76 * cm,
            prov["status"],
        )

        # Nombre
        c.setFont(FONT_BOLD, 11)
        c.setFillColor(C_DARK_BLUE)
        c.drawString(right_x + 0.4 * cm, prov_y - 0.75 * cm, prov["name"])

        # Detalle
        c.setFont(FONT_REGULAR, 8.5)
        c.setFillColor(C_SUBTLE)
        c.drawString(right_x + 0.4 * cm, prov_y - 1.3 * cm, prov["detail"])

        prov_y -= prov_h + prov_gap

    # Nota de patrón Strategy
    note_y = prov_y - 0.4 * cm
    rounded_rect(
        c,
        right_x,
        note_y - 1.3 * cm,
        right_w,
        1.3 * cm,
        colors.HexColor("#FFF9C4"),
        C_ACCENT,
        radius=6,
        line_width=1,
    )
    c.setFont(FONT_BOLD, 9)
    c.setFillColor(colors.HexColor("#E65100"))
    c.drawString(right_x + 0.4 * cm, note_y - 0.45 * cm, "Patrón Strategy:")
    c.setFont(FONT_REGULAR, 8.5)
    c.setFillColor(C_TEXT)
    c.drawString(
        right_x + 0.4 * cm, note_y - 0.95 * cm, "Swap de proveedor via env var LLM_PROVIDER"
    )

    draw_page_number(c, 7, 8)


def slide_8_cierre(c: canvas.Canvas) -> None:
    """Slide 8 — Closing slide."""
    # Mismo fondo que el title slide pero variado
    c.setFillColor(C_DARK_BLUE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Panel inferior de acento
    c.setFillColor(C_MID_BLUE)
    c.rect(0, 0, PAGE_W, PAGE_H * 0.28, fill=1, stroke=0)

    # Línea separadora
    c.setStrokeColor(C_ACCENT)
    c.setLineWidth(3)
    c.line(0, PAGE_H * 0.28, PAGE_W, PAGE_H * 0.28)

    # Patrón decorativo: líneas diagonales sutiles
    c.setStrokeColor(colors.Color(1, 1, 1, alpha=0.04))
    c.setLineWidth(1)
    for i in range(0, int(PAGE_W + PAGE_H), 40):
        c.line(i, 0, i - PAGE_H, PAGE_H)

    # Contenido central
    center_x = PAGE_W / 2
    center_y = PAGE_H * 0.62

    # Círculo decorativo de fondo
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.05))
    c.circle(center_x, center_y + 0.5 * cm, 4 * cm, fill=1, stroke=0)

    # Ícono (cruz medica)
    cross_cx = center_x
    cross_cy = center_y + 0.5 * cm
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.15))
    c.rect(cross_cx - 0.2 * cm, cross_cy - 1.0 * cm, 0.4 * cm, 2 * cm, fill=1, stroke=0)
    c.rect(cross_cx - 1.0 * cm, cross_cy - 0.2 * cm, 2 * cm, 0.4 * cm, fill=1, stroke=0)

    # Título
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 40)
    c.drawCentredString(center_x, center_y - 1.8 * cm, "Clinical Copilot NLP")

    # Subtítulo
    c.setFillColor(colors.HexColor("#64B5F6"))
    c.setFont(FONT_REGULAR, 16)
    c.drawCentredString(
        center_x, center_y - 2.8 * cm, "Mejorando la atención médica con inteligencia artificial"
    )

    # Fase
    c.setFillColor(colors.HexColor("#90CAF9"))
    c.setFont(FONT_ITALIC, 12)
    c.drawCentredString(center_x, center_y - 3.6 * cm, "Fase 1  —  Infraestructura y Pipeline Base")

    # Info en la franja inferior
    c.setFillColor(C_WHITE)
    c.setFont(FONT_BOLD, 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H * 0.18, "Tecnologías utilizadas")

    techs = ["FastAPI", "Python 3.14", "OpenAI GPT-4o", "Pydantic v2", "Docker", "Strategy Pattern"]
    tech_total_w = len(techs) * 3.2 * cm + (len(techs) - 1) * 0.5 * cm
    tx = (PAGE_W - tech_total_w) / 2
    ty = PAGE_H * 0.11

    for tech in techs:
        tw = 3.2 * cm
        th = 0.65 * cm
        rounded_rect(c, tx, ty, tw, th, colors.Color(1, 1, 1, alpha=0.15), None, radius=3)
        c.setFillColor(C_WHITE)
        c.setFont(FONT_REGULAR, 8.5)
        c.drawCentredString(tx + tw / 2, ty + 0.2 * cm, tech)
        tx += tw + 0.5 * cm

    draw_page_number(c, 8, 8)


# ===========================================================================
# Main
# ===========================================================================


def main() -> None:
    output_dir = Path(__file__).parent
    output_path = output_dir / "clinical_copilot_nlp_slides.pdf"

    c = canvas.Canvas(str(output_path), pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Clinical Copilot NLP — Presentación")
    c.setAuthor("Clinical Copilot NLP Project")
    c.setSubject("Asistente Inteligente para Historias Clínicas")

    slides = [
        slide_1_title,
        slide_2_problema,
        slide_3_desafio1,
        slide_4_desafio2,
        slide_5_desafio3,
        slide_6_solucion,
        slide_7_arquitectura,
        slide_8_cierre,
    ]

    for i, slide_fn in enumerate(slides):
        slide_fn(c)
        if i < len(slides) - 1:
            c.showPage()

    c.save()
    print(f"PDF generado exitosamente: {output_path}")
    print(f"Total de slides: {len(slides)}")


if __name__ == "__main__":
    main()
