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
SITE_RISK = (248, 113, 113, 255)

ALLOWED_LAYOUTS = {"process_flow", "layered_architecture", "comparison", "cause_effect", "cycle"}
ALLOWED_ICONS = {"user", "identity", "shield", "lock", "network", "server", "database", "sensor", "plc", "ai", "energy", "analytics", "approval", "decision", "eye", "pulse", "cloud", "gateway"}


def clean_text(value, limit):
    return " ".join(str(value or "").split())[:limit].strip()


def turkish_upper(value):
    return str(value or "").replace("i", "İ").replace("ı", "I").upper()


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

PILLAR_HEADERS = {
    "OT_VERI_MIMARISI": ("ENDÜSTRİYEL VERİ MİMARİSİ", "INDUSTRIAL DATA ARCHITECTURE"),
    "ENDUSTRIYEL_AI": ("ENDÜSTRİYEL YAPAY ZEKA", "INDUSTRIAL AI"),
    "ENERJI_SURDURULEBILIRLIK": ("ENDÜSTRİYEL ENERJİ YÖNETİMİ", "INDUSTRIAL ENERGY MANAGEMENT"),
    "URETIMDE_GENAI": ("ÜRETİMDE AI AGENT", "AGENTIC AI"),
    "OT_SIBER_GUVENLIK": ("OT SİBER GÜVENLİK", "OT CYBER SECURITY"),
    "TEKNIK_LIDERLIK": ("TEKNİK KARAR TASARIMI", "TECHNICAL DECISION DESIGN"),
}

HEADER_RULES = [
    (re.compile(r"(vlan|segment|ayrıştır)", re.I), "AĞ SEGMENTASYONU", "NETWORK SEGMENTATION"),
    (re.compile(r"(yetki|hesa|kimli|eriş|\brol)", re.I), "OT ERİŞİM KONTROLÜ", "ACCESS CONTROL"),
    (re.compile(r"\b(opc\s*ua)\b", re.I), "OPC UA", "OPEN PLATFORM COMMUNICATIONS"),
    (re.compile(r"\b(mqtt)\b", re.I), "MQTT", "MESSAGE QUEUING TELEMETRY TRANSPORT"),
    (re.compile(r"\b(unified namespace|uns)\b", re.I), "UNIFIED NAMESPACE", "UNS"),
    (re.compile(r"\b(ai agent|agentic|ajan)\b", re.I), "AI AGENT MİMARİSİ", "AGENTIC AI ARCHITECTURE"),
    (re.compile(r"\b(enerji|tüketim|verimlilik)\b", re.I), "ENDÜSTRİYEL ENERJİ YÖNETİMİ", "INDUSTRIAL ENERGY MANAGEMENT"),
]

PILLAR_CALLOUTS = {
    "OT_VERI_MIMARISI": [
        ("left", 350, "VERİ KAYNAĞI", "Saha verisi üretim noktasında oluşur"),
        ("right", 600, "OPC UA SUNUCUSU", "Veriyi ortak ve güvenli modele taşır"),
        ("left", 850, "MQTT BROKER", "Mesajları ilgili tüketicilere dağıtır"),
        ("right", 1090, "UNIFIED NAMESPACE", "Tek ve güncel operasyonel bağlam sağlar"),
    ],
    "ENDUSTRIYEL_AI": [
        ("left", 350, "SENSÖR VERİSİ", "Makinenin gerçek durumunu temsil eder"),
        ("right", 600, "EDGE SUNUCU", "Veriyi kaynağa yakın işler ve filtreler"),
        ("left", 850, "AI MODELİ", "Örüntüyü analiz ederek tahmin üretir"),
        ("right", 1090, "OPERATÖR AKSİYONU", "Tahmin kontrollü bir karara dönüşür"),
    ],
    "ENERJI_SURDURULEBILIRLIK": [
        ("left", 350, "ENERJİ SAYACI", "Tüketimi makine ve hat bazında ölçer"),
        ("right", 600, "VERİ SUNUCUSU", "Enerji ve üretim verisini eşleştirir"),
        ("left", 850, "ANALİTİK KATMANI", "Kayıp ve anormallikleri görünür kılar"),
        ("right", 1090, "İYİLEŞTİRME", "Ölçülebilir operasyonel aksiyon üretir"),
    ],
    "URETIMDE_GENAI": [
        ("left", 350, "KULLANICI", "Hedefi ve çalışma bağlamını tanımlar"),
        ("right", 600, "AI AGENT", "Görevi adımlara ayırır ve araçları seçer"),
        ("left", 850, "YETKİ SINIRI", "Riskli işlemleri politika ile sınırlar"),
        ("right", 1090, "OT SİSTEMİ", "Yalnız onaylanan komutu uygular"),
    ],
    "OT_SIBER_GUVENLIK": [
        ("left", 350, "KULLANICI / HESAP", "Erişim talebi kimlik ile başlar"),
        ("right", 600, "YETKİ KONTROLÜ", "Rol ve ihtiyaç doğrulanmadan geçiş yoktur"),
        ("left", 850, "GÜVENLİK SINIRI", "İzin verilmeyen trafik burada durur"),
        ("right", 1090, "OT VLAN / SAHA AĞI", "Yalnız gerekli sisteme erişim açılır"),
    ],
    "TEKNIK_LIDERLIK": [
        ("left", 350, "TEKNİK KARAR", "İhtiyaç, kısıt ve hedef birlikte ele alınır"),
        ("right", 600, "PLATFORM KATMANI", "Karar sürdürülebilir bir yapıya dönüşür"),
        ("left", 850, "OPERASYONEL RİSK", "Etkiler devreye almadan önce görünür olur"),
        ("right", 1090, "İŞ SONUCU", "Teknik tercih ölçülebilir değer üretir"),
    ],
}

