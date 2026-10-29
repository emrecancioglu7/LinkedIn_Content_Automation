import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CONTENT_ROOT = Path(os.environ.get("CONTENT_ROOT", "/data/content/generated")).resolve()
LOGO_PATH = Path(os.environ.get("LOGO_PATH", "/data/brand/linkedin-app-logo.png"))
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)

# emrecancioglu.com design tokens
SITE_BG = (10, 11, 13, 255)          # #0a0b0d
SITE_SURFACE = (19, 21, 25, 255)     # #131519
SITE_SURFACE_2 = (26, 29, 34, 255)   # #1a1d22
SITE_ACCENT = (52, 211, 153, 255)    # #34d399
SITE_ACCENT_STRONG = (16, 185, 129, 255)  # #10b981
SITE_TEXT = (236, 236, 234, 255)     # #ececea
SITE_MUTED = (154, 154, 151, 255)    # #9a9a97
SITE_BORDER = (47, 51, 55, 255)


def clean_text(value, limit):
    return " ".join(str(value or "").split())[:limit].strip()


def fit_font(draw, text, max_width, start, minimum, font_path):
    size = start
    while size > minimum:
        font = ImageFont.truetype(font_path, size)
        if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(font_path, minimum)


def wrap_lines(draw, text, font, max_width):
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if not current or draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_multiline_title(draw, text, max_width, start=38, minimum=28, max_lines=2):
    for size in range(start, minimum - 1, -2):
        font = ImageFont.truetype(FONT_BOLD, size)
        lines = wrap_lines(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines
    font = ImageFont.truetype(FONT_BOLD, minimum)
    return font, wrap_lines(draw, text, font, max_width)[:max_lines]


def truncate_words(value, limit):
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    shortened = text[: max(limit - 1, 1)].rsplit(" ", 1)[0].strip()
    return f"{shortened or text[: max(limit - 1, 1)]}…"


def extract_points(body):
    candidates = re.split(r"(?:\n+|(?<=[.!?])\s+)", clean_text(body, 1200))
    return [item.strip(" -•\t") for item in candidates if len(item.strip(" -•\t")) >= 12][:3]


PILLAR_LABELS = {
    "OT_VERI_MIMARISI": "OT VERİ MİMARİSİ",
    "ENDUSTRIYEL_AI": "ENDÜSTRİYEL YAPAY ZEKA",
    "ENERJI_SURDURULEBILIRLIK": "ENERJİ & SÜRDÜRÜLEBİLİRLİK",
    "URETIMDE_GENAI": "ÜRETİMDE GENAI",
    "OT_SIBER_GUVENLIK": "OT SİBER GÜVENLİK",
    "TEKNIK_LIDERLIK": "TEKNİK LİDERLİK",
}

PILLAR_TAGS = {
    "OT_VERI_MIMARISI": ["OPC UA", "MQTT", "UNIFIED NAMESPACE"],
    "ENDUSTRIYEL_AI": ["VERİ KALİTESİ", "AI MODELİ", "OPERASYONEL AKSİYON"],
    "ENERJI_SURDURULEBILIRLIK": ["ENERJİ VERİSİ", "ÜRETİM BAĞLAMI", "İYİLEŞTİRME"],
    "URETIMDE_GENAI": ["AI AGENT", "YETKİ SINIRI", "İNSAN ONAYI"],
    "OT_SIBER_GUVENLIK": ["YETKİ KONTROLÜ", "AĞ SEGMENTASYONU", "SÜREKLİ İZLEME"],
    "TEKNIK_LIDERLIK": ["TEKNİK KARAR", "OPERASYONEL RİSK", "SÜRDÜRÜLEBİLİRLİK"],
}

PILLAR_CALLOUTS = {
    "OT_VERI_MIMARISI": [("left", 350, "VERİ KAYNAĞI"), ("right", 620, "OPC UA SUNUCUSU"), ("left", 850, "MQTT BROKER"), ("right", 1110, "UNIFIED NAMESPACE")],
    "ENDUSTRIYEL_AI": [("left", 350, "SENSÖR VERİSİ"), ("right", 620, "EDGE SUNUCU"), ("left", 850, "AI MODELİ"), ("right", 1110, "OPERATÖR AKSİYONU")],
    "ENERJI_SURDURULEBILIRLIK": [("left", 350, "ENERJİ SAYACI"), ("right", 620, "VERİ SUNUCUSU"), ("left", 850, "ANALİTİK KATMANI"), ("right", 1110, "İYİLEŞTİRME AKSİYONU")],
    "URETIMDE_GENAI": [("left", 350, "KULLANICI"), ("right", 620, "AI AGENT"), ("left", 850, "YETKİ SINIRI"), ("right", 1110, "OT SİSTEMİ")],
    "OT_SIBER_GUVENLIK": [("left", 350, "KULLANICI / HESAP"), ("right", 620, "VERİTABANI SUNUCUSU"), ("left", 850, "GÜVENLİK SINIRI"), ("right", 1110, "OT VLAN / SAHA AĞI")],
    "TEKNIK_LIDERLIK": [("left", 350, "TEKNİK KARAR"), ("right", 620, "PLATFORM KATMANI"), ("left", 850, "OPERASYONEL RİSK"), ("right", 1110, "İŞ SONUCU")],
}


def visual_title(value):
    text = clean_text(value, 140)
    first_clause = re.split(r"[,;:]", text, maxsplit=1)[0].strip(" .!?–—")
    if 18 <= len(first_clause) <= 52:
        return first_clause
    return truncate_words(text, 52).strip(" .!?–—")


def draw_callout(draw, side, y, label):
    font = ImageFont.truetype(FONT_BOLD, 16)
    text_width = draw.textbbox((0, 0), label, font=font)[2]
    width = text_width + 28
    if side == "left":
        x1, x2 = 54, 54 + width
        line_start, line_end = x2, min(x2 + 92, 555)
    else:
        x2, x1 = 1146, 1146 - width
        line_start, line_end = x1, max(x1 - 92, 645)
    draw.line((line_start, y, line_end, y), fill=SITE_ACCENT, width=2)
    draw.ellipse((line_end - 4, y - 4, line_end + 4, y + 4), fill=SITE_ACCENT)
    draw.rounded_rectangle((x1, y - 18, x2, y + 18), radius=18, fill=SITE_SURFACE, outline=SITE_ACCENT, width=2)
    draw.text(((x1 + x2) / 2, y), label, font=font, fill=SITE_TEXT, anchor="mm")


def vertical_gradient(image, top, bottom, y_start, y_end):
    draw = ImageDraw.Draw(image)
    span = max(y_end - y_start, 1)
    for y in range(y_start, y_end):
        ratio = (y - y_start) / span
        color = tuple(round(top[index] + (bottom[index] - top[index]) * ratio) for index in range(3)) + (255,)
        draw.line((0, y, image.width, y), fill=color)


def rounded_image(source, size, radius):
    source = source.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
    source.putalpha(mask)
    return source


def render(post_id, title, points, body, pillar):
    if not UUID_RE.fullmatch(post_id):
        raise ValueError("invalid post id")
    image_path = (CONTENT_ROOT / f"{post_id}.png").resolve()
    if image_path.parent != CONTENT_ROOT or not image_path.is_file():
        raise ValueError("image not found")

    image = Image.open(image_path).convert("RGBA")
    # Re-rendering a previously branded 4:5 preview reuses only its illustration.
    if image.size == (1200, 1500):
        image = image.crop((30, 236, 1170, 1376))
    if image.size != (1200, 1200):
        image = image.resize((1200, 1200), Image.Resampling.LANCZOS)

    pillar_key = str(pillar or "")
    title = visual_title(title)
    source_points = PILLAR_TAGS.get(pillar_key) or points or extract_points(body)
    points = [truncate_words(item, 24) for item in source_points if clean_text(item, 24)][:3]

    # Premium 4:5 LinkedIn canvas. The illustration remains in its own card;
    # all typography lives in dedicated header/footer areas.
    canvas = Image.new("RGBA", (1200, 1500), SITE_BG)
    vertical_gradient(canvas, (10, 11, 13), (14, 29, 25), 0, 230)
    draw = ImageDraw.Draw(canvas)
    draw.ellipse((1000, -90, 1260, 170), outline=(22, 91, 68, 255), width=3)
    draw.ellipse((1060, -30, 1220, 130), outline=(35, 122, 91, 255), width=2)
    draw.line((0, 228, 1200, 228), fill=SITE_ACCENT, width=3)

    category = PILLAR_LABELS.get(str(pillar or ""), "TEKNİK NOT")
    category_font = ImageFont.truetype(FONT_BOLD, 17)
    category_width = draw.textbbox((0, 0), category, font=category_font)[2] + 34
    draw.rounded_rectangle((54, 20, 54 + category_width, 54), radius=17, fill=SITE_SURFACE_2, outline=SITE_ACCENT, width=2)
    draw.text((71, 37), category, font=category_font, fill=SITE_ACCENT, anchor="lm")

    title_font, title_lines = fit_multiline_title(draw, title, 1080)
    title_y = 64 if len(title_lines) > 1 else 78
    line_step = title_font.size + 3
    for index, line in enumerate(title_lines):
        draw.text((54, title_y + index * line_step), line, font=title_font, fill=SITE_TEXT)

    for index, point in enumerate(points):
        x = 54 + (index * 377)
        draw.rounded_rectangle((x, 168, x + 350, 214), radius=23, fill=SITE_SURFACE_2, outline=SITE_BORDER, width=1)
        draw.ellipse((x + 16, 185, x + 26, 195), fill=SITE_ACCENT)
        point_font = fit_font(draw, point, 292, 19, 14, FONT_REGULAR)
        draw.text((x + 38, 191), point, font=point_font, fill=SITE_TEXT, anchor="lm")

    # Framed illustration card with a restrained shadow and no text overlay.
    draw.rounded_rectangle((24, 242, 1184, 1402), radius=32, fill=(5, 6, 8, 255))
    card = rounded_image(image, 1140, 28)
    canvas.alpha_composite(card, (30, 236))
    draw.rounded_rectangle((30, 236, 1170, 1376), radius=28, outline=SITE_BORDER, width=2)
    for side, y, label in PILLAR_CALLOUTS.get(pillar_key, []):
        draw_callout(draw, side, y, label)

    # Deterministic brand signature in its own footer band.
    vertical_gradient(canvas, (19, 21, 25), (10, 11, 13), 1400, 1500)
    draw = ImageDraw.Draw(canvas)
    tagline_font = ImageFont.truetype(FONT_REGULAR, 22)
    draw.text((60, 1450), "OT • IIoT • Endüstriyel AI", font=tagline_font, fill=SITE_MUTED, anchor="lm")
    if LOGO_PATH.is_file():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        content_box = logo.getbbox()
        if content_box:
            logo = logo.crop(content_box)
        logo.thumbnail((52, 52), Image.Resampling.LANCZOS)
    brand_font = ImageFont.truetype(FONT_BOLD, 25)
    brand_text = "emrecancioglu.com"
    brand_width = draw.textbbox((0, 0), brand_text, font=brand_font)[2]
    group_width = logo.width + 10 + brand_width if LOGO_PATH.is_file() else brand_width
    group_x = 1140 - group_width
    if LOGO_PATH.is_file():
        canvas.alpha_composite(logo, (group_x, 1450 - logo.height // 2))
        group_x += logo.width + 10
    draw.text((group_x, 1450), brand_text, font=brand_font, fill=SITE_TEXT, anchor="lm")

    canvas.convert("RGB").save(image_path, "PNG", optimize=True)
    return str(image_path)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/render":
            self.send_error(404)
            return
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 16384)
            payload = json.loads(self.rfile.read(length))
            path = render(payload.get("post_id", ""), payload.get("title", ""), payload.get("points", []), payload.get("body", ""), payload.get("pillar", ""))
            body = json.dumps({"ok": True, "image_path": path}).encode()
            self.send_response(200)
        except (ValueError, json.JSONDecodeError) as error:
            body = json.dumps({"ok": False, "error": str(error)}).encode()
            self.send_response(400)
        except Exception:
            body = json.dumps({"ok": False, "error": "render failed"}).encode()
            self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


ThreadingHTTPServer(("0.0.0.0", 8081), Handler).serve_forever()
