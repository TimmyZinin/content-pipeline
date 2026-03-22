# Changelog

> Лог изменений Content Pipeline v2. Новые записи — сверху.

---

## 2026-03-22 | CTA/Link Placement Audit + Incident Containment
- /test-publish DISABLED (HTTP 403) — was publishing to real accounts
- Strategy audit: CTA placement matrix for all platforms (new doc: CTA-Placement.md)
- Root cause: Publisher Service passes link_url to adapters but adapters ignore it
- Etap 1 code (body links) written in Publisher Service but NOT verified live
- Etap 2 (comment/reply post-publish) identified as gap, NOT implemented
- Data model sufficient — no schema changes needed
- LinkedIn CTA design deferred to Sprint 4G

## 2026-03-22 | Sprint 4C: Text Coverage Completion
- Bluesky: text verified (5/5 tests), image blocked (blob >1MB, platform limit)
- Write.as: ✅ working, verified via /test-publish
- Minds: ✅ working, verified via /test-publish
- Nostr: ✅ working, verified via /test-publish (websocket-client + coincurve installed)
- Tumblr: ❌ blocked (401 Unauthorized — OAuth tokens expired/invalid)
- Mastodon: ❌ blocked (401 Unauthorized — access token invalid)
- Tumblr adapter rewritten as proper module (was standalone script)
- Docker deps: +pytumblr +coincurve +websocket-client
- .env mounted into Docker for adapters that read credentials from file

Final text publish map:
- Working (10): Telegram, Dev.to, VK, Threads RU, Hashnode, Facebook, Threads EN, Write.as, Minds, Nostr
- Partial: Bluesky (text ok, image >1MB blocked)
- Blocked: Tumblr (401), Mastodon (401)
- Separate path: LinkedIn

## 2026-03-22 | Sprint 4B.1: Verification Truth Pass
- Facebook via Publer: TEXT ONLY verified. Image NOT transmitted (verified by Tim in Publer app)
- Threads EN via Publer: TEXT ONLY verified. Image NOT transmitted (verified by Tim in Threads app)
- Publer media: simple `media: [{url: "..."}]` does NOT work. Publer requires pre-uploaded media IDs
- Bluesky: 1 successful text test, not a series. Honest confidence: partial
- Publer integration: User-Agent fix, correct endpoint /posts/schedule/publish + Publer-Workspace-Id
- LinkedIn: separate standalone pipeline (/opt/linkedin-pipeline/), not migrated into Publisher v3
- Mastodon: token invalid. Deferred

Honest platform status after media fix:
- Full (text+image, verified by Tim): Telegram, Dev.to, VK, Threads RU, Hashnode, Facebook (Publer), Threads EN (Publer) (7)
- Partial: Bluesky (1 test) (1)
- Not working: LinkedIn, Mastodon (2)
- Publer media fix: 2-step upload via POST /media/from-url → get media_id → reference in post with type:"photo"
- Root cause of initial failure: Publer ignores inline media URLs, requires pre-uploaded media IDs

## 2026-03-22 | Sprint 4B checkpoint: Anti-duplicate + Verify + Observer
- Anti-duplicate guard: atomic lock (status='sending'), rejects sent/verified/published (400/409)
- /verify endpoint: TG (trusted), Dev.to (API GET), VK (API wall.getById), Threads RU (Graph API), Hashnode (trusted), Bluesky (trusted)
- Bluesky: 1 successful test (adapter works), previous 400 was text truncation. Needs more testing for confidence
- Observer cards: +Sent, +Verified alongside Published* (legacy)
- Observer Publication Log: shows sent/verified/failed with external IDs and errors
- Status model: scheduled → sending (lock) → sent (API ok) → verified (read-back) / failed (3 retry)
- sending status = atomic anti-duplicate guard, not a long-lived state
- Publisher Service redeployed: post_external_id in SELECT, /verify endpoint
- Docs updated: Publisher.md, Database.md, Workflows.md, Changelog.md