PILLAR_TAKEAWAYS = {
    "OT_VERI_MIMARISI": "HAM VERİ → ORTAK MODEL → GÜVENİLİR OPERASYONEL BAĞLAM",
    "ENDUSTRIYEL_AI": "VERİ → TAHMİN → İNSAN KONTROLLÜ OPERASYONEL AKSİYON",
    "ENERJI_SURDURULEBILIRLIK": "ÖLÇ → ÜRETİMLE EŞLEŞTİR → KAYBI AZALT",
    "URETIMDE_GENAI": "HEDEF → AGENT PLANI → YETKİ KONTROLÜ → ONAYLI AKSİYON",
    "OT_SIBER_GUVENLIK": "KİMLİK → MİNİMUM YETKİ → AĞ AYRIŞTIRMA → İZLENEBİLİR ERİŞİM",
    "TEKNIK_LIDERLIK": "KARAR → RİSK ANALİZİ → SÜRDÜRÜLEBİLİR İŞ SONUCU",
}

PILLAR_BENEFITS = {
    "OT_VERI_MIMARISI": [
        ("network", "TEK VERİ BAĞLAMI", "Sistemler aynı anlamı kullanır"),
        ("pulse", "GERÇEK ZAMANLI", "Değişim anında ilgili yere ulaşır"),
        ("eye", "UÇTAN UCA GÖRÜŞ", "Veri yolu kolayca izlenebilir"),
        ("shield", "YÖNETİLEBİLİR", "Entegrasyon karmaşası azalır"),
    ],
    "ENDUSTRIYEL_AI": [
        ("pulse", "ERKEN SİNYAL", "Anormallik büyümeden görünür olur"),
        ("network", "BAĞLAMLI VERİ", "Model doğru üretim koşulunu görür"),
        ("eye", "AÇIKLANABİLİR", "Operatör kararın nedenini izler"),
        ("shield", "KONTROLLÜ AKSİYON", "İnsan onayı süreçte kalır"),
    ],
    "ENERJI_SURDURULEBILIRLIK": [
        ("pulse", "ÖLÇÜLEBİLİR", "Tüketim kaynak bazında görünür"),
        ("network", "ÜRETİMLE BAĞLI", "Enerji ve çıktı birlikte okunur"),
        ("eye", "KAYIP GÖRÜNÜRLÜĞÜ", "Anormallikler kolayca ayrışır"),
        ("shield", "KALICI İYİLEŞME", "Aksiyon etkisi takip edilir"),
    ],
    "URETIMDE_GENAI": [
        ("network", "ARAÇ KULLANIMI", "Agent doğru sistemi seçer"),
        ("shield", "YETKİ SINIRI", "Riskli işlem politika ile durur"),
        ("eye", "İNSAN ONAYI", "Kritik karar kontrol altında kalır"),
        ("pulse", "HIZLI GERİ BİLDİRİM", "Sonuç süreç içinde doğrulanır"),
    ],
    "OT_SIBER_GUVENLIK": [
        ("lock", "MİNİMUM YETKİ", "Yalnız ihtiyaç kadar erişim"),
        ("network", "AĞ AYRIŞTIRMA", "Risk OT VLAN'a yayılmaz"),
        ("eye", "İZLENEBİLİRLİK", "Her erişim kayda alınır"),
        ("shield", "SAHA KORUMASI", "Kritik OT sistemi izole kalır"),
    ],
    "TEKNIK_LIDERLIK": [
        ("eye", "NET GEREKSİNİM", "Kararın amacı görünür kalır"),
        ("network", "ORTAK YÖN", "Ekipler aynı mimariyi paylaşır"),
        ("shield", "RİSK KONTROLÜ", "Etkiler önceden değerlendirilir"),
        ("pulse", "ÖLÇÜLEBİLİR SONUÇ", "Teknik tercih değerle izlenir"),
    ],
}


