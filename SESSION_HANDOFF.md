# Content Pipeline v2 — Полный статус для передачи в новую сессию

## Дата: 21 марта 2026

---

## ЧТО СДЕЛАНО

### Спринт 1: Content Pipeline на n8n ✅ DONE

**n8n workflows (все на Contabo VPS 30, n8n.timzinin.com):**

| ID | Название | Статус | Что делает |
|----|---------|--------|------------|
| RSQALdJch4WYZfit | Scout — Разведка | ACTIVE, cron 6ч | RSS (EN+RU) + HackerNews + GitHub → дедупликация SHA256 → PostgreSQL content.news_feed |
| ZQtg31g6dzAV0lXX | Writer — Автор | ACTIVE, cron 03:00 | Берёт лучшую новость → MiniMax M2.5 → Quality Gate (12 проверок) → content.posts |
| Z94O5uyaFEmrYGIJ | Illustrator — Художник | ACTIVE, cron 03:30 | Генерирует картинку через Gemini 2.5 Flash (Docker gemini-image-service:8800) → content.posts.image_url |
| DC3a34HOedbU7rVb | Dashboard — Дашборд | ACTIVE | Webhook GET /content-dashboard → SQL → HTML |
| umId4uV39dewR8Um | LinkedIn Pipeline v3 | ACTIVE | Старый, работает параллельно |
| JHZEnMf87VLN93pI | Threads News | ACTIVE | Старый, работает параллельно |

**PostgreSQL (schema content, в n8n_production):**
- `content.news_feed` — разведка (29+ записей)
- `content.posts` — нарративы (10 постов, все с Gemini-картинками в поп-арт стиле)
- `content.platform_posts` — адаптации (пока пусто)
- `content.engagement` — статистика (пока пусто)

**Credentials n8n:**
- PostgreSQL: id=ZoqVLKcTqNQGoDI5, name="Content Pipeline PG"
- MiniMax: id=XuWX7OQvQ3kOGJRj, name="MiniMax API v2"
- n8n логин: tim@timzinin.com / [REDACTED]

**Gemini Image Service:**
- Docker контейнер `gemini-image-service` в сети `zinin-corp_default`
- Порт 8800 внутри Docker network
- Принимает POST с {prompt, post_id} → вызывает OpenRouter Gemini → сохраняет PNG → возвращает URL
- Файлы: /opt/content-pipeline-images/ (bind mount в n8n контейнер)
- Nginx: corp.timzinin.com/content-images/ → /opt/content-pipeline-images/

**n8n REST API:**
- Правильный формат запуска: `{workflowData: wf, triggerToStartFrom: {name: "Schedule Daily", data: null}}` — БЕЗ runData!
- `startNodes` — устаревшее поле, не работает в n8n 2.12+

**Gallery:** corp.timzinin.com/gallery.html — 10 постов с картинками, текстами, ссылками на продукты
**Архитектура:** timzinin.com/content-pipeline/ — Mermaid диаграмма на GitHub Pages

### Спринт 1b: Обновление стратегий ✅ DONE

**Source of Truth = GitHub** https://github.com/TimmyZinin/smm-research-hub

Создано/обновлено 16 файлов:
- s00_global_strategy.md — мастер-стратегия (AI 80%, 3 языка, Publer, воронка)
- s01_linkedin.md — AI-фокус, CTA timzinin.com, карусели > видео
- s04_telegram_personal.md — 2 поста/день, AI-фокус
- s05_telegram_sborka.md — 2-3/нед, СБОРКА 100%
- s06_threads.md — **RU основной**, 5+/день, AI 80%
- s07_facebook.md — личный профиль (не страница), Publer push
- s09_vk.md — AI 80%, CTA timzinin.com
- s14_bluesky.md — EN, 2-3/день
- s15_mastodon.md — EN, 1/день
- s22_twitter.md — через Publer
- s30_email_digest.md — AI Digest на Beehiiv/Substack
- s31_telegram_bot.md — TG-бот CRM
- s32_threads_multilingual.md — 3 языка (RU + EN + TH), 5+/день каждый
- s33_publer_integration.md — гибридная схема API + Publer
- s34_chatplace.md — кодовое слово → подписка → ссылка
- 00_STRATEGY_AUDIT — полный пересмотр

### Спринт 2: Publer + Threads — ЧАСТИЧНО

**Publer:**
- Зарегистрирован, оплачен **Business план** (TRY 930/мес)
- Подключены: Facebook (Timofey Zinin), TikTok (Tim Zinin), Threads EN (Tim Zinin)
- **API key НЕ сгенерирован** — popup Generate API Key в Access & Login → нужно нажать кнопку и скопировать ключ
- Workspace name: Lisa Solovyova (исторически, нужно переименовать)

**Threads аккаунты:**
- @timzinin (RU, основной) — работает, API token на Contabo: THREADS_ACCESS_TOKEN
- timzinin_en (EN) — создан, залогинен в Threads, пароль: [REDACTED]
- timzinin_th (TH) — создан в Instagram, email привязан: [REDACTED], в Threads НЕ залогинен (проблема с паролем)

