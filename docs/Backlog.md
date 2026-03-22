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
| — | Observer (добавлен, не был в плане) | ✅ Done | 22 мар |
| 4A | Publisher Refactor (Python Service + n8n v3) | ✅ Done | 22 мар |
| 4B | Publisher: Publer + verify + anti-duplicate | ✅ Done (7/10 verified) | 22 мар |
| 4C | Text Coverage Completion | 🔄 Current | — |
| 4G | LinkedIn System Audit & Integration Design | ⏳ After 4C | — |
| 5 | ChatPlace + Email + TG-бот | ❌ Не начат | — |
| 6 | Analyst + Feedback | ❌ Не начат | — |

## Observer — постоянный инструмент наблюдения

**URL:** https://n8n.timzinin.com/webhook/observer
**n8n ID:** V2wnna7ACw5iSqdi
**Timezone:** Istanbul (UTC+3)

Observer — центральная точка наблюдения за всей системой. Показывает:
- Карточки статусов (draft/scheduled/published/skipped/failed)
- Platform Summary — распределение по платформам
- Schedule — расписание и недавние публикации
- Pipeline Health — статус последнего цикла (Scout → Writer → Illustrator → Adapter → Curator)

**Интеграции Observer:**
- Ссылка на corp.timzinin.com/ (дашборды)
- Ссылка на странице Content Calendar
- CUR-12 (TG сводка) включает ссылку на Observer
- Auto-refresh при открытии

---

## Спринт 3: Curator+ (Полнота + Observability)

| # | Задача | Приоритет | Описание |
|---|--------|-----------|----------|
| CUR-11 | +5 платформ в Adapter | HIGH | Write.as, Tumblr, Minds, Nostr, Twitter/Publer — адаптеры уже есть в auto-publisher, нужно добавить в промпт MiniMax и PLATFORM_CONFIG Curator |
| CUR-12 | TG сводка + Observer ссылка | HIGH | Ежедневно после Curator: "Назначено X на Y платформ" + ссылка на Observer. Curator шлёт через tg-communicator |
| CUR-13 | Observer: Pipeline Health | HIGH | Добавить секцию: когда последний раз отработали Scout/Writer/Illustrator/Adapter/Curator, сколько записей создал каждый, были ли ошибки |
| CUR-14 | Конфиг в JSON | MED | /opt/content-pipeline/curator-config.json — расписание, maxPerDay, publishDays. Curator читает при запуске |
| CUR-15 | Fallback alert | MED | Если 0 draft постов → TG: "Writer/Adapter не сработали, проверь" |
| CUR-16 | Observer на corp.timzinin.com | MED | Добавить ссылку на Observer в дашборды corp.timzinin.com + на страницу Content Calendar |
| CUR-17 | Override в Dashboard | LOW | Кнопки добавить/убрать из расписания в Observer |

## Спринт 4: Publisher Refactor

Bottleneck всей системы — Publisher работает на 2/10 платформ.

| # | Задача | Приоритет | Описание |
|---|--------|-----------|----------|
| PUB-1 | Python Publisher Service | CRIT | FastAPI wrapper над auto-publisher/adapters/. Docker на Contabo :8085. POST /publish {platform, text, image_url, comment, reply, link} → {status, post_id, error} |
| PUB-2 | n8n Publisher → HTTP | CRIT | Одна HTTP Request нода вместо Code нод. Вызов Python сервиса |
| PUB-3 | Проверка ответа | CRIT | status=published ТОЛЬКО если API вернул success. Иначе status=failed + error |
| PUB-4 | Retry с backoff | HIGH | 3 попытки: 5/15/60 мин. n8n retry механизм или loop |
| PUB-5 | Dead letter + alert | HIGH | После 3 неудач → status=failed + TG alert с деталями |
| PUB-6 | Все 10 платформ | HIGH | TG, LinkedIn, Threads RU/EN, VK, Bluesky, FB, Mastodon, Dev.to, Hashnode |
| PUB-7 | Credentials в n8n | MED | Токены из Code нод → n8n Credentials store. Python сервис читает из .env |
| PUB-8 | Observer: Publication Log | MED | Секция в Observer: последние 20 публикаций с результатом (success/error/retry) |