def visual_title(value):
    text = clean_text(value, 140)
    first_clause = re.split(r"[,;:]", text, maxsplit=1)[0].strip(" .!?–—")
    if 18 <= len(first_clause) <= 52:
        return first_clause
    return truncate_words(text, 52).strip(" .!?–—")


def infographic_header(value, pillar_key):
    source = clean_text(value, 180).strip(" .")
    for pattern, concept, expansion in HEADER_RULES:
        if pattern.search(source):
            return concept, expansion, truncate_words(source, 100)
    concept, expansion = PILLAR_HEADERS.get(pillar_key, ("TEKNİK MİMARİ", "TECHNICAL ARCHITECTURE"))
    return concept, expansion, truncate_words(source, 100)


def normalize_visual_spec(value, title, body, pillar_key):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            value = {}
    spec = value if isinstance(value, dict) else {}
    stages = spec.get("stages") if isinstance(spec.get("stages"), list) else []
    takeaways = spec.get("takeaways") if isinstance(spec.get("takeaways"), list) else []
    if spec.get("layout_type") in ALLOWED_LAYOUTS and 3 <= len(stages) <= 5 and 3 <= len(takeaways) <= 4:
        normalized_stages = []
        for stage in stages[:5]:
            if not isinstance(stage, dict):
                continue
            normalized_stages.append({
                "label": truncate_words(stage.get("label"), 26),
                "description": truncate_words(stage.get("description"), 58),
                "icon": stage.get("icon") if stage.get("icon") in ALLOWED_ICONS else "decision",
                "state": stage.get("state") if stage.get("state") in {"normal", "controlled", "risk", "outcome"} else "normal",
            })
        normalized_takeaways = []
        for item in takeaways[:4]:
            if not isinstance(item, dict):
                continue
            normalized_takeaways.append({
                "label": truncate_words(item.get("label"), 24),
                "description": truncate_words(item.get("description"), 46),
                "icon": item.get("icon") if item.get("icon") in ALLOWED_ICONS else "eye",
            })
        if 3 <= len(normalized_stages) <= 5 and 3 <= len(normalized_takeaways) <= 4:
            return {
                "layout_type": spec["layout_type"],
                "technical_title": truncate_words(spec.get("technical_title"), 42),
                "international_name": truncate_words(spec.get("international_name"), 48),
                "curiosity_subtitle": truncate_words(spec.get("curiosity_subtitle"), 92),
                "stages": normalized_stages,
                "connections": spec.get("connections") if isinstance(spec.get("connections"), list) else [],
                "takeaways": normalized_takeaways,
            }

    concept, expansion, subtitle = infographic_header(title, pillar_key)
    fallback_stages = []
    for _, _, label, detail in PILLAR_CALLOUTS.get(pillar_key, []):
        fallback_stages.append({"label": label, "description": detail, "icon": "decision", "state": "normal"})
    fallback_takeaways = [
        {"icon": icon, "label": label, "description": detail}
        for icon, label, detail in PILLAR_BENEFITS.get(pillar_key, [])
    ]
    return {
        "layout_type": "process_flow",
        "technical_title": concept,
        "international_name": expansion,
        "curiosity_subtitle": subtitle or visual_title(body),
        "stages": fallback_stages,
        "connections": [],
        "takeaways": fallback_takeaways,
    }