**Threads API:**
- App: Zinin Threads (ID: 881402564532283)
- Threads App ID: 1227588962261659
- Threads App Secret: [REDACTED]
- Redirect URI: https://sborka.work/threads-callback
- OAuth catcher на Contabo :8801 + nginx proxy настроен
- timzinin_en добавлен как Тестировщик Threads — статус "На рассмотрении"
- timzinin_th НЕ добавлен (не удалось выбрать радиокнопку через автоматизацию)

**Substack:**
- Регистрация начата (tim.zinin@gmail.com), код подтверждения 127998 был в Gmail
- НЕ завершена

**Beehiiv:**
- Русский номер телефона не проходит верификацию — отложен

---

## ЧТО ОСТАЛОСЬ СДЕЛАТЬ

### Спринт 2 (завершить):
1. **Publer API key** — зайти в Publer → Settings → Access & Login → прокрутить вниз → Generate API Key → скопировать → сохранить на Contabo
2. **Threads EN OAuth token** — дождаться одобрения тестировщика → OAuth → получить access token → сохранить на Contabo
3. **Threads TH** — войти в Threads через timzinin_th (нужен сброс пароля через email [REDACTED]) → добавить как тестировщика → OAuth → token
4. **Substack** — завершить регистрацию "AI Digest"

### Спринт 3: Adapter workflow (n8n)
1. Создать workflow "Adapter" — берёт готовый пост (text + image + product_url) и адаптирует:
   - Telegram: 600-1000 символов + ссылка (preview через OG-теги)
   - LinkedIn: 1000-1500 символов + ссылка в комментарии
   - Threads RU: 300-500 символов, 5+/день
   - Threads EN: перевод RU → EN, 5+/день
   - Bluesky: 250-300 символов EN + ссылка
   - Mastodon: 500 символов EN + хештеги
   - VK: 800-1500 символов RU + картинка
   - Facebook: 600-1000 символов RU (через Publer)
   - TikTok: текст для описания видео (через Publer)
2. Результат → content.platform_posts с scheduled_at
3. Стратегии из s00-s34 = конфиг для адаптера

### Спринт 4: Publisher + HITL
1. Создать workflow "Publisher" — HITL через Approval Bot (:8791) → публикация
2. Гибридная схема:
   - Прямые API (бесплатно): Telegram, Bluesky, Mastodon, Threads RU
   - Publer API: Facebook, TikTok, Threads EN
3. Telegram: ссылка с OG-preview (каждый пост = отдельная HTML-страница с OG-тегами)
4. LinkedIn: пост + автоматический комментарий со ссылкой

### Спринт 5: ChatPlace + Email + TG-бот
1. ChatPlace.io — механика кодового слова для IG/TikTok/YouTube
2. Substack/Beehiiv — AI Digest ежедневная рассылка
3. TG-бот CRM

### Спринт 6: Analyst + Feedback
1. Сбор engagement с платформ API
2. Daily report в TG
3. Feedback loop: лучшие темы → приоритет в Scout

---

## КРИТИЧЕСКИЕ CREDENTIALS

| Что | Где |
|-----|-----|
| n8n | tim@timzinin.com / [REDACTED] |
| Facebook (Meta) | timiich@yandex.ru / [REDACTED] |
| Threads App Secret | [REDACTED] |
| Threads App ID | 1227588962261659 |
| Instagram timzinin_en | timzinin_en / [REDACTED] |
| Instagram timzinin_th | timzinin_th / [REDACTED] (пароль может не работать, нужен сброс) |
| OpenRouter | [REDACTED] |
| Publer | tim.zinin@gmail.com (Google OAuth), Business план |

## ХУКИ (обновлённые)

- bash-pretooluse-guard.py — объединяет secret-scanner, dangerous-command-blocker, process-kill-blocker, sborka-prod-blocker, no-delegation-to-user
- sprint-completion-checker.py — Stop hook, напоминает о незавершённых спринтах
- Feedback memories: no_imperative_commands, max_2_attempts, meta_dev_console_radio, instagram_needs_email, no_close_user_tabs, publer_api_paid

## КЛЮЧЕВЫЕ РЕШЕНИЯ

1. Source of Truth = GitHub (smm-research-hub), не локальная копия
2. Контент-микс: AI 80% / проекты 20%
3. Threads: RU основной (5+/день), EN + TH дополнительные (5+/день каждый)
4. Publer для Facebook/TikTok/Threads EN, прямые API для TG/Bluesky/Mastodon/Threads RU
5. Email = отдельное медиа "AI Digest", НЕ часть воронки подписки
6. ChatPlace.io для видео-воронки (кодовое слово → подписка → ссылка)
7. Gemini image через Docker контейнер в n8n network (обход проблемы base64 в sandbox)
8. Anti-AI writing rules в промпте Writer (запрет тире, "это не просто", сравнительных оборотов)
9. Поп-арт стиль картинок (красный/жёлтый, halftone, fisheye, девушки каждый 3-й пост)
