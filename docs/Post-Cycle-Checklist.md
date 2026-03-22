# Post-Cycle Verification Checklist

> Выполнять после каждого нового Curator+Publisher цикла.
> Особенно после расширения allowlist.

## 1. DB Status Check

```sql
SELECT platform, status, COUNT(*)
FROM content.platform_posts
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY platform, status
ORDER BY platform, status;
```

**Ожидаемое:**
- Allowlisted платформы: `sent` (не `failed`, не `sending`)
- Остальные: `scheduled` (остались без публикации) или `skipped`
- Нет `sending` (зависших)

## 2. External Verification (allowlisted platforms)

| Платформа | Что проверить | Как |
|-----------|--------------|-----|
| Telegram | Пост в @timofeyzinin, ссылка кликабельна | Открыть канал |
| Write.as | Пост на write.as/timzinin, ссылка в конце | Открыть профиль |
| Minds | Пост на Minds профиле | Открыть профиль |

## 3. Link Verification

- [ ] Ссылка присутствует в посте
- [ ] Формат ссылки правильный (TG: HTML anchor, остальные: plain URL)
- [ ] Ссылка кликабельна
- [ ] Нет голых UTM-параметров (TG)

## 4. No Noise Check

- [ ] Нет **новых** `failed` записей (filter: `created_at > last cycle start`). Старые failed от cleanup 22 мар — игнорировать
- [ ] Нет TG alerts от dead letter
- [ ] Нет дубликатов

## 5. Signals

| Signal | Meaning |
|--------|---------|
| Allowlisted posts = `sent` | ✅ Phase 1 working |
| Non-allowlisted = `scheduled` | ✅ Correctly filtered |
| Any `failed` for allowlisted | ⚠️ Investigate |
| Any `sending` stuck | ❌ Anti-duplicate issue |
| TG dead letter alert | ❌ Retry exhausted |
| Duplicate posts | ❌ Rollback and investigate |
