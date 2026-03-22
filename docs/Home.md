# Content Pipeline v2 — Source of Truth

> Автоматическая контент-система Tim Zinin на n8n
> Обновлено: 22 марта 2026

## Обзор

Content Pipeline v2 — полностью автоматизированный пайплайн создания и публикации контента на 10+ социальных платформ. Построен на n8n (self-hosted, Contabo VPS 30).

## Оглавление

- [[Architecture]] — архитектура, Mermaid-диаграммы, data flow
- [[Workflows]] — все n8n workflows с описанием нод
- [[Database]] — PostgreSQL схема, статусы, таблицы
- [[Platforms]] — все платформы, расписания, API, credentials
- [[Curator]] — логика распределения, Tier-система, дедупликация
- [[Publisher]] — текущий статус, проблемы, план рефакторинга
- [[Backlog]] — бэклог спринтов 3-6
- [[Changelog]] — лог изменений

## Текущий статус

```mermaid
flowchart LR
    S[Scout ✅] --> W[Writer ✅]
    W --> I[Illustrator ✅]
    I --> A[Adapter ✅]
    A --> C[Curator ✅]
    C --> P[Publisher ⚠️]
    P --> AN[Analyst ❌]
    AN --> F[Feedback ❌]
```

| Компонент | Статус | n8n ID |
|-----------|--------|--------|
| Scout | ✅ Active | RSQALdJch4WYZfit |
| Writer | ✅ Active | ZQtg31g6dzAV0lXX |
| Illustrator | ✅ Active | Z94O5uyaFEmrYGIJ |
| Adapter | ✅ Active | NJoPcdp38ZU0dQwG |
| Curator | ✅ Active | EYPcT5B4rLmQRQBM |
| Publisher v2 | ⚠️ Partial | 1cD3qXs2XZkgcQyt |
| Dashboard | ✅ Active | DC3a34HOedbU7rVb |
| Curator Preview | ✅ Active | JzYcKrUfXheatEi1 |

## Инфраструктура

| Компонент | Где | Порт |
|-----------|-----|------|
| n8n | Contabo Docker | :5678 |
| PostgreSQL | n8n Docker Compose | :5432 (internal) |
| Gemini Image Service | Docker | :8800 (internal) |
| Content Dashboard | corp.timzinin.com | webhook |
| Архитектура | timzinin.com/content-pipeline/ | GitHub Pages |
