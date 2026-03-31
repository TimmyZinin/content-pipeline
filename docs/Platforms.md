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

| # | Платформа | Язык | Частота | Метод | Current status (31 мар 2026) | Last publish |
|---|-----------|------|---------|-------|------------------------------|-------------|
| 1 | Telegram @timofeyzinin | RU | 2/день | Direct adapter | ✅ Currently verified | Mar 31 (msg_id=318) |
| 2 | Threads RU @timzinin | RU | 5/день | Direct adapter (2-step) | ✅ Currently verified | Mar 30 |
| 3 | Threads EN | EN | 5/день | Publer 2-step media | ⚠️ Recently verified | Mar 28 |
| 4 | LinkedIn | RU | 1/день ПН/СР/ПТ | Direct adapter | ⚠️ Recently verified | Mar 27 |
| 5 | Bluesky | EN | 3/день | Direct adapter (auto-resize) | ✅ Currently verified | Mar 30 |
| 6 | Mastodon | EN | 1/день | Direct adapter | ⚠️ Recently verified | Mar 29 |
| 7 | VK | RU | 1/день | Direct adapter (community) | ⚠️ Recently verified | Mar 28 |
| 8 | Facebook | RU | 1/день | Publer (personal profile) | ⚠️ Recently verified | Mar 28 |
| 9 | Dev.to | EN | 1/нед (ПН) | Direct adapter | ⏳ Historically worked | Mar 23 |
| 10 | Hashnode | EN | 1/нед (ПН) | Direct adapter (GraphQL) | ⏳ Historically worked | Mar 23 |
| 11 | Write.as | EN | 1/нед (ПН) | Direct adapter | ⏳ Historically worked | Manual test 22 Mar |
| 12 | Minds | EN | ПН/СР/ПТ | Direct adapter | ⏳ Historically worked | Manual test 22 Mar |
| 13 | Nostr | EN | ПН/СР/ПТ | Direct adapter | ⏳ Historically worked | Manual test 22 Mar |
| 14 | Tumblr | EN | ПН/СР/ПТ | — | ❌ Blocked (401 OAuth) | Never |

Legend: ✅ = published in last 2 days | ⚠️ = published in last 7 days | ⏳ = published >7 days ago | ❌ = blocked

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
