# Publisher — Публикатор

## Текущее состояние (v3) — Sprint 4A

### Publisher v3 (n8n)
**n8n ID:** ErbbScuvxWHLX1np
**Cron:** */30 09:00-03:00 Istanbul (UTC+3)
**Статус:** Active

7 нод:
```
Schedule → Select Scheduled → Has Post? → Call Publisher → Update Status → Dead Letter? → TG Alert
```

### Python Publisher Service
**URL:** http://publisher-service:8085 (Docker, Contabo :8086 external)
**API:** POST /publish {platform_post_id} → {status, platform, post_id, external_id, error}
**Health:** GET /health
**Source:** /opt/publisher-service/main.py
**Adapters:** /opt/auto-publisher/adapters/ (mounted read-only)
**Credentials:** /opt/zinin-corp/.env (env_file в docker-compose)

### Текущая модель статусов (Sprint 4A)

```
scheduled → sent (Python Service вернул ok, API платформы принял)
scheduled → failed (после 3 retry с backoff 5/15/60 мин)
```

> `verified` вводится в Sprint 4B (external read-back).
> Старый статус `published` больше НЕ используется Publisher v3. Записи со статусом `published` — наследие старого Publisher v2.

### Deactivated
- **Publisher v2** (1cD3qXs2XZkgcQyt) — ДЕАКТИВИРОВАН 22 мар 2026. Был причиной дубликатов и публикаций без картинок.

### Verified platforms (через Python Service)

| Платформа | Статус | External ID | Примечание |
|-----------|--------|-------------|-----------|
| Telegram | ✅ sent | 292, 293 | Верифицировано внешне (Тим видел в канале) |
| Dev.to | ✅ sent | 3384773 | Статья опубликована |
| VK | ✅ sent | 350 | wall.post через user token |
| Threads RU | ✅ sent | 17992609448939339 | Двухшаговый API (create+publish) |
| Hashnode | ✅ sent | 69c0062180048b76fe51c505 | GraphQL mutation |
| Bluesky | ❌ error | — | 400 Bad Request, баг в адаптере (апострофы). Fix в 4B |

### Не тестировались в 4A
| Платформа | Причина | Когда |
|-----------|---------|-------|
| LinkedIn | Отдельный OAuth flow | Sprint 4B |
| Facebook | Через Publer | Sprint 4B |
| Threads EN | Через Publer | Sprint 4B |
| Mastodon | Токен невалиден | Sprint 4B (если credential восстановлен) |
| Tumblr, Write.as, Minds, Nostr | Новые в Adapter | Sprint 4B |

---

## Инцидент: дубликаты (22 мар 2026)

**Что произошло:** Telegram и LinkedIn получили дублированные посты Zeroboot.

**Root cause:** Ручное тестирование Publisher Service через `curl POST /publish` не обновляет статус в БД (это ответственность n8n). Пост остался `scheduled`, и Publisher v2/v3 отправил его повторно.

**Что сделано:**
- Publisher v2 деактивирован
- Publisher v3 обновляет статус на `sent` сразу после успешного вызова

**Правило на будущее:** ручной `curl /publish` по scheduled постам в prod запрещён. Для тестирования — создавать тестовый пост или использовать пост со статусом `draft`, вручную переведённый в `scheduled`.

---

## Sprint 4B: Verification + остальные платформы

| # | Задача | Описание |
|---|--------|----------|
| PUB-B1 | Bluesky fix | Исправить адаптер (encoding апострофов) |
| PUB-B2 | verified status | External read-back для TG, Dev.to, VK, Threads RU, Hashnode |
| PUB-B3 | Publer platforms | Facebook, Threads EN через Publer API |
| PUB-B4 | LinkedIn | OAuth refresh + image upload |
| PUB-B5 | Mastodon | Восстановить credential |
| PUB-B6 | Observer Publication Log | Показывать sent/verified/failed с деталями |
| PUB-B7 | Новые 4 платформы | Tumblr, Write.as, Minds, Nostr через адаптеры |