def stage_positions(count, layout_type):
    if count <= 1:
        return [("left", 700)]
    start, end = 350, 1090
    ys = [round(start + index * (end - start) / (count - 1)) for index in range(count)]
    if layout_type == "comparison":
        sides = ["left" if index % 2 == 0 else "right" for index in range(count)]
    elif layout_type == "cycle" and count >= 4:
        sides = ["left", "right", "right", "left"] + ["right"]
    else:
        sides = ["left" if index % 2 == 0 else "right" for index in range(count)]
    return list(zip(sides[:count], ys))


def draw_callout(draw, side, y, label, detail, number=None, state="normal"):
    label_font = ImageFont.truetype(FONT_BOLD, 16)
    detail_font = ImageFont.truetype(FONT_REGULAR, 14)
    width = 292
    height = 84
    if side == "left":
        x1, x2 = 54, 54 + width
        line_start, line_end = x2, 500
    else:
        x2, x1 = 1146, 1146 - width
        line_start, line_end = x1, 700
    accent = SITE_RISK if state == "risk" else SITE_ACCENT
    # The illustration follows a centered vertical spine. Each side card
    # connects horizontally to its matching stage at the same height.
    draw.line((line_start, y, line_end, y), fill=accent, width=2)
    draw.ellipse((line_end - 4, y - 4, line_end + 4, y + 4), fill=accent)
    draw.rounded_rectangle((x1, y - height // 2, x2, y + height // 2), radius=16, fill=SITE_SURFACE, outline=accent, width=2)
    if number is None:
        draw.ellipse((x1 + 14, y - 26, x1 + 24, y - 16), fill=accent)
        label_x = x1 + 34
        detail_x = x1 + 34
    else:
        badge_font = ImageFont.truetype(FONT_BOLD, 11)
        draw.ellipse((x1 + 14, y - 15, x1 + 44, y + 15), fill=(15, 57, 45, 255), outline=accent, width=2)
        draw.text((x1 + 29, y), f"{number:02d}", font=badge_font, fill=SITE_TEXT, anchor="mm")
        label_x = x1 + 58
        detail_x = x1 + 58
    draw.text((label_x, y - 15), turkish_upper(label), font=label_font, fill=SITE_TEXT, anchor="lm")
    detail_width = x2 - detail_x - 16
    detail_lines = wrap_lines(draw, truncate_words(detail, 64), detail_font, detail_width)[:2]
    for line_index, line in enumerate(detail_lines):
        draw.text((detail_x, y + 10 + line_index * 16), line, font=detail_font, fill=SITE_MUTED, anchor="lm")


def draw_icon(draw, kind, cx, cy):
    draw.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), fill=(15, 57, 45, 255), outline=SITE_ACCENT, width=2)
    color = SITE_ACCENT
    if kind in {"user", "identity"}:
        draw.ellipse((cx - 5, cy - 11, cx + 5, cy - 1), outline=color, width=3)
        draw.arc((cx - 12, cy - 2, cx + 12, cy + 16), 180, 360, fill=color, width=3)
        if kind == "identity":
            draw.line((cx + 7, cy - 10, cx + 13, cy - 10), fill=color, width=2)
            draw.line((cx + 7, cy - 5, cx + 14, cy - 5), fill=color, width=2)
    elif kind == "lock":
        draw.arc((cx - 8, cy - 13, cx + 8, cy + 4), 180, 360, fill=color, width=3)
        draw.rounded_rectangle((cx - 11, cy - 3, cx + 11, cy + 13), radius=3, outline=color, width=3)
        draw.ellipse((cx - 2, cy + 3, cx + 2, cy + 7), fill=color)
    elif kind == "network":
        points = [(cx, cy - 10), (cx - 11, cy + 8), (cx + 11, cy + 8)]
        draw.line((points[0], points[1]), fill=color, width=2)
        draw.line((points[0], points[2]), fill=color, width=2)
        draw.line((points[1], points[2]), fill=color, width=2)
        for px, py in points:
            draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=color)
    elif kind == "eye":
        draw.arc((cx - 14, cy - 9, cx + 14, cy + 9), 190, 350, fill=color, width=3)
        draw.arc((cx - 14, cy - 9, cx + 14, cy + 9), 10, 170, fill=color, width=3)
        draw.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=color)
    elif kind == "pulse":
        draw.line((cx - 14, cy, cx - 7, cy, cx - 3, cy - 9, cx + 3, cy + 9, cx + 8, cy, cx + 14, cy), fill=color, width=3)
    elif kind in {"server", "plc", "gateway"}:
        draw.rounded_rectangle((cx - 13, cy - 12, cx + 13, cy + 12), radius=3, outline=color, width=2)
        for offset in (-6, 0, 6):
            draw.line((cx - 8, cy + offset, cx + 5, cy + offset), fill=color, width=2)
            draw.ellipse((cx + 8, cy + offset - 1, cx + 10, cy + offset + 1), fill=color)
    elif kind == "database":
        draw.ellipse((cx - 12, cy - 12, cx + 12, cy - 4), outline=color, width=2)
        draw.rectangle((cx - 12, cy - 8, cx + 12, cy + 9), outline=color, width=2)
        draw.arc((cx - 12, cy + 4, cx + 12, cy + 13), 0, 180, fill=color, width=2)
    elif kind in {"sensor", "cloud"}:
        if kind == "sensor":
            draw.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=color)
            for radius in (9, 14):
                draw.arc((cx - radius, cy - radius, cx + radius, cy + radius), 210, 330, fill=color, width=2)
                draw.arc((cx - radius, cy - radius, cx + radius, cy + radius), 30, 150, fill=color, width=2)
        else:
            draw.arc((cx - 14, cy - 5, cx, cy + 11), 90, 270, fill=color, width=3)
            draw.arc((cx - 5, cy - 13, cx + 13, cy + 9), 180, 355, fill=color, width=3)
            draw.line((cx - 8, cy + 9, cx + 12, cy + 9), fill=color, width=3)
    elif kind in {"ai", "analytics", "decision"}:
        if kind == "analytics":
            draw.line((cx - 13, cy + 11, cx - 13, cy - 10), fill=color, width=2)
            draw.line((cx - 13, cy + 11, cx + 13, cy + 11), fill=color, width=2)
            draw.line((cx - 8, cy + 5, cx - 2, cy - 2, cx + 3, cy + 2, cx + 11, cy - 9), fill=color, width=3)
        else:
            nodes = [(cx - 10, cy - 7), (cx + 10, cy - 7), (cx, cy + 10)]
            draw.line((nodes[0], nodes[1]), fill=color, width=2)
            draw.line((nodes[0], nodes[2]), fill=color, width=2)
            draw.line((nodes[1], nodes[2]), fill=color, width=2)
            for px, py in nodes:
                draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=color)
    elif kind == "energy":
        draw.polygon([(cx + 2, cy - 14), (cx - 9, cy + 1), (cx - 1, cy + 1), (cx - 5, cy + 14), (cx + 10, cy - 4), (cx + 2, cy - 4)], fill=color)
    elif kind == "approval":
        draw.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), outline=color, width=2)
        draw.line((cx - 7, cy, cx - 2, cy + 6, cx + 9, cy - 7), fill=color, width=3)
    else:
        shield = [(cx, cy - 13), (cx + 12, cy - 8), (cx + 9, cy + 7), (cx, cy + 14), (cx - 9, cy + 7), (cx - 12, cy - 8)]
        draw.polygon(shield, outline=color)
        draw.line((cx - 5, cy, cx - 1, cy + 5, cx + 7, cy - 5), fill=color, width=3)