## Sprint 4C: Text Coverage Completion (CURRENT)

Добить все текстовые платформы до честного статуса в Publisher v3.

| # | Задача | Платформа | Описание |
|---|--------|-----------|----------|
| 4C-1 | Bluesky hardening | Bluesky | Серия тестов (text, text+image, длинный текст). Довести до verified или зафиксировать ограничения |
| 4C-2 | Mastodon credential | Mastodon | Проверить/восстановить токен. Если удастся — тест через /test-publish |
| 4C-3 | Tumblr | Tumblr | Адаптер есть в auto-publisher. Подключить в Publisher Service, тест через /test-publish |
| 4C-4 | Write.as | Write.as | Адаптер есть. Подключить, тест |
| 4C-5 | Minds | Minds | Адаптер есть. Подключить, тест |
| 4C-6 | Nostr | Nostr | Адаптер есть. Подключить, тест |

**НЕ входит:** LinkedIn, video channels, Sprint 5, Sprint 6.
**LinkedIn правило:** не трогать, не писать адаптер, не тестировать.

**Definition of Done:** для каждой платформы — один из статусов:
- working (verified)
- blocked (explicit reason)
- separate owned path
- intentionally out of scope

## Sprint 4G: LinkedIn System Audit & Integration Design (AFTER 4C)

**Исследовательский спринт, НЕ implementation.**

Цель: понять как безопасно подключить LinkedIn к общему content bank без дублей.

Вопросы для ответа:
1. Где живёт текущий LinkedIn publisher
2. Что именно он публикует
3. Откуда берёт контент
4. Какой approval flow
5. Какой image flow
6. Какой scheduler/trigger/runtime
7. Можно ли безопасно подключить к content bank
8. Целевая архитектура: отдельный publisher + content bank source, migration в v3, или гибрид

**Гипотеза:** LinkedIn лучше оставить отдельным specialized publisher, но подключить к общему content bank как source of content. Единый source, но не обязательно единый transport.

---

## Спринт 5: Дистрибуция + Воронка

Расширение каналов за пределы соцсетей.

| # | Задача | Приоритет | Описание |
|---|--------|-----------|----------|
| EXT-1 | ChatPlace.io | HIGH | Видео-воронка: кодовое слово → подписка → ссылка (IG/TikTok/YouTube) |
| EXT-2 | AI Digest email | HIGH | Substack или Beehiiv. Ежедневная рассылка из лучших постов. Автоматическая выборка из content.posts (top quality_score за день) |
| EXT-3 | TG-бот CRM | MED | Бот для сбора лидов: подписка → nurturing цепочка → discovery call |
| EXT-4 | Observer: Channel Stats | MED | Секция в Observer: подписчики/охват по каждому каналу |

## Спринт 6: Analyst + Feedback Loop

Замыкание цикла: публикация → аналитика → улучшение генерации.

| # | Задача | Приоритет | Описание |
|---|--------|-----------|----------|
| ANA-1 | Сбор engagement | HIGH | VK API, TG API, Threads API, LinkedIn API → content.engagement (views, likes, comments, shares) |
| ANA-2 | Daily report в TG | HIGH | Ежедневно 21:00: топ-3 поста по engagement, худший пост, общий охват. Ссылка на Observer |
| ANA-3 | Weekly digest | MED | По воскресеньям: лучшие темы/платформы, рост подписчиков, рекомендации |
| FBK-1 | Feedback → Scout | MED | Engagement data → приоритет topic_cluster в Scout. Темы с высоким ER получают больше новостей |
| FBK-2 | QG калибровка | MED | Quality Gate: bell curve (70-100), не все 98+. Разделить compliance score и viral score |
| FBK-3 | Evergreen recycling | LOW | Посты с score >90 через 30 дней → recycle на другие платформы |
| FBK-4 | Hero Content Model | LOW | 1 long-form статья → 10 micro-pieces для разных платформ |
| ANA-4 | Observer: Analytics | LOW | Графики engagement по дням, платформам. Trend lines |
