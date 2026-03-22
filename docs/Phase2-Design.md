# Phase 2 Design: Comment/Reply Orchestration

> Design doc для post-publish comment/reply steps.
> НЕ implementation — только архитектура.

## Проблема

Для Facebook и Threads ссылка должна быть не в теле поста, а в первом комментарии или reply. Текущий Publisher Service делает только один HTTP вызов (publish). Нужен второй шаг.

## Threads RU/EN — Reply Flow

**Стратегия (s06):** ссылка в first reply, не в теле (штраф -30-50%).

**Текущий flow:**
```
Curator → scheduled → Publisher Service → publish (text+image) → sent
```

**Целевой flow:**
```
Curator → scheduled → Publisher Service → publish (text+image) → get post_id
→ Publisher Service → reply (reply_text + link) → sent
```

**Реализация:**
- Threads RU (direct API): create container → publish → **create reply container → publish reply**
- Threads EN (Publer): Publer не поддерживает reply post-publish → **gap**, нужно альтернативное решение

**Data model:** `reply_text` уже есть в platform_posts. Достаточно.

**Изменения в Publisher Service:**
- `publish_one()` для threads_ru: после основного publish → API call create_reply → publish_reply
- Возврат: {status: "ok", post_id: main_post_id, reply_id: reply_id}

## Facebook — First Comment Flow

**Стратегия (s07):** ссылка в первом комментарии (штраф -50-80% за ссылку в теле).

**Текущий flow:** Publer публикует только text+image.

**Целевой flow:**
```
Publer publish (text+image) → get Publer post_id
→ Publer comment API или Graph API → add first comment with link
```

**Реализация:**
- Вариант A: Publer bulk с комментарием (если Publer API поддерживает)
- Вариант B: После Publer publish → Graph API `POST /{post_id}/comments`
- Вариант B требует Page token или user token с publish_actions permission

**Data model:** `comment_text` уже есть. Достаточно.

## LinkedIn — Sprint 4G Boundary

**Стратегия (s01):** ссылка в первом комментарии.

**НЕ реализуем сейчас.** LinkedIn = отдельный standalone pipeline.
Sprint 4G: research как подключить к content bank.

**Граница:** Publisher v3 не должен знать про LinkedIn. LinkedIn pipeline сам решает comment logic.

## n8n Workflow Changes (Phase 2)

Publisher v3 workflow остаётся 7 нод. Изменения только в Publisher Service:
- `publish_one()` получает capability: multi-step publish
- Для threads_ru: 2 API calls (create+reply)
- Для facebook: 1 Publer call + 1 comment API call
- n8n не меняется — только result parsing может показать reply_id

## Rollout Phase 2

| Этап | Платформы | Что добавляется |
|------|-----------|----------------|
| 2a | Threads RU | Reply с ссылкой после основного поста |
| 2b | Facebook | First comment с ссылкой после Publer publish |
| 2c | Threads EN | Зависит от Publer reply support |

## Не делаем

- LinkedIn implementation
- Multi-step warm-up chains (стратегия не требует)
- Отдельный n8n workflow для comments
- Новые таблицы в БД