def draw_takeaway(draw, pillar_key, visual_spec=None):
    benefits = []
    if isinstance(visual_spec, dict):
        benefits = [
            (item.get("icon", "eye"), item.get("label", ""), item.get("description", ""))
            for item in visual_spec.get("takeaways", [])
            if isinstance(item, dict)
        ]
    if not benefits:
        benefits = PILLAR_BENEFITS.get(pillar_key)
    if not benefits:
        return
    # The opaque panel begins above the illustration's lower safe zone so
    # generated objects can never intrude into the takeaway/brand area.
    draw.rounded_rectangle((48, 1190, 1152, 1364), radius=20, fill=(10, 11, 13, 255), outline=SITE_BORDER, width=2)
    label_font = ImageFont.truetype(FONT_BOLD, 14)
    draw.text((72, 1214), "NEDEN ÖNEMLİ?", font=label_font, fill=SITE_ACCENT, anchor="lm")
    draw.line((198, 1214, 1128, 1214), fill=SITE_BORDER, width=1)
    count = min(max(len(benefits), 3), 4)
    gap = 12
    total_width = 1080
    card_width = (total_width - gap * (count - 1)) // count
    for index, (icon, title, detail) in enumerate(benefits[:count]):
        x1 = 60 + index * (card_width + gap)
        x2 = x1 + card_width
        draw.rounded_rectangle((x1, 1226, x2, 1350), radius=15, fill=SITE_SURFACE_2, outline=SITE_BORDER, width=1)
        draw_icon(draw, icon, x1 + 32, 1288)
        text_width = card_width - 76
        title = turkish_upper(title)
        title_font = fit_font(draw, title, text_width, 15, 11, FONT_BOLD)
        draw.text((x1 + 62, 1270), title, font=title_font, fill=SITE_TEXT, anchor="lm")
        detail_font = fit_font(draw, detail, text_width, 13, 10, FONT_REGULAR)
        detail_lines = wrap_lines(draw, detail, detail_font, text_width)[:2]
        for line_index, line in enumerate(detail_lines):
            draw.text((x1 + 62, 1300 + line_index * 16), line, font=detail_font, fill=SITE_MUTED, anchor="lm")


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


