# Runbook — диагностика и восстановление

> Операционные процедуры для content pipeline. Обновлено 31 марта 2026.

## Почему пост не вышел?

```mermaid
flowchart TD
    START["Пост не опубликован"] --> CHECK_STATUS["Проверить статус в БД"]
    CHECK_STATUS --> |"draft"| CURATOR["Curator не одобрил<br/>или freeze активен"]
    CHECK_STATUS --> |"scheduled"| PUBLISHER["Publisher v3 не подхватил"]
    CHECK_STATUS --> |"sending"| STUCK["Пост застрял в sending"]
    CHECK_STATUS --> |"failed"| FAILED["3 retry исчерпаны"]
    CHECK_STATUS --> |"skipped"| SKIPPED["Quality Gate отклонил<br/>или Curator пропустил"]

    PUBLISHER --> PUB_CHECK["Publisher v3 активен?"]
    PUB_CHECK --> |"нет"| ACTIVATE["Активировать в n8n"]
    PUB_CHECK --> |"да"| CRON_CHECK["scheduled_at <= NOW()?"]
    CRON_CHECK --> |"нет"| WAIT["Ждать scheduled_at"]
    CRON_CHECK --> |"да"| QUEUE["В очереди — LIMIT 1 за тик"]

    STUCK --> MANUAL["Ручное исправление:<br/>UPDATE SET status='scheduled'<br/>WHERE id=X AND status='sending'<br/>AND published_at IS NULL"]

    FAILED --> ERROR["Проверить error в БД"]
    ERROR --> |"quality_gate"| QG["Текст не прошёл фильтр"]
    ERROR --> |"HTTP 400"| API["Проблема API платформы"]
    ERROR --> |"HTTP 401"| AUTH["Токен/ключ невалиден"]

    SKIPPED --> SKIP_ERROR["Проверить error"]
    SKIP_ERROR --> |"quality_gate: profanity"| FIX_TEXT["Убрать мат из текста"]
    SKIP_ERROR --> |"quality_gate: AI-tell"| FIX_PCT["Убрать фейковые проценты"]
```

## Команды диагностики

### Статус поста
```sql
SELECT id, platform, status, error, retries, post_external_id
FROM content.platform_posts WHERE id = <ID>;
```

### Все scheduled сейчас
```sql
SELECT id, platform, scheduled_at FROM content.platform_posts
WHERE status = 'scheduled' ORDER BY scheduled_at;
```

### Publisher v3 статус
```sql
SELECT active FROM workflow_entity WHERE id = 'ErbbScuvxWHLX1np';
```

### Последние ошибки
```bash
docker logs publisher-service --tail 50 2>&1 | grep -E "ERROR|FAIL|WARNING"
```

## Восстановление

### Пост застрял в `sending`
```sql
-- Проверить что пост не опубликован (нет external_id)
SELECT id, post_external_id FROM content.platform_posts
WHERE id = <ID> AND status = 'sending';

-- Если external_id пуст — вернуть в scheduled
UPDATE content.platform_posts SET status = 'scheduled'
WHERE id = <ID> AND status = 'sending' AND post_external_id IS NULL;
```

### Emergency freeze (остановить все публикации)
```sql
UPDATE content.platform_posts SET status = 'draft'
WHERE status = 'scheduled';
```
Также: деактивировать Publisher v3 в n8n.

### Откат publisher-service
```bash
# На Contabo:
docker cp /opt/publisher-service/main.py.bak publisher-service:/app/main.py
docker restart publisher-service
```

### Replay одного поста
```sql
UPDATE content.platform_posts
SET status = 'scheduled', retries = 0, error = NULL,
    scheduled_at = NOW() + INTERVAL '10 minutes'
WHERE id = <ID>;
```
**ВАЖНО:** Publisher v3 должен быть активен. Quality Gate проверит текст автоматически.

## Мониторинг

### Текущее состояние pipeline
```sql
SELECT status, count(*) FROM content.platform_posts GROUP BY status ORDER BY status;
```

### Посты без картинок (image-post без image_url)
```sql
SELECT id, platform FROM content.platform_posts
WHERE include_image = true AND image_url IS NULL AND status NOT IN ('skipped');
```

## Известные инциденты

### 30 марта 2026
- 4 debug сообщения отправлены в @timofeyzinin канал (Claude тестировал quality gate через production channel)
- Post 51 ("нахер") опубликован — quality gate был в неправильном файле контейнера
- Post 458 опубликован normal pipeline (freeze не учёл новые scheduled rows)

### 31 марта 2026
- Post 471 (post 45, telegram) опубликован cron — Curator перезаписал freeze (draft → scheduled)
- Publisher v3 деактивирован для предотвращения дальнейших незапланированных публикаций
- 18 rows заморожены в draft

### Row 393 (telegram, post 41)
- Статус: draft (заморожен)
- Ошибка: HTTP 400 через /publish endpoint, но работает через прямой API вызов
- Причина: не определена
- Рекомендация: пересоздать пост с чистым текстом (убрать "97%")
