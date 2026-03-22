# Content Pipeline v2 — Source of Truth

> Автоматическая контент-система Tim Zinin на n8n
> Обновлено: 22 марта 2026

## Policies

- **docs/ = source of truth.** Wiki = mirror. При расхождении — docs/ приоритет.
- **Timezone:** хранение в UTC, отображение пользователю в Istanbul (UTC+3). Подписывать везде.
- **Definition of Done:** runtime changed + repo updated + docs updated + changelog updated + verification evidence.

## Оглавление

- [[Architecture]] — архитектура, Mermaid-диаграммы, data flow
- [[Workflows]] — все 10 n8n workflows с описанием нод
- [[Database]] — PostgreSQL схема, статусы, таблицы
- [[Platforms]] — все платформы, расписания, API
- [[Curator]] — логика распределения, Tier-система, дедупликация
- [[Publisher]] — текущий статус, проблемы, план рефакторинга
- [[Backlog]] — бэклог спринтов 4-6
- [[Changelog]] — лог изменений

## Текущий статус

```mermaid
flowchart LR
    S[Scout ✅] --> W[Writer ✅]
    W --> I[Illustrator ✅]
    I --> A[Adapter ✅\n14 платформ]
    A --> C[Curator ✅\nTier + dedup]
    C --> P[Publisher ⚠️\n2/10]
    P --> AN[Analyst ❌]
    AN --> F[Feedback ❌]
```

## Active Workflows (n8n)

| # | Компонент | Статус | n8n ID | Cron/Trigger |
|---|-----------|--------|--------|-------------|
| 1 | Scout | ✅ Active | RSQALdJch4WYZfit | каждые 6ч |
| 2 | Writer | ✅ Active | ZQtg31g6dzAV0lXX | 06:00 Istanbul |
| 3 | Illustrator | ✅ Active | Z94O5uyaFEmrYGIJ | 06:30 Istanbul |
| 4 | Adapter | ✅ Active | NJoPcdp38ZU0dQwG | 07:00 Istanbul |
| 5 | Curator | ✅ Active | EYPcT5B4rLmQRQBM | 07:30 Istanbul |
| 6 | Publisher v2 | ⚠️ Partial (2/10) | 1cD3qXs2XZkgcQyt | */30 09-03 Istanbul |
| 7 | Dashboard | ✅ Active | DC3a34HOedbU7rVb | webhook |
| 8 | Curator Preview | ✅ Active | JzYcKrUfXheatEi1 | webhook |
| 9 | Observer | ✅ Active | V2wnna7ACw5iSqdi | webhook |
| 10 | Кнопочные (4 шт) | ✅ Active | UR2K/rejq/JLrN/RjCO | manual |

## Инфраструктура

**n8n:** n8n.timzinin.com (Contabo Docker :5678)
**Observer:** n8n.timzinin.com/webhook/observer
**Dashboard:** n8n.timzinin.com/webhook/content-dashboard
**Curator Preview:** n8n.timzinin.com/webhook/curator-preview
**Архитектура:** timzinin.com/content-pipeline/ (GitHub Pages)
**Corp Dashboards:** corp.timzinin.com
**Curator Config:** /opt/content-pipeline/curator-config.json
**PostgreSQL:** internal :5432 (n8n Docker Compose)
**Gemini Image:** internal :8800 (Docker)

## Связанные репозитории

| Репозиторий | Роль |
|------------|------|
| TimmyZinin/content-pipeline | Этот репо. Docs, архитектура, wiki |
| TimmyZinin/smm-research-hub | Source of truth для стратегий платформ (s00-s34) |
| TimmyZinin/auto-publisher | Transport layer: 15 Python адаптеров для публикации |
| TimmyZinin/content-factory | Legacy. Scheduler.py переиспользуется, остальное — архив |
