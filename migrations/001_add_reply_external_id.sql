-- Migration 001: Add reply_external_id to platform_posts
-- Sprint 4E: Threads RU Reply Orchestration
-- Applied: 2026-03-24

ALTER TABLE content.platform_posts
ADD COLUMN IF NOT EXISTS reply_external_id TEXT;

COMMENT ON COLUMN content.platform_posts.reply_external_id
IS 'External ID of the reply post (e.g. Threads reply). Set by Publisher Service after successful reply publication.';
