ALTER TABLE content_posts
    DROP CONSTRAINT IF EXISTS content_posts_approval_status_check;

ALTER TABLE content_posts
    ADD CONSTRAINT content_posts_approval_status_check
    CHECK (approval_status IN (
        'draft',
        'blocked',
        'needs_review',
        'regenerating_text',
        'regenerating_both',
        'approved',
        'publishing',
        'rejected',
        'published'
    ));

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

CREATE INDEX IF NOT EXISTS idx_telegram_review_pending
    ON content_posts (updated_at)
    WHERE approval_status = 'needs_review'
      AND image_path IS NOT NULL;
