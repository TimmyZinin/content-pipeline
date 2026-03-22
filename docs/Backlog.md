# Бэклог

> Обновлено: 22 марта 2026

## Прогресс по оригинальному плану

| # | Спринт | Статус | Дата |
|---|--------|--------|------|
| 1 | Pipeline на n8n (Scout, Writer, Illustrator, Dashboard) | ✅ Done | 20 мар |
| 1b | Обновление 16 стратегий smm-research-hub | ✅ Done | 21 мар |
| 2 | Publer API key + Threads EN/TH | ✅ Частично | 21 мар |
| 3 | Adapter workflow (10 платформ) | ✅ Done | 21 мар |
| — | Curator (добавлен, не был в плане) | ✅ Done | 22 мар |
| 4 | Publisher + HITL | ⚠️ Сделан криво | 22 мар |
| 5 | ChatPlace + Email + TG-бот | ❌ Не начат | — |
| 6 | Analyst + Feedback | ❌ Не начат | — |

## Спринт 3 (Curator+): Полнота + Observability

| # | Задача | Приоритет | Описание |
|---|--------|-----------|----------|
| CUR-11 | +5 платформ в Adapter | HIGH | Write.as, Tumblr, Minds, Nostr, Twitter/Publer |
| CUR-12 | TG отчёт от Curator | MED | Ежедневная сводка: сколько назначено, на какие платформы |
| CUR-13 | Конфиг в JSON | MED | /opt/content-pipeline/curator-config.json — менять без n8n |
| CUR-14 | Fallback alert | MED | Если 0 draft постов → TG уведомление |
| CUR-15 | Override в Dashboard | LOW | Кнопки добавить/убрать из расписания |

## Спринт 4: Publisher Refactor

| # | Задача | Приоритет | Описание |
|---|--------|-----------|----------|
| PUB-1 | Python HTTP сервис | CRIT | Flask/FastAPI wrapper над auto-publisher адаптерами |
| PUB-2 | n8n Publisher refactor | CRIT | HTTP Request нода → Python сервис |
| PUB-3 | Проверка API ответа | CRIT | published ТОЛЬКО после success |
| PUB-4 | Retry с backoff | HIGH | 3 попытки: 5/15/60 мин |
| PUB-5 | Dead letter + alert | HIGH | После 3 неудач → failed + TG alert |
| PUB-6 | Все 10 платформ | HIGH | Через Python адаптеры |
| PUB-7 | Credentials в n8n | MED | Вынести токены из Code нод |

## Спринт 5: ChatPlace + Email + TG-бот

| # | Задача | Приоритет | Описание |
|---|--------|-----------|----------|
| EXT-1 | ChatPlace.io | HIGH | Кодовое слово → подписка → ссылка (IG/TikTok/YouTube) |
| EXT-2 | AI Digest email | HIGH | Substack/Beehiiv ежедневная рассылка |
| EXT-3 | TG-бот CRM | MED | Бот для сбора лидов и nurturing |

## Спринт 6: Analyst + Feedback Loop

| # | Задача | Приоритет | Описание |
|---|--------|-----------|----------|
| ANA-1 | Сбор engagement | HIGH | VK/TG/Threads/LinkedIn API → content.engagement |
| ANA-2 | Daily report в TG | HIGH | Топ посты по engagement |
| ANA-3 | Weekly digest | MED | Лучшие темы/платформы за неделю |
| FBK-1 | Feedback → Ideator | MED | Engagement → приоритет в Scout |
| FBK-2 | QG калибровка | MED | Bell curve, не все 98+ |
| FBK-3 | Evergreen recycling | LOW | score >90 через 30 дней → recycle |
| FBK-4 | Hero Content Model | LOW | 1 long-form → 10 micro-pieces |
