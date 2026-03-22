# Publisher — Публикатор

## Текущее состояние (v3) — Sprint 4A + 4B checkpoint

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
**Source:** /opt/publisher-service/main.py
**Adapters:** /opt/auto-publisher/adapters/ (mounted read-only)
**Credentials:** /opt/zinin-corp/.env (env_file в docker-compose)

**Endpoints:**
| Method | Path | Input | Output | DB changes? |
|--------|------|-------|--------|-------------|
| POST | /publish | {platform_post_id} | {status, platform, post_id, external_id, error} | Yes (sending→sent/failed) |
| POST | /verify | {platform_post_id} | {status, platform, post_id, reason} | No |
| POST | /test-publish | {platform, text, image_url?} | {status, platform, post_id, external_id, error} | **No** — safe test, no DB |
| GET | /health | — | {status: "ok"} | No |

**Safe testing:** `/test-publish` для ручного тестирования платформ. Не трогает БД, не может создать дубликаты. Используй вместо `/publish` при проверке новых адаптеров.

**Anti-duplicate guard:** перед публикацией сервис атомарно ставит `status='sending'` через `UPDATE ... WHERE status IN ('scheduled','failed') RETURNING id`. Если пост уже `sent`, `verified`, `published` или `sending` — возвращает HTTP 400/409. Это предотвращает повторную публикацию при параллельных вызовах или ручном тестировании.

### Текущая модель статусов

```
scheduled → sending → sent → (verified в 4B)
scheduled → sending → failed (после 3 retry)
```

| Статус | Что означает |
|--------|-------------|
| scheduled | Curator назначил, ожидает Publisher |
| sending | Atomic lock: Publisher Service взял пост, публикация в процессе |
| sent | API платформы ответил OK, external_id записан |
| verified | /verify подтвердил наличие поста на платформе (Sprint 4B) |
| failed | Ошибка после 3 retry, TG alert отправлен |
| published | Legacy статус от старого Publisher v2. Не используется Publisher v3 |

**Verify endpoint:** проверяет наличие поста на платформе по external_id.

| Платформа | Метод verify | Надёжность |
|-----------|-------------|------------|
| Telegram | Trusted (sendMessage response) | Высокая — Тим подтвердил внешне |
| Dev.to | API GET /articles/{id} | Высокая — проверяет реальную статью |
| VK | API wall.getById | Высокая — проверяет реальный пост |
| Threads RU | Graph API GET /{id} | Высокая — проверяет реальный пост |
| Hashnode | Trusted (GraphQL response) | Средняя — доверяем API ответу |
| Bluesky | Trusted (createRecord response) | Средняя — доверяем API ответу |

### Deactivated
- **Publisher v2** (1cD3qXs2XZkgcQyt) — ДЕАКТИВИРОВАН 22 мар 2026. Был причиной дубликатов и публикаций без картинок.

### Verified platforms (через Python Service)

| Платформа | Статус | External ID | Примечание |
|-----------|--------|-------------|-----------|
| Telegram | ✅ sent | 292, 293 | Верифицировано внешне (Тим видел в канале) |
| Dev.to | ✅ sent | 3384773 | Статья опубликована |
| VK | ✅ sent (text+image) | 351 | wall.post в сообщество (group 229813427). Target = community wall |
| Threads RU | ✅ sent | 17992609448939339 | Двухшаговый API (create+publish) |
| Hashnode | ✅ sent | 69c0062180048b76fe51c505 | GraphQL mutation |
| Bluesky | ✅ sent (1 test) | at://...3mhnuulnbph2x | Адаптер работает. Ранее 400 при тексте >300 chars с em-dash |
| Facebook | ✅ sent (text+image) | Publer job_id | Personal profile через Publer. 2-step media upload. Verified by Tim |
| Threads EN | ✅ sent (text+image) | threads.com/@timzinin_en/... | Через Publer. 2-step media upload. Verified by Tim |

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

**Anti-duplicate measures:**

Риск дублей значительно снижен, но не исключён полностью. Root cause известен.

Текущие меры:
1. Anti-duplicate guard: atomic `sending` lock в Publisher Service (HTTP 400/409 при повторном вызове)
2. Процессное правило: ручной `curl POST /publish` по prod scheduled постам запрещён
3. Тестирование: создавать отдельный тестовый пост с уникальным текстом

Safe testing path:
- **`POST /test-publish`** — dedicated endpoint, не трогает БД, изолирован от prod scheduler. Deployed.

Инцидент 22 мар: дубли в TG, LinkedIn, VK — все от одной причины (ручной curl без обновления статуса).

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
