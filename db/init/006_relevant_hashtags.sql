CREATE OR REPLACE FUNCTION set_relevant_hashtags()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.hashtags := CASE NEW.pillar
        WHEN 'OT_VERI_MIMARISI' THEN ARRAY['#DigitalTransformation', '#IIoT', '#IndustrialAutomation']
        WHEN 'ENDUSTRIYEL_AI' THEN ARRAY['#ArtificialIntelligence', '#IndustrialAI', '#Manufacturing']
        WHEN 'ENERJI_SURDURULEBILIRLIK' THEN ARRAY['#Sustainability', '#EnergyManagement', '#Manufacturing']
        WHEN 'URETIMDE_GENAI' THEN ARRAY['#GenerativeAI', '#ArtificialIntelligence', '#Manufacturing']
        WHEN 'OT_SIBER_GUVENLIK' THEN ARRAY['#CyberSecurity', '#OTSecurity', '#IEC62443']
        WHEN 'TEKNIK_LIDERLIK' THEN ARRAY['#Leadership', '#EngineeringLeadership', '#DigitalTransformation']
        ELSE NEW.hashtags
    END;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS content_posts_relevant_hashtags ON content_posts;
CREATE TRIGGER content_posts_relevant_hashtags
BEFORE INSERT OR UPDATE OF pillar, hashtags ON content_posts
FOR EACH ROW EXECUTE FUNCTION set_relevant_hashtags();

UPDATE content_posts SET hashtags = hashtags
WHERE approval_status <> 'published';