def draw_brand_footer(canvas):
    vertical_gradient(canvas, (22, 31, 28), (10, 11, 13), 1392, 1500)
    draw = ImageDraw.Draw(canvas)
    draw.line((0, 1392, 1200, 1392), fill=SITE_ACCENT, width=3)
    if LOGO_PATH.is_file():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        content_box = logo.getbbox()
        if content_box:
            logo = logo.crop(content_box)
        logo.thumbnail((54, 54), Image.Resampling.LANCZOS)
        draw.rounded_rectangle((54, 1410, 126, 1482), radius=20, fill=SITE_SURFACE_2, outline=SITE_ACCENT, width=2)
        canvas.alpha_composite(logo, (90 - logo.width // 2, 1446 - logo.height // 2))
    brand_font = ImageFont.truetype(FONT_BOLD, 25)
    draw.text((146, 1433), "Emre Çancıoğlu", font=brand_font, fill=SITE_TEXT, anchor="lm")
    tagline_font = ImageFont.truetype(FONT_REGULAR, 15)
    draw.text((147, 1466), "emrecancioglu.com  •  OT  •  IIoT  •  Endüstriyel AI", font=tagline_font, fill=SITE_MUTED, anchor="lm")

    draw.rounded_rectangle((830, 1417, 1146, 1475), radius=29, fill=(15, 57, 45, 255), outline=SITE_ACCENT, width=2)
    badge_font = ImageFont.truetype(FONT_BOLD, 13)
    draw.ellipse((852, 1440, 862, 1450), fill=SITE_ACCENT)
    draw.text((878, 1446), "DAHA FAZLA TEKNİK İÇERİK  →", font=badge_font, fill=SITE_TEXT, anchor="lm")


def refresh_text_overlays(post_id, visual_spec):
    if not UUID_RE.fullmatch(post_id):
        raise ValueError("invalid post id")
    image_path = (CONTENT_ROOT / f"{post_id}.png").resolve()
    if image_path.parent != CONTENT_ROOT or not image_path.is_file():
        raise ValueError("image not found")
    canvas = Image.open(image_path).convert("RGBA")
    spec = normalize_visual_spec(visual_spec, "", "", "")
    draw = ImageDraw.Draw(canvas)
    stages = spec.get("stages", [])
    positions = stage_positions(len(stages), spec.get("layout_type", "process_flow"))
    for index, (stage, position) in enumerate(zip(stages, positions), start=1):
        side, y = position
        draw_callout(draw, side, y, stage.get("label", ""), stage.get("description", ""), number=index, state=stage.get("state", "normal"))
    draw_brand_footer(canvas)
    canvas.convert("RGB").save(image_path, "PNG", optimize=True)
    return str(image_path)


def render(post_id, title, points, body, pillar, visual_spec=None):
    if not UUID_RE.fullmatch(post_id):
        raise ValueError("invalid post id")
    image_path = (CONTENT_ROOT / f"{post_id}.png").resolve()
    if image_path.parent != CONTENT_ROOT or not image_path.is_file():
        raise ValueError("image not found")

    image = Image.open(image_path).convert("RGBA")
    already_branded = image.size == (1200, 1500)
    # Re-rendering a previously branded 4:5 preview reuses only its illustration.
    if already_branded:
        image = image.crop((30, 236, 1170, 1376))
    if image.size != (1200, 1200):
        image = image.resize((1200, 1200), Image.Resampling.LANCZOS)

    pillar_key = str(pillar or "")
    spec = normalize_visual_spec(visual_spec, title, body, pillar_key)
    concept = spec["technical_title"] or infographic_header(title, pillar_key)[0]
    expansion = spec["international_name"]
    subtitle = spec["curiosity_subtitle"] or infographic_header(title, pillar_key)[2]

    # Premium 4:5 LinkedIn canvas. The illustration remains in its own card;
    # all typography lives in dedicated header/footer areas.
    canvas = Image.new("RGBA", (1200, 1500), SITE_BG)
    vertical_gradient(canvas, (10, 11, 13), (14, 29, 25), 0, 230)
    draw = ImageDraw.Draw(canvas)
    draw.line((0, 228, 1200, 228), fill=SITE_ACCENT, width=3)

    concept_font = fit_font(draw, concept, 610, 38, 28, FONT_BOLD)
    expansion_text = f"({expansion})" if expansion else ""
    expansion_font = fit_font(draw, expansion_text, 440, 28, 19, FONT_BOLD)
    concept_width = draw.textbbox((0, 0), concept, font=concept_font)[2]
    expansion_width = draw.textbbox((0, 0), expansion_text, font=expansion_font)[2]
    heading_width = concept_width + (16 + expansion_width if expansion_text else 0)
    heading_x = (1200 - heading_width) / 2
    draw.text((heading_x, 65), concept, font=concept_font, fill=SITE_ACCENT, anchor="lm")
    if expansion_text:
        draw.text((heading_x + concept_width + 16, 65), expansion_text, font=expansion_font, fill=SITE_TEXT, anchor="lm")

    subtitle = turkish_upper(subtitle)
    subtitle_font = fit_font(draw, subtitle, 820, 18, 13, FONT_BOLD)
    subtitle_width = draw.textbbox((0, 0), subtitle, font=subtitle_font)[2]
    subtitle_y = 145
    left_end = max(70, 600 - subtitle_width / 2 - 28)
    right_start = min(1130, 600 + subtitle_width / 2 + 28)
    draw.line((54, subtitle_y, left_end, subtitle_y), fill=SITE_ACCENT, width=2)
    draw.ellipse((left_end - 4, subtitle_y - 4, left_end + 4, subtitle_y + 4), fill=SITE_ACCENT)
    draw.line((right_start, subtitle_y, 1146, subtitle_y), fill=SITE_ACCENT, width=2)
    draw.ellipse((right_start - 4, subtitle_y - 4, right_start + 4, subtitle_y + 4), fill=SITE_ACCENT)
    draw.text((600, subtitle_y), subtitle, font=subtitle_font, fill=SITE_TEXT, anchor="mm")

    # Framed illustration card with a restrained shadow and no text overlay.
    draw.rounded_rectangle((24, 242, 1184, 1402), radius=32, fill=(5, 6, 8, 255))
    card = rounded_image(image, 1140, 28)
    canvas.alpha_composite(card, (30, 236))
    draw.rounded_rectangle((30, 236, 1170, 1376), radius=28, outline=SITE_BORDER, width=2)
    stages = spec.get("stages", [])
    positions = stage_positions(len(stages), spec.get("layout_type", "process_flow"))
    for index, (stage, position) in enumerate(zip(stages, positions), start=1):
        side, y = position
        draw_callout(draw, side, y, stage.get("label", ""), stage.get("description", ""), number=index, state=stage.get("state", "normal"))
    draw_takeaway(draw, pillar_key, spec)

    # High-impact brand signature in its own footer band.
    draw_brand_footer(canvas)

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
            visual_spec = payload.get("visual_spec", {})
            path = render(payload.get("post_id", ""), payload.get("title", ""), payload.get("points", []), payload.get("body", ""), payload.get("pillar", ""), visual_spec)
            normalized = normalize_visual_spec(visual_spec, payload.get("title", ""), payload.get("body", ""), payload.get("pillar", ""))
            body = json.dumps({"ok": True, "image_path": path, "layout_type": normalized.get("layout_type"), "stage_count": len(normalized.get("stages", [])), "takeaway_count": len(normalized.get("takeaways", []))}).encode()
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


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8081), Handler).serve_forever()