## 2026-03-22 | Sprint 4A: Publisher Refactor
- Python Publisher Service deployed (Docker :8086, FastAPI)
- Reads platform_post by ID from DB, calls auto-publisher adapters
- Publisher v3 (ErbbScuvxWHLX1np): 7 n8n nodes, replaces v2
- Old Publisher v2 (1cD3qXs2XZkgcQyt) DEACTIVATED
- Status model: scheduled → sent (API ok) / failed (retry 3x, TG alert)
- Verified platforms: Telegram, Dev.to, VK, Threads RU, Hashnode (5/5)
- Bluesky: known adapter bug (apostrophes), deferred to 4B
- Observer: Publication Log section added (sent/failed with details)
- INCIDENT: duplicate posts to TG and LinkedIn caused by manual /publish without status update. Fixed: v2 deactivated, v3 updates status. Rule: no manual curl /publish on prod scheduled posts.

## 2026-03-22 | Reconciliation Pass
- docs/Home.md: добавлен Observer, policies (SoT, timezone, DoD), связанные репо
- docs/Workflows.md: добавлен Observer workflow (#9) с описанием секций
- docs/Platforms.md: добавлены 4 новые платформы (writeas/tumblr/minds/nostr), обновлены статусы
- docs/Changelog.md: добавлены записи Sprint 3
- SESSION_HANDOFF.md: помечен как legacy
- Timezone policy: storage=UTC, display=Istanbul (UTC+3)
- docs/ = source of truth, wiki = mirror

## 2026-03-22 | Спринт 3 Curator+: Полнота + Observability
- CUR-11: +4 платформы в Adapter + Curator (writeas, tumblr, minds, nostr)
- CUR-12: TG сводка после Curator с ссылкой на Observer (ежедневно 04:30 MSK)
- CUR-13: Observer: секция Pipeline Health (статус каждого workflow за 24ч)
- CUR-14: Конфиг в JSON (/opt/content-pipeline/curator-config.json, 14 платформ)
- CUR-15: Fallback alert при 0 draft постов → TG уведомление
- CUR-16: Observer ссылки на corp.timzinin.com (sidebar + content-calendar)
- CUR-17: Override кнопки — отложено в конец бэклога
- Observer workflow (V2wnna7ACw5iSqdi): Pipeline Health, Platform Summary, Schedule, Recent Published

## 2026-03-22 | Спринт 2 Curator: Smart Scheduling
- Дедупликация по topic_cluster (3-дневное окно)
- Fresh посты приоритетнее stale
- Curator Preview workflow (JzYcKrUfXheatEi1) — dry-run без изменения БД
- Dashboard: +2 стата (Назначено, Пропущено)
- Dashboard SQL: platform_scheduled, platform_skipped

## 2026-03-22 | Спринт 1 Curator: MVP
- Создан n8n workflow "Curator — Куратор" (EYPcT5B4rLmQRQBM)
- Cron 04:30 MSK (после Adapter 04:00)
- Tier-система: T1 ежедневно, T2 ПН/СР/ПТ, T3 только ПН
- Quality-based selection: лучшие по score → приоритетным платформам
- Stagger scheduling: Dubai UTC+4
- Publisher SQL обновлён: WHERE status='scheduled' AND scheduled_at <= NOW()
- Тест: 14 scheduled, 26 skipped (суббота)

## 2026-03-22 | Publisher v2
- Создан Publisher v2 workflow (1cD3qXs2XZkgcQyt)
- 10 нод, cron */30 06-21 MSK
- Верифицированы: Telegram ✅, Dev.to ✅
- Деактивированы: LinkedIn Pipeline v3, Threads News

## 2026-03-21 | Adapter workflow
- Создан Adapter workflow (NJoPcdp38ZU0dQwG), cron 04:00
- 10 платформ: TG, LI, Threads RU/EN, VK, Bluesky, FB, Mastodon, Dev.to, Hashnode
- Составные сущности: post_text + comment_text + reply_text + link_url
- ALTER TABLE platform_posts: +5 столбцов
- Dashboard обновлён: секция "Расписание публикаций"

## 2026-03-21 | Publer API + стратегии
- Publer API key получен (de555d3f...)
- 3 аккаунта: Facebook, Threads EN, TikTok
- Обновлены 16 стратегий в smm-research-hub

## 2026-03-20 | Первый запуск
- Scout, Writer, Illustrator, Dashboard — все active
- PostgreSQL schema content создана
- Gemini Image Service (Docker :8800)
- GitHub Pages: timzinin.com/content-pipeline/
- Первые 10 постов с pop-art картинками
