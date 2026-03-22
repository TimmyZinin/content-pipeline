# CTA / Link Placement Matrix

> Source of truth для размещения ссылок по платформам.
> Основан на стратегиях smm-research-hub (s01-s15).

## Placement Rules

| Платформа | Где ссылка | Формат | Частота CTA | Штраф за ссылку в теле | Источник |
|-----------|-----------|--------|-------------|----------------------|---------|
| Telegram | Body (HTML anchor) | `<a href="url">Product</a>` | Soft 1/нед, прямой 1/2 нед | Нет штрафа, но голые URL запрещены | s04:149,254,339 |
| Threads RU | First reply или "link in bio" | CTA текст + ссылка в reply | По стратегии | -30-50% охвата за ссылку в теле | s06:37,212 |
| Threads EN | First reply или "link in bio" | Аналогично RU | По стратегии | -30-50% | s06:37 |
| LinkedIn | Первый комментарий | Ссылка в comment_text | По стратегии | -40-50% | s01:21 |
| Facebook | Первый комментарий | Ссылка в comment_text | По стратегии | -50-80% | s07:50,165 |
| VK | Body | Прямая ссылка в тексте | Max 1/5 постов прямой CTA | Нет данных о штрафе | s09:228-230 |
| Bluesky | Body | Прямая ссылка | С каждым постом | Нет | s14 |
| Dev.to | Body (conclusion) | UTM ссылка, 1-2 CTA | В каждой статье | Нет | s11 |
| Hashnode | Body + canonical | CTA + canonical URL | В каждой статье | Нет | s13 |
| Mastodon | Body | Прямая ссылка + хэштеги | С каждым постом | Нет | s15 |
| Write.as | Body | Прямая ссылка | В каждом эссе | Нет | s20 |
| Minds | Body | Прямая ссылка + хэштеги | С каждым постом | Нет | — |
| Nostr | Body | Прямая ссылка | С каждым постом | Нет | — |

## Implementation Status

### Этап 1: Body links (code written, not yet verified)
Platforms: Telegram, VK, Bluesky, Mastodon, Dev.to, Hashnode, Write.as, Minds, Nostr
Method: Publisher Service вставляет link_url в текст перед вызовом адаптера
Telegram: HTML `<a href>` anchor. Остальные: append URL.

### Этап 2: Post-publish comment/reply (NOT YET IMPLEMENTED)
Platforms: Threads RU, Threads EN, Facebook, LinkedIn
Method: после publish основного поста → отдельный API call для comment/reply
Gap: Publisher Service и n8n workflow не поддерживают multi-step post-publish

### Этап 3: LinkedIn (Sprint 4G)
Design only, no implementation.

## Incident Note

22 мар 2026: `/test-publish` endpoint отправлял реальные посты в боевые соцсети.
Endpoint заблокирован (HTTP 403). Для тестирования используется только code review и local adapter testing.
