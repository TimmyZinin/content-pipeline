# Live SQL Snippets

> Versioned copy of critical SQL from n8n workflows.
> If n8n UI diverges from this file — this file is the intended state.

## Publisher v3 — Select Scheduled (with allowlist)

**n8n workflow:** ErbbScuvxWHLX1np
**Status ownership:** Publisher Service writes sent/failed. n8n "Check Result" node = pass-through only.
**Node "Select Scheduled":**

```sql
SELECT id, platform, substring(adapted_text for 80) as preview
FROM content.platform_posts
WHERE status = 'scheduled'
  AND scheduled_at <= NOW()
  AND platform IN ('telegram','writeas','minds')
ORDER BY scheduled_at
LIMIT 1;
```

**To expand allowlist:** add platform names to IN clause + update PUBLISH_ALLOWLIST env var on Contabo.

## Curator — Select Drafts

**n8n workflow:** EYPcT5B4rLmQRQBM, node "Получить draft посты"

```sql
SELECT pp.id, pp.post_id, pp.platform, pp.adapted_text, pp.char_count,
  pp.comment_text, pp.reply_text, pp.link_url, pp.link_placement,
  pp.include_image, pp.image_url, pp.status,
  p.quality_score, p.topic_cluster,
  (SELECT COUNT(*) FROM content.platform_posts pp2
   JOIN content.posts p2 ON p2.id = pp2.post_id
   WHERE pp2.platform = pp.platform
     AND pp2.status = 'published'
     AND p2.topic_cluster = p.topic_cluster
     AND pp2.published_at > NOW() - INTERVAL '3 days'
  ) AS recent_same_cluster
FROM content.platform_posts pp
JOIN content.posts p ON p.id = pp.post_id
WHERE pp.status = 'draft'
ORDER BY p.quality_score DESC, pp.post_id DESC;
```
