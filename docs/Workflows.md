# Workflows (n8n)

> Все workflows на Contabo VPS 30, n8n.timzinin.com

## Активные workflows

| # | Workflow | n8n ID | Cron | Статус |
|---|---------|--------|------|--------|
| 1 | Scout — Разведка | RSQALdJch4WYZfit | каждые 6ч (05:00 Istanbul) | ✅ Active |
| 2 | Writer — Автор | ZQtg31g6dzAV0lXX | 06:00 Istanbul | ✅ Active |
| 3 | Illustrator — Художник | Z94O5uyaFEmrYGIJ | 06:30 Istanbul | ✅ Active |
| 4 | Adapter — Адаптер | NJoPcdp38ZU0dQwG | 07:00 Istanbul | ✅ Active |
| 5 | Curator — Куратор | EYPcT5B4rLmQRQBM | 07:30 Istanbul | ✅ Active |
| 6 | Publisher v3 | ErbbScuvxWHLX1np | */30 09:00-03:00 Istanbul | ✅ Active (10 working, 2 blocked, 1 partial) |
| 7 | Dashboard — Дашборд | DC3a34HOedbU7rVb | webhook | ✅ Active |
| 8 | Curator Preview | JzYcKrUfXheatEi1 | webhook | ✅ Active |
| 9 | Observer — Наблюдатель | V2wnna7ACw5iSqdi | webhook | ✅ Active |

## Деактивированные

| Workflow | n8n ID | Причина |
|---------|--------|---------|
| LinkedIn Pipeline v3 (n8n) | umId4uV39dewR8Um | Деактивирован в n8n. LinkedIn живёт отдельным standalone pipeline (/opt/linkedin-pipeline/) |
| Threads News | JHZEnMf87VLN93pI | Заменён Publisher v3 |
| Publisher v2 | 1cD3qXs2XZkgcQyt | Заменён Publisher v3 (дубликаты, нет картинок) |

## Кнопочные workflows (ручной запуск)

| Workflow | n8n ID | Назначение |
|---------|--------|-----------|
| Запуск Scout | UR2KDwBOocF82mZ1 | Ручной запуск Scout |
| Запуск Writer | rejq5CSnMMqdt4Wz | Ручной запуск Writer |
| Запуск Illustrator | JLrN4a1uAuHEhdoH | Ручной запуск Illustrator |
| Запуск Adapter | RjCOikDrkV6JEL0E | Ручной запуск Adapter |

---

## 1. Scout — Разведка

```mermaid
flowchart LR
    CRON["Cron 6ч"] --> GN["Google News RSS\nEN + RU, 9 запросов"]
    CRON --> HN["HackerNews\nTop AI stories"]
    CRON --> GH["GitHub Trending\nAI repos за 7 дней"]
    GN & HN & GH --> FILTER["Фильтр 24ч\n+ дедупликация SHA256"]
    FILTER --> DB["content.news_feed"]
```

**Источники:** Google News RSS (EN + RU, 9 AI-запросов), HackerNews Top Stories, GitHub Trending AI repos
**Фильтрация:** только за последние 24ч, дедупликация по SHA256(title)
**Результат:** записи в `content.news_feed` с полями title, url, source, score

---

## 2. Writer — Автор

```mermaid
flowchart LR
    CRON["Cron 06:00 Istanbul"] --> SQL["TOP-5 неиспользованных\nновостей по score"]
    SQL --> LLM["MiniMax M2.5\n700-1200 символов RU\nx5 постов"]
    LLM --> QG["Quality Gate\n12 проверок\nscore >= 65"]
    QG --> DB["content.posts"]
```

**LLM:** MiniMax M2.5 через Anthropic-совместимый API
**Промпт:** Anti-AI writing rules (запрет тире, канцелярита, "это не просто")
**Quality Gate:** 12 проверок, минимальный score 65
**Результат:** 3-5 постов/день в `content.posts`

---

## 3. Illustrator — Художник

```mermaid
flowchart LR
    CRON["Cron 06:30 Istanbul"] --> SQL["Посты без картинок"]
    SQL --> GEMINI["Gemini 2.5 Flash\nDocker :8800\npop-art стиль"]
    GEMINI --> DB["content.posts\n+ image_url"]
```

**Сервис:** Docker контейнер `gemini-image-service` (порт 8800, внутри Docker network)
**Стиль:** Pop-art (красный/жёлтый, halftone, fisheye perspective, девушки каждый 3-й пост)
**Хранение:** /opt/content-pipeline-images/ → corp.timzinin.com/content-images/

---

## 4. Adapter — Адаптер

