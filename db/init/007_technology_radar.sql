CREATE TABLE IF NOT EXISTS radar_items (
    id bigserial PRIMARY KEY,
    source text NOT NULL,
    source_id text NOT NULL,
    title text NOT NULL,
    summary text NOT NULL DEFAULT '',
    url text NOT NULL,
    published_at timestamptz,
    category text NOT NULL,
    relevance_score integer NOT NULL DEFAULT 0,
    urgency_score integer NOT NULL DEFAULT 0,
    status text NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'selected', 'used', 'rejected')),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source, source_id),
    UNIQUE (url)
);

CREATE TABLE IF NOT EXISTS evergreen_topics (
    id bigserial PRIMARY KEY,
    pillar text NOT NULL,
    format text NOT NULL CHECK (format IN ('architecture', 'comparison', 'problem_solution', 'checklist', 'opinion')),
    title text NOT NULL UNIQUE,
    angle text NOT NULL,
    last_used_at timestamptz,
    active boolean NOT NULL DEFAULT true
);

INSERT INTO evergreen_topics (pillar, format, title, angle) VALUES
('OT_VERI_MIMARISI','architecture','Unified Namespace neden yalnızca bir MQTT broker değildir?','UNS yaklaşımını topic yapısı, veri sahipliği, isimlendirme standardı ve yönetişim açısından açıkla.'),
('OT_VERI_MIMARISI','comparison','OPC UA ve MQTT aynı problemin rakip çözümleri mi?','İki teknolojiyi rakip gibi değil tamamlayıcı katmanlar olarak karşılaştır.'),
('ENDUSTRIYEL_AI','problem_solution','Endüstriyel yapay zekâ projeleri neden pilotta kalır?','Veri kalitesi, süreç sahipliği, entegrasyon ve operasyonel benimseme sorunlarını çözüm önerileriyle ele al.'),
('ENDUSTRIYEL_AI','checklist','Üretimde anomali tespiti için başlamadan önce sorulacak 7 soru','Modelden önce sinyal kalitesi, etiket, yanlış alarm maliyeti ve aksiyon sürecini sorgula.'),
('URETIMDE_GENAI','architecture','Agentic AI sistemlerinde yetki sınırı nasıl tasarlanmalı?','Araç erişimi, minimum yetki, onay kapıları, gözlemlenebilirlik ve geri alma mekanizmasını tartış.'),
('URETIMDE_GENAI','comparison','RAG, fine-tuning ve agentic workflow ne zaman kullanılmalı?','Üretim bilgisi senaryolarında üç yaklaşımın güçlü ve zayıf yanlarını karşılaştır.'),
('OT_SIBER_GUVENLIK','architecture','Düz bir OT ağından katmanlı mimariye geçiş','Segmentasyon, erişim kontrolü, sıçrama sunucusu ve izleme katmanlarını örnek senaryo üzerinden açıkla.'),
('OT_SIBER_GUVENLIK','problem_solution','OT güvenliğinde CVSS neden tek başına yeterli değildir?','Sömürülebilirlik, varlık kritiklik değeri, maruziyet ve üretim etkisini birlikte ele al.'),
('ENERJI_SURDURULEBILIRLIK','problem_solution','Enerji izleme projesi neden sadece sayaç toplamaktan ibaret değildir?','Bağlam, üretim miktarı, ürün reçetesi, vardiya ve baz yük ilişkisini açıkla.'),
('ENERJI_SURDURULEBILIRLIK','checklist','Üretim hattında enerji baz çizgisi oluşturma kontrol listesi','Veri çözünürlüğü, normalizasyon, duruşlar ve mevsimsellik başlıklarını işle.'),
('TEKNIK_LIDERLIK','opinion','Teknik borç ile operasyonel risk arasındaki görünmeyen bağ','Bakım ertelenmesi, entegrasyon kırılganlığı ve bilgi tekelleşmesini teknik liderlik açısından tartış.'),
('TEKNIK_LIDERLIK','comparison','Merkezi standart mı, tesis özgürlüğü mü?','Endüstriyel dijital dönüşümde platform standardizasyonu ile yerel çevikliği dengele.')
ON CONFLICT (title) DO NOTHING;

CREATE INDEX IF NOT EXISTS idx_radar_queue ON radar_items (status, relevance_score DESC, urgency_score DESC, published_at DESC);
