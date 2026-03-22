# LEGACY — НЕ ИСПОЛЬЗОВАТЬ

> **Source of truth: docs/Home.md**
> Этот файл устарел. Актуальная документация в docs/.

# Content Pipeline v2 — Статус на 22 марта 2026 (LEGACY)

## Работающие workflows (n8n, Contabo)

| Workflow | ID | Cron | Статус |
|----------|----|------|--------|
| Scout | RSQALdJch4WYZfit | 02:00 MSK | ACTIVE |
| Writer | ZQtg31g6dzAV0lXX | 03:00 MSK | ACTIVE |
| Illustrator | Z94O5uyaFEmrYGIJ | 03:30 MSK | ACTIVE |
| Adapter | NJoPcdp38ZU0dQwG | 04:00 MSK | ACTIVE |
| Dashboard | DC3a34HOedbU7rVb | webhook | ACTIVE |
| Curator | EYPcT5B4rLmQRQBM | 04:30 MSK | ACTIVE |
| Publisher v2 | 1cD3qXs2XZkgcQyt | */30 06-21 | ACTIVE |

## Publisher — верифицированный статус платформ

| Платформа | Работает? | Проблема |
|-----------|----------|---------|
| Telegram | ДА | Bot 8567660569, @timofeyzinin |
| Dev.to | ДА | API key, articles API |
| LinkedIn | Вероятно | ugcPosts API |
| Facebook | Вероятно | Publer API |
| Threads EN | Вероятно | Publer API |
| Threads RU | НЕТ | Двухшаговый API (create + publish) |
| VK | НЕТ | wall.post не создаёт пост |
| Bluesky | НЕТ | Двухшаговый (auth + createRecord) |
| Mastodon | НЕТ | Токен невалидный? |
| Hashnode | Не проверено | GraphQL |

## Критический баг

n8n Code node sandbox блокирует `fetch()` и `require('https')`.
ВСЕ HTTP запросы ТОЛЬКО через HTTP Request ноды n8n.
Для двухшаговых API (Threads, Bluesky) нужна цепочка HTTP нод.

## Что нужно

1. Добавить Switch + вторую HTTP ноду для Threads RU и Bluesky
2. Исправить VK (формат запроса)
3. Проверить Mastodon токен
4. Реализовать Curator workflow
5. Dashboard UX доработки
