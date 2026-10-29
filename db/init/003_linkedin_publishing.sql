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

CREATE INDEX IF NOT EXISTS idx_posts_due_for_linkedin
    ON content_posts (scheduled_at)
    WHERE approval_status = 'approved'
      AND linkedin_post_urn IS NULL;
