INSERT INTO evidence_items
    (kind, title, situation, action_text, result_text, source_ref, proof_level,
     confidentiality, approved_claims, tags)
VALUES
(
    'publication',
    'Akü üretiminde enerji tüketimi tahmini',
    'Üretim planlarına bağlı elektrik ve basınçlı hava tüketiminin öngörülmesi.',
    'XGBoost, LightGBM ve GBM regresyon modelleriyle kısa vadeli tahminleme.',
    'Yayınlanan çalışmada R2 değeri 0.944 seviyesine kadar ulaştı.',
    'resume_tr.pdf - Sunumlar ve Yayınlar; 13th International European Conference on Interdisciplinary Scientific Research, Mayıs 2026',
    'verified', 'public',
    '["Akü üretim hatlarında elektrik ve basınçlı hava tüketimini tahminleyen modeller geliştirdim.", "Kısa vadeli tahminlerde R2 değeri 0.944 seviyesine kadar ulaştı."]'::jsonb,
    ARRAY['enerji', 'makine-ogrenmesi', 'xgboost', 'surdurulebilirlik']
),
(
    'publication',
    'UNS tabanlı Endüstri 4.0 veri entegrasyonu',
    'Saha sistemleri arasında parçalı ve noktadan noktaya veri akışı.',
    'MQTT, OPC UA ve Node.js ile Unified Namespace yaklaşımının ele alınması.',
    'Çalışma R&D & Innovation 2024 kapsamında sunuldu.',
    'resume_tr.pdf - R&D & Innovation 2024, Aralık 2024',
    'verified', 'public',
    '["MQTT, OPC UA ve Node.js ile Unified Namespace tabanlı dijital dönüşüm üzerine bir çalışma sundum."]'::jsonb,
    ARRAY['uns', 'mqtt', 'opc-ua', 'iiot']
),
(
    'publication',
    'Tennessee Eastman prosesinde hata teşhisi',
    'Proses kontrol sistemlerinde arızaların ölçümlerden sınıflandırılması.',
    'Poincare grafiği ölçüleri ve ensemble learning algoritmaları kullanıldı.',
    'Tennessee Eastman sürecinde sınıflandırma doğruluğu yüzde 89,5 seviyesine ulaştı.',
    'resume_tr.pdf - Human-Computer Interaction Optimization and Robotic Applications, Haziran 2021',
    'verified', 'public',
    '["Poincare grafiği ölçüleri ve ensemble learning yöntemleriyle proses hata teşhisi üzerine çalıştım.", "Tennessee Eastman sürecindeki sınıflandırma doğruluğu yüzde 89,5 seviyesine ulaştı."]'::jsonb,
    ARRAY['proses-kontrol', 'anomali', 'makine-ogrenmesi']
),
(
    'real_work',
    'OT veri mimarisinde Unified Namespace yaklaşımı',
    'PLC, SCADA, MES ve kurumsal sistemler arasında ölçeklenen veri entegrasyonu ihtiyacı.',
    'OPC UA, MQTT ve Kafka temelli bir veri omurgası ve standart isimlendirme yaklaşımı uygulandı.',
    NULL,
    'resume_tr.pdf - Kıdemli Operasyonel Teknolojiler Mühendisi deneyimi',
    'self_reported', 'anonymize',
    '["Üretim sistemlerinin entegrasyonunda Unified Namespace yaklaşımını uyguladım."]'::jsonb,
    ARRAY['uns', 'ot', 'isa-95', 'veri-mimarisi']
),
(
    'real_work',
    'OPC UA tabanlı kendi kendine servis alarm yaklaşımı',
    'Bağlı makineler için alarm tanımlamanın merkezi ekibe bağımlı olması.',
    'Kullanıcıların bağlı makineler için gerçek zamanlı özel alarm tanımlayabildiği OPC UA tabanlı yaklaşım geliştirildi.',
    NULL,
    'resume_tr.pdf - Dijitalleşme ve Yapay Zeka Ekip Lideri deneyimi',
    'self_reported', 'anonymize',
    '["OPC UA tabanlı, kullanıcıların kendi alarmlarını tanımlayabildiği bir yaklaşım geliştirdim."]'::jsonb,
    ARRAY['opc-ua', 'alarm', 'self-service', 'ot']
),
(
    'real_work',
    'Basınçlı hava kaçağı anomali tespiti',
    'Basınçlı hava kaçaklarının üretim bağlamından kopuk değerlendirilmesi.',
    'Kompresör, MES ve üretim teyit verileri birleştirilerek anomali tespiti geliştirildi.',
    'Erken müdahaleyi destekleyen bir izleme yaklaşımı oluşturuldu.',
    'resume_tr.pdf - Dijitalleşme ve Yapay Zeka Ekip Lideri deneyimi',
    'self_reported', 'anonymize',
    '["Basınçlı hava, MES ve üretim teyit verilerini birleştiren bir anomali tespit yaklaşımı geliştirdim."]'::jsonb,
    ARRAY['enerji', 'anomali', 'mes', 'basincli-hava']
),
(
    'real_work',
    'OT ağ segmentasyonu ve IEC 62443 yaklaşımı',
    'Üretim sürekliliği ile veri güvenliğinin birlikte korunması.',
    'ISA-95/Purdue katmanları, VLAN, NAT ve endüstriyel firewall kuralları uygulandı.',
    NULL,
    'resume_tr.pdf - Kıdemli Operasyonel Teknolojiler Mühendisi deneyimi',
    'self_reported', 'anonymize',
    '["OT ağ tasarımında Purdue modeli, VLAN, NAT ve endüstriyel firewall yaklaşımlarını birlikte kullandım."]'::jsonb,
    ARRAY['iec-62443', 'purdue', 'vlan', 'ot-security']
),
(
    'real_work',
    'Enerji ölçüm altyapısı ve ISO 50001 hazırlığı',
    'Makine bazlı enerji tüketimi ve karbon etkisinin izlenmesi.',
    'Elektrik, su ve doğal gaz ölçümleri tarihsel üretim verisiyle birleştirildi ve dashboard oluşturuldu.',
    NULL,
    'resume_tr.pdf - Dijitalleşme ve Yapay Zeka Ekip Lideri deneyimi',
    'self_reported', 'anonymize',
    '["Enerji ölçümlerini üretim verisiyle birleştiren makine bazlı bir izleme yaklaşımı geliştirdim."]'::jsonb,
    ARRAY['iso-50001', 'enerji', 'karbon', 'dashboard']
),
(
    'real_work',
    'Bilgisayarlı görü ile endüstriyel güvenlik',
    'Robot alanları ve kör noktalarda insan-makine etkileşim riskleri.',
    'YOLO tabanlı algılama modelleri gerçek zamanlı uyarı ve durdurma mekanizmalarıyla entegre edildi.',
    NULL,
    'resume_tr.pdf - Dijitalleşme ve Yapay Zeka Ekip Lideri deneyimi',
    'self_reported', 'anonymize',
    '["YOLO tabanlı güvenlik modellerini gerçek zamanlı uyarı ve durdurma mekanizmalarıyla entegre ettim."]'::jsonb,
    ARRAY['yolo', 'bilgisayarli-goru', 'is-guvenligi', 'edge-ai']
),
(
    'lesson',
    'Üretimde GenAI projesi seçme çerçevesi',
    'Her süreç GenAI için uygun değildir; veri, risk ve ölçülebilir değer birlikte değerlendirilmelidir.',
    'Problemi tekrarlanabilirlik, veri erişimi, hata maliyeti ve insan onayı açısından değerlendiren bir kontrol listesi.',
    NULL,
    'Uzmanlık alanı ve kamuya açık CV özeti',
    'idea', 'public',
    '[]'::jsonb,
    ARRAY['genai', 'proje-secimi', 'roi', 'yonetisim']
),
(
    'lesson',
    'UNS ve point-to-point entegrasyon karşılaştırması',
    'Noktadan noktaya entegrasyonlar büyüdükçe bakım maliyeti ve semantik tutarsızlık artar.',
    'Aynı örnek üretim sinyalini iki mimariyle karşılaştıran teknik öğretici.',
    NULL,
    'Uzmanlık alanı ve kamuya açık yayın',
    'idea', 'public',
    '[]'::jsonb,
    ARRAY['uns', 'point-to-point', 'iiot', 'mimari']
),
(
    'lab_demo',
    'Yerel MQTT verisinde anomali tespiti demosu',
    'Gerçek tesis verisi kullanmadan uçtan uca veri akışını göstermek.',
    'Sentetik sensör verisi MQTT ile yayınlanır; hareketli eşik veya Isolation Forest ile anomali işaretlenir.',
    'Sonuçlar yalnızca yerel demo sonucu olarak paylaşılacaktır.',
    'Planlanan tekrar üretilebilir yerel demo',
    'demo', 'public',
    '["Gerçek tesis verisi kullanmadan, sentetik MQTT verisiyle yerel bir anomali tespiti demosu hazırladım."]'::jsonb,
    ARRAY['mqtt', 'demo', 'anomali', 'python']
)
ON CONFLICT (title, source_ref) DO NOTHING;
