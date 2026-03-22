# Publisher — Публикатор

## Текущее состояние (v3) — Sprint 4D

### Publisher v3 (n8n)
**n8n ID:** ErbbScuvxWHLX1np
**Cron:** */30 09:00-03:00 Istanbul (UTC+3)
**Статус:** Active (staged rollout)

7 нод:
```
Schedule → Select Scheduled (SQL allowlist) → Has Post? → Call Publisher → Check Result (pass-through) → Dead Letter? → TG Alert
```

**n8n role = orchestration only.** Не пишет sent/failed в БД. Только: select, call, check, retry, alert.

### Python Publisher Service
**URL:** http://publisher-service:8085 (Docker, Contabo :8086 external)
**Canonical source:** content-pipeline/publisher-service/main.py
**Adapters:** /opt/auto-publisher/adapters/ (mounted read-only)
**Credentials:** /opt/zinin-corp/.env (env_file в docker-compose)

**Endpoints:**
| Method | Path | Input | Output | DB changes? |
|--------|------|-------|--------|-------------|
| POST | /publish | {platform_post_id} | {status, platform, post_id, external_id, error} | Yes (sending→sent/failed) |
| POST | /verify | {platform_post_id} | {status, platform, post_id, reason} | No |
| POST | /test-publish | — | HTTP 403 | **DISABLED** — published to real accounts |
| GET | /health | — | {status: "ok"} | No |

**Safe testing:** `/test-publish` **ОТКЛЮЧЁН** (HTTP 403). Публиковал в реальные аккаунты. Для тестирования — только local adapter testing.

### Staged Rollout (allowlist)

**Primary filter:** SQL в n8n Publisher v3 workflow (Select Scheduled):
```sql
WHERE platform IN ('telegram','writeas','minds')
```
Неразрешённые платформы **не попадают** в Publisher вообще. Нет HTTP вызова, нет retry, нет шума.

**Secondary guard:** `PUBLISH_ALLOWLIST` env var в Publisher Service. Если пост каким-то образом дошёл — 403 ROLLOUT GUARD.

**Где живёт allowlist:**
| Место | Что делает | Приоритет |
|-------|-----------|-----------|
| n8n Select Scheduled SQL | Фильтрует ДО HTTP вызова | Primary |
| Publisher Service env var | Reject если прошёл мимо SQL | Secondary |
| docs/Publisher.md | Документация | Reference |

**Расширение allowlist:** обновить **оба** места синхронно:
1. n8n workflow SQL: `platform IN (...)`
2. Contabo env: `PUBLISH_ALLOWLIST=...` + restart publisher-service

**Текущий rollout stage:** telegram, writeas, minds

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

### Current Rollout (staged allowlist)

**Сейчас активно публикуются только:** telegram, writeas, minds

Остальные платформы отфильтрованы SQL upstream. Не публикуются, не retry, не failed.

### Historically Verified Capability (через Python Service)

| Платформа | Статус | External ID | Примечание |
|-----------|--------|-------------|-----------|
| Telegram | ✅ sent | 292, 293 | Верифицировано внешне (Тим видел в канале) |
| Dev.to | ✅ sent | 3384773 | Статья опубликована |
| VK | ✅ sent (text+image) | 351 | wall.post в сообщество (group 229813427). Target = community wall |
| Threads RU | ✅ sent | 17992609448939339 | Двухшаговый API (create+publish) |
| Hashnode | ✅ sent | 69c0062180048b76fe51c505 | GraphQL mutation |
| Bluesky | ⚠️ text verified (5/5) | at://... | Text ok, image blocked (>1MB blob limit) |
| Facebook | ✅ sent (text+image) | Publer job_id | Personal profile через Publer. 2-step media upload. Verified by Tim |
| Threads EN | ✅ sent (text+image) | threads.com/@timzinin_en/... | Через Publer. 2-step media upload. Verified by Tim |
| Write.as | ✅ sent | 9kmx5xof89omds5g | Historically verified during manual tests 22 mar |
| Minds | ✅ sent | 1882500900157657088 | Historically verified during manual tests 22 mar |
| Nostr | ✅ sent | 92928e1a... | Historically verified during manual tests 22 mar |
| Tumblr | ❌ blocked | — | 401 OAuth expired. Adapter rewritten, credential needs refresh |
| Mastodon | ❌ blocked | — | 401 token invalid |
| LinkedIn | ⚡ separate | — | Own pipeline (/opt/linkedin-pipeline/). Not in Publisher v3 |

---

## Инцидент: дубликаты (22 мар 2026)

**Что произошло:** Telegram и LinkedIn получили дублированные посты Zeroboot.

**Root cause:** ручной `curl POST /publish` публиковал пост, но статус не обновлялся (n8n Update Status не вызывался). Пост оставался `scheduled`, и workflow повторял публикацию.

**Что исправлено:**
- Publisher Service теперь **сам пишет** `sent/failed` в БД (ownership fix)
- n8n `Update Status` → `Check Result` (pass-through, не пишет в БД)
- Anti-duplicate: atomic `sending` lock + 409 при повторном вызове
- `/test-publish` отключён (HTTP 403)

**Anti-duplicate measures:**

Риск дублей значительно снижен, но не исключён полностью. Root cause известен.

Текущие меры:
1. Anti-duplicate guard: atomic `sending` lock в Publisher Service (HTTP 400/409 при повторном вызове)
2. Процессное правило: ручной `curl POST /publish` по prod scheduled постам запрещён
3. Тестирование: создавать отдельный тестовый пост с уникальным текстом

Safe testing:
- **`POST /test-publish` — DISABLED** (HTTP 403). Публиковал в реальные аккаунты. Инцидент 22 мар.
- Для тестирования платформ — только local adapter testing вне Docker.

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
