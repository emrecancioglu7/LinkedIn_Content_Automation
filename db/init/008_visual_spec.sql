ALTER TABLE content_posts
    ADD COLUMN IF NOT EXISTS visual_spec jsonb NOT NULL DEFAULT '{}'::jsonb;

CREATE INDEX IF NOT EXISTS idx_posts_visual_layout
    ON content_posts ((visual_spec->>'layout_type'));
