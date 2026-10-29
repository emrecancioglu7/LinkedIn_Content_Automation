ALTER TABLE content_posts
    ADD COLUMN IF NOT EXISTS image_title text NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS image_points text[] NOT NULL DEFAULT '{}';
