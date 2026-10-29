CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS evidence_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    kind text NOT NULL CHECK (kind IN ('real_work', 'lab_demo', 'lesson', 'opinion', 'publication')),
    title text NOT NULL,
    situation text NOT NULL DEFAULT '',
    action_text text NOT NULL DEFAULT '',
    result_text text,
    source_ref text,
    proof_level text NOT NULL CHECK (proof_level IN ('verified', 'self_reported', 'demo', 'idea')),
    confidentiality text NOT NULL CHECK (confidentiality IN ('public', 'anonymize', 'private')),
    approved_claims jsonb NOT NULL DEFAULT '[]'::jsonb,
    tags text[] NOT NULL DEFAULT '{}',
    status text NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'reserved', 'used', 'blocked')),
    used_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS content_posts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id uuid REFERENCES evidence_items(id) ON DELETE SET NULL,
    pillar text NOT NULL,
    hook text NOT NULL,
    body text NOT NULL,
    cta text NOT NULL DEFAULT '',
    hashtags text[] NOT NULL DEFAULT '{}',
    image_brief text NOT NULL DEFAULT '',
    image_prompt text,
    image_path text,
    risk_flags text[] NOT NULL DEFAULT '{}',
    approval_status text NOT NULL DEFAULT 'draft'
        CHECK (approval_status IN ('draft', 'blocked', 'needs_review', 'regenerating_text', 'regenerating_both', 'approved', 'publishing', 'rejected', 'published')),
    reviewer_notes text,
    scheduled_at timestamptz,
    approved_at timestamptz,
    published_at timestamptz,
    linkedin_post_urn text UNIQUE,
    text_model text,
    image_model text,
    openai_response_id text,
    token_usage jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS claim_map (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id uuid NOT NULL REFERENCES content_posts(id) ON DELETE CASCADE,
    evidence_id uuid REFERENCES evidence_items(id) ON DELETE SET NULL,
    claim_text text NOT NULL,
    allowed boolean NOT NULL DEFAULT false,
    reason text NOT NULL DEFAULT '',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS post_metrics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id uuid NOT NULL REFERENCES content_posts(id) ON DELETE CASCADE,
    measured_on date NOT NULL DEFAULT current_date,
    impressions integer,
    reactions integer,
    comments integer,
    reposts integer,
    profile_views integer,
    qualified_connections integer,
    notes text,
    UNIQUE (post_id, measured_on)
);

CREATE TABLE IF NOT EXISTS system_events (
    id bigserial PRIMARY KEY,
    event_type text NOT NULL,
    entity_type text,
    entity_id uuid,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS telegram_bot_state (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    update_offset bigint NOT NULL DEFAULT 0,
    paired_chat_id bigint UNIQUE,
    paired_username text,
    paired_at timestamptz,
    updated_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO telegram_bot_state (singleton)
VALUES (true)
ON CONFLICT (singleton) DO NOTHING;

CREATE TABLE IF NOT EXISTS telegram_review_deliveries (
    post_id uuid NOT NULL REFERENCES content_posts(id) ON DELETE CASCADE,
    post_updated_at timestamptz NOT NULL,
    chat_id bigint NOT NULL,
    photo_message_id bigint,
    text_message_id bigint,
    sent_at timestamptz NOT NULL DEFAULT now(),
    action text,
    action_at timestamptz,
    PRIMARY KEY (post_id, post_updated_at)
);

CREATE INDEX IF NOT EXISTS idx_evidence_status_created
    ON evidence_items (status, created_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_evidence_title_source_unique
    ON evidence_items (title, source_ref);
CREATE INDEX IF NOT EXISTS idx_posts_approval_created
    ON content_posts (approval_status, created_at);
CREATE INDEX IF NOT EXISTS idx_claim_map_post
    ON claim_map (post_id);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS evidence_items_set_updated_at ON evidence_items;
CREATE TRIGGER evidence_items_set_updated_at
BEFORE UPDATE ON evidence_items
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS content_posts_set_updated_at ON content_posts;
CREATE TRIGGER content_posts_set_updated_at
BEFORE UPDATE ON content_posts
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE VIEW draft_review_queue AS
SELECT
    p.id AS post_id,
    p.created_at,
    p.approval_status,
    p.pillar,
    p.hook,
    p.body,
    p.cta,
    p.hashtags,
    p.image_path,
    p.risk_flags,
    e.title AS evidence_title,
    e.kind AS evidence_kind,
    e.proof_level,
    e.confidentiality
FROM content_posts p
LEFT JOIN evidence_items e ON e.id = p.evidence_id
WHERE p.approval_status IN ('draft', 'blocked', 'needs_review', 'approved')
ORDER BY p.created_at DESC;
