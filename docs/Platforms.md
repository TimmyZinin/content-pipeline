# Платформы

> Расписание, API, частота публикаций

## Tier-система

```mermaid
graph TD
    T1["Tier 1 — Ежедневно"]
    T2["Tier 2 — 3x/нед (ПН/СР/ПТ)"]
    T3["Tier 3 — 1x/нед (ПН)"]
    T4["Tier 4 — Видео (отдельный пайплайн)"]

    T1 --> TG["Telegram 2/день"]
    T1 --> THR["Threads RU 5/день"]
    T1 --> THEN["Threads EN 5/день"]
    T1 --> BS["Bluesky 3/день"]
    T1 --> MAS["Mastodon 1/день"]

    T2 --> LI["LinkedIn 1/день"]
    T2 --> VK["VK 1/день"]
    T2 --> FB["Facebook 1/день"]

    T3 --> DEV["Dev.to 1/нед"]
    T3 --> HASH["Hashnode 1/нед"]

    T4 --> TT["TikTok"]
    T4 --> IG["Instagram Reels"]
    T4 --> YT["YouTube Shorts"]
```

## Полная таблица

| # | Платформа | Язык | Частота | Метод | Status (1 апр 2026) | Last published_at (UTC) |
|---|-----------|------|---------|-------|---------------------|------------------------|
| 1 | Telegram @timofeyzinin | RU | 2/день | Direct adapter | ⚠️ Recently verified | 2026-03-31 10:00 (1 день) |
| 2 | Threads RU @timzinin | RU | 5/день | Direct adapter (2-step) | ⚠️ Recently verified | 2026-03-30 10:09 (2 дня) |
| 3 | Bluesky | EN | 3/день | Direct adapter (auto-resize) | ⚠️ Recently verified | 2026-03-30 10:09 (2 дня) |
| 4 | Mastodon | EN | 1/день | Direct adapter | ⚠️ Recently verified | 2026-03-29 13:00 (3 дня) |
| 5 | Threads EN | EN | 5/день | Publer 2-step media | ⚠️ Recently verified | 2026-03-28 23:00 (3 дня) |
| 6 | Facebook | RU | 1/день | Publer (personal profile) | ⚠️ Recently verified | 2026-03-28 19:30 (3 дня) |
| 7 | VK | RU | 1/день | Direct adapter (community) | ⚠️ Recently verified | 2026-03-28 19:00 (3 дня) |
| 8 | LinkedIn | RU | 1/день ПН/СР/ПТ | Direct adapter | ⚠️ Recently verified | 2026-03-27 11:30 |
| 9 | Dev.to | EN | 1/нед (ПН) | Direct adapter | ⏳ Historically worked | 2026-03-23 (9 дней) |
| 10 | Hashnode | EN | 1/нед (ПН) | Direct adapter (GraphQL) | ⏳ Historically worked | 2026-03-23 (9 дней) |
| 11 | Write.as | EN | 1/нед (ПН) | Direct adapter | ⏳ Historically worked | Manual test 22 Mar |
| 12 | Minds | EN | ПН/СР/ПТ | Direct adapter | ⏳ Historically worked | Manual test 22 Mar |
| 13 | Nostr | EN | ПН/СР/ПТ | Direct adapter | ⏳ Historically worked | Manual test 22 Mar |
| 14 | Tumblr | EN | ПН/СР/ПТ | — | ❌ Blocked (401 OAuth) | Never |

Legend: ⚠️ = published ≤7 days ago | ⏳ = published >7 days ago | ❌ = blocked

## Не подключены (бэклог)

| Платформа | Язык | Статус |
|-----------|------|--------|
| Twitter/X | EN | Отложен |
| Medium | EN | Нет API |
| VC.ru | RU | Нет адаптера |

## Методы публикации

```mermaid
graph LR
    subgraph DIRECT["Direct API (бесплатно)"]
        TG["Telegram"]
        BS["Bluesky"]
        MAS["Mastodon"]
        DEV["Dev.to"]
        HASH["Hashnode"]
        THR["Threads RU"]
        VK["VK"]
        LI["LinkedIn"]
    end

    subgraph PUBLER["Publer API ($5/мес)"]
        FB["Facebook"]
        THEN["Threads EN"]
        TT["TikTok"]
    end

    subgraph AUTOPUB["auto-publisher адаптеры"]
        WA["Write.as"]
        TUM["Tumblr"]
        MINDS["Minds"]
        NOSTR["Nostr"]
    end
```

## Source of Truth для стратегий

GitHub: https://github.com/TimmyZinin/smm-research-hub
Файлы: `smm_audits/md/s00-s34`

| Файл | Платформа |
|------|-----------|
| s00_global_strategy.md | Мастер-стратегия |
| s01_linkedin.md | LinkedIn |
| s04_telegram_personal.md | Telegram |
| s06_threads.md | Threads |
| s07_facebook.md | Facebook |
| s09_vk.md | VK |
| s11_devto.md | Dev.to |
| s13_hashnode.md | Hashnode |
| s14_bluesky.md | Bluesky |
| s15_mastodon.md | Mastodon |
| s33_publer_integration.md | Publer |
