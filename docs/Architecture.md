# Архитектура Content Pipeline v2

## Data Flow

```mermaid
flowchart TB
    subgraph SOURCES["Источники | cron 05:00 Istanbul"]
        GN["Google News RSS<br/>EN + RU, 9 запросов"]
        HN["HackerNews<br/>Top AI stories"]
        GH["GitHub Trending<br/>AI repos за 7 дней"]
    end

    subgraph SCOUT["Scout — Разведка"]
        FILTER["Фильтр 24ч + дедупликация SHA256"]
    end

    subgraph WRITER["Writer — Автор | 06:00 Istanbul"]
        LLM["MiniMax M2.5<br/>700-1200 символов RU"]
        QG["Quality Gate<br/>12 проверок, score >= 65"]
    end

    subgraph ILLUSTRATOR["Illustrator — Художник | 06:30 Istanbul"]
        GEMINI["Gemini 2.5 Flash<br/>Pop-art стиль"]
    end

    subgraph ADAPTER["Adapter — Адаптер | 07:00 Istanbul"]
        ADAPT["MiniMax M2.5<br/>10 платформ"]
    end

    subgraph CURATOR["Curator — Куратор | 07:30 Istanbul"]
        TIER["Tier-система<br/>Quality-based selection"]
        DEDUP["Дедупликация<br/>topic_cluster 3 дня"]
        SCHED["Stagger scheduling<br/>Istanbul UTC+3"]
    end

    subgraph PUBLISHER["Publisher — Публикатор | */30 09-03 Istanbul"]
        DIRECT["Direct API<br/>TG, Bluesky, Mastodon<br/>Dev.to, Hashnode"]
        PUBLER["Publer API<br/>Facebook, TikTok<br/>Threads EN"]
        TWOAPI["Two-step API<br/>Threads RU, LinkedIn"]
    end

    GN & HN & GH --> FILTER
    FILTER --> DB_NEWS[("content.news_feed")]
    DB_NEWS --> LLM --> QG --> DB_POSTS[("content.posts")]
    DB_POSTS --> GEMINI --> DB_POSTS
    DB_POSTS --> ADAPT --> DB_PP[("content.platform_posts<br/>status: draft")]
    DB_PP --> TIER & DEDUP --> SCHED --> DB_PP2[("content.platform_posts<br/>status: scheduled")]
    DB_PP2 --> DIRECT & PUBLER & TWOAPI --> DB_PP3[("content.platform_posts<br/>status: published*")]

    style SOURCES fill:#dbeafe,stroke:#2563eb
    style SCOUT fill:#dbeafe,stroke:#2563eb
    style WRITER fill:#dcfce7,stroke:#16a34a
    style ILLUSTRATOR fill:#fef3c7,stroke:#d97706
    style ADAPTER fill:#ede9fe,stroke:#7c3aed
    style CURATOR fill:#fff7ed,stroke:#ea580c
    style PUBLISHER fill:#fce7f3,stroke:#db2777
```

## Инфраструктура

```mermaid
graph LR
    subgraph CONTABO["Contabo VPS 30 (185.202.239.165)"]
        N8N["n8n :5678"]
        PG["PostgreSQL :5432"]
        GEMINI["Gemini Image :8800"]
        NGINX["Nginx :443"]
    end

    subgraph EXTERNAL["Внешние сервисы"]
        MM["MiniMax M2.5 API"]
        GEM["Google Gemini API"]
        PUB["Publer API"]
        TG_API["Telegram Bot API"]
        META["Meta Threads API"]
        VK_API["VK API"]
        LI_API["LinkedIn API"]
        BS_API["Bluesky API"]
    end

    N8N --> PG
    N8N --> GEMINI
    N8N --> MM & GEM & PUB
    N8N --> TG_API & META & VK_API & LI_API & BS_API
    NGINX --> N8N

    style CONTABO fill:#f0fdf4,stroke:#16a34a
    style EXTERNAL fill:#fef2f2,stroke:#dc2626
```

## Время работы (Istanbul UTC+3, ежедневно)

> Все cron-ы задаются в UTC на сервере. Ниже — Istanbul (UTC+3) для удобства.

| Время (Istanbul) | Workflow | Что делает |
|-----------------|----------|------------|
| 05:00 | Scout | Сбор новостей из RSS, HN, GitHub |
| 06:00 | Writer | Генерация 5 постов из лучших новостей |
| 06:30 | Illustrator | Генерация картинок Gemini |
| 07:00 | Adapter | Адаптация 5 постов на 14 платформ |
| 07:30 | Curator | Распределение по расписанию |
| 09:00-00:00 | Publisher | Публикация каждые 30 мин по scheduled_at |

## Текущая модель статусов (Sprint 4A/4B/4C)

```
draft → scheduled → sending (atomic lock) → sent (API ok) → verified (read-back)
draft → scheduled → sending → failed (after 3 retry)
draft → skipped (пропущен Curator)
published = legacy статус от старого Publisher v2
```

> Подробнее: [[Database]], [[Publisher]]