```mermaid
flowchart LR
    CRON["Cron 07:00 Istanbul"] --> SQL["Неадаптированные посты"]
    SQL --> LLM["MiniMax M2.5\n10 платформ"]
    LLM --> DB["content.platform_posts\nпост + комментарий\n+ reply + ссылка"]
    DB --> SYNC["Синхронизация\nDashboard"]
```

**10 платформ:** telegram, linkedin, threads_ru, threads_en, vk, bluesky, facebook, mastodon, devto, hashnode
**Составные сущности:** post_text + comment_text (LI/FB) + reply_text (Threads) + link_url + include_image
**Результат:** ~50 записей/день в `content.platform_posts` со статусом `draft`

---

## 5. Curator — Куратор

```mermaid
flowchart LR
    CRON["Cron 07:30 Istanbul"] --> SQL["Все draft посты\n+ quality_score\n+ topic_cluster"]
    SQL --> CODE["Распределение по Tier\n+ дедупликация\n+ stagger scheduling"]
    CODE --> UPDATE["scheduled_at\nstatus = scheduled|skipped"]
```

**Tier-система:** см. [[Curator]]
**Дедупликация:** topic_cluster за последние 3 дня — fresh посты приоритетнее stale
**Scheduling:** Istanbul UTC+3, stagger по платформам
**Результат:** ~14-25 записей `scheduled`, остальные `skipped`

---

## 6. Publisher v3

**n8n ID:** ErbbScuvxWHLX1np (заменил v2: 1cD3qXs2XZkgcQyt)

```mermaid
flowchart LR
    CRON["Schedule\n*/30 09-03 Istanbul"] --> SQL["Select Scheduled\nLIMIT 1\nWHERE platform IN allowlist"]
    SQL --> IF1{"Has Post?"}
    IF1 -->|Да| HTTP["Call Publisher\nPOST :8085/publish"]
    HTTP --> UPD["Update Status\nsent / failed + retry"]
    UPD --> IF2{"Dead Letter?\nretries >= 3"}
    IF2 -->|Да| TG["TG Alert"]
```

**Python Publisher Service:** Docker :8086 (internal :8085), reads post by ID from DB, calls auto-publisher adapter
**Модель:** `scheduled → sending (lock) → sent (API ok) → verified (/verify)` / `→ failed (retry 3x → TG alert)`
**Anti-duplicate:** atomic lock через `sending` status, отказ при повторном вызове
**Working (10):** Telegram, Dev.to, VK, Threads RU, Hashnode, Facebook (Publer), Threads EN (Publer), Write.as, Minds, Nostr
**Partial:** Bluesky (text 5/5 ok, image blocked >1MB)
**Blocked:** Tumblr (401 OAuth), Mastodon (401 token)
**Separate:** LinkedIn (own pipeline)
**/verify:** endpoint для external read-back (6 платформ)
**Подробнее:** [[Publisher]]

---

## 7. Dashboard

**URL:** GET https://n8n.timzinin.com/webhook/content-dashboard
**Данные:** news_feed, posts, platform_posts, stats (scheduled, skipped, published)
**Формат:** HTML с таблицами и статистикой

## 8. Curator Preview

**URL:** GET https://n8n.timzinin.com/webhook/curator-preview
**Назначение:** dry-run Curator без изменения БД. Показывает snapshot текущих draft → что бы Curator назначил, НЕ меняя данные.
**Важно:** preview пустой если нет draft постов (все уже scheduled/skipped). Это не баг.
**Формат:** JSON с полями scheduled[], skipped[], summary

---

## 9. Observer — Наблюдатель

**n8n ID:** V2wnna7ACw5iSqdi
**URL:** GET https://n8n.timzinin.com/webhook/observer
**Timezone:** Istanbul (UTC+3)

```mermaid
flowchart LR
    WH["Webhook GET"] --> SQL["PostgreSQL:\nstats + schedule +\nplatforms + health"]
    SQL --> HTML["Render HTML"]
    HTML --> RESP["HTML Response"]
```

Центральный operational dashboard. Показывает:

| Секция | Что показывает |
|--------|---------------|
| Cards | Draft / Scheduled / Published* / Sent / Verified / Skipped / Failed / Posts / News / Unused |
| Pipeline Health | Последний запуск каждого workflow за 24ч, количество записей |
| Platform Summary | Таблица: платформа × статус (draft/scheduled/sending/sent/verified/published*/skipped/failed) |
| Schedule | Расписание постов с временем (Istanbul), quality score, topic cluster |
| Recent Published | Последние 10 опубликованных постов |
| Publication Log | Последние 20 попыток публикации: sent/verified/failed с external ID и ошибками (Sprint 4A) |

**Ссылки на Observer:**
- corp.timzinin.com → sidebar → Observer (PIPELINE)
- corp.timzinin.com/content-calendar.html → подзаголовок
- TG сводка от Curator (ежедневно 07:30 Istanbul)
