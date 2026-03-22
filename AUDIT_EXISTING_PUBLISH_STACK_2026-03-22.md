# Audit: Existing Social Publishing Stack

Date: 2026-03-22
Scope: existing social publishing systems across local workspace, memory markdown files, and known GitHub repos
Purpose: give the next Claude session a grounded map of what already exists so it does not re-invent connectors or rebuild the stack from zero

## Executive Summary

There is not one publishing system. There are at least three generations of it:

1. `auto-publisher` = the last clearly working multi-platform publishing core.
2. `content-factory` = a more systematic successor with queue, scheduler, analytics, feedback, and publishers, but historically unstable / partially dead as runtime.
3. `content-pipeline` on n8n = the newest attempt to move the pipeline into n8n, but most of the real publisher state currently lives in live n8n workflows rather than in versioned code.

The key conclusion:

- do not write connectors from scratch;
- treat `auto-publisher` as the existing transport layer;
- treat `smm-research-hub` as strategy source of truth;
- treat `n8n` as orchestration, not as the place to re-implement every platform adapter in fragile expressions.

## Main Repositories And Assets

### 1. `auto-publisher`

Path: [auto-publisher](/Users/timofeyzinin/auto-publisher)
GitHub: `TimmyZinin/auto-publisher`

This is the strongest existing operational asset for publishing.

Important files:

- [auto_publisher.py](/Users/timofeyzinin/auto-publisher/auto_publisher.py)
- [gatekeeper.py](/Users/timofeyzinin/auto-publisher/gatekeeper.py)
- [schedule_watcher.py](/Users/timofeyzinin/auto-publisher/schedule_watcher.py)
- [review_handler.py](/Users/timofeyzinin/auto-publisher/review_handler.py)
- [run.sh](/Users/timofeyzinin/auto-publisher/run.sh)
- [adapters](/Users/timofeyzinin/auto-publisher/adapters)
- [linkedin_pipeline/linkedin_pipeline.py](/Users/timofeyzinin/auto-publisher/linkedin_pipeline/linkedin_pipeline.py)

What it already has:

- cron-driven publishing runtime
- calendar-driven publish engine
- platform adapter loading
- state tracking
- gatekeeper pre-publish validation
- stale/overdue watcher
- review/regenerate HTTP layer
- separate LinkedIn pipeline

Adapters already present:

- Telegram
- Threads
- VK
- Bluesky
- Mastodon
- Dev.to
- Hashnode
- Facebook
- Tumblr
- Write.as
- plus additional adapters such as Minds and Nostr

High confidence conclusion:

- this repo already contains the publishing connectors you need for the core text/article platforms;
- it should be reused, not replaced.

### 2. `smm-research-hub`

Path: [smm-research-hub](/Users/timofeyzinin/smm-research-hub)
GitHub: `TimmyZinin/smm-research-hub`

This is the strategic source of truth.

Important files:

- [s00_global_strategy.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s00_global_strategy.md)
- [s01_linkedin.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s01_linkedin.md)
- [s04_telegram_personal.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s04_telegram_personal.md)
- [s06_threads.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s06_threads.md)
- [s07_facebook.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s07_facebook.md)
- [s09_vk.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s09_vk.md)
- [s11_devto.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s11_devto.md)
- [s13_hashnode.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s13_hashnode.md)
- [s14_bluesky.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s14_bluesky.md)
- [s15_mastodon.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s15_mastodon.md)
- [s16_tumblr.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s16_tumblr.md)
- [s20_writeas.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s20_writeas.md)
- [s22_twitter.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s22_twitter.md)
- [s33_publer_integration.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s33_publer_integration.md)

What it contains:

- platform-specific strategies
- cadence and content rules
- language rules
- CTA and link placement logic
- distribution recommendations
- Publer split for platforms where direct API is not preferred

High confidence conclusion:

- strategy already exists for far more platforms than the current live publisher actually supports cleanly;
- strategy should remain source of truth for platform behavior, not scattered inline prompts in live workflows.

### 3. `content-factory`

GitHub: `TimmyZinin/content-factory`

Observed structure from remote repo:

- `services/scheduler.py`
- `services/feedback.py`
- `services/analytics.py`
- `services/quality_gate.py`
- `services/publishers/*`
- `config/strategies`
- `dashboard/factory.html`
- `docs/content-systems-map.html`

What this indicates:

- there was already an attempt to build a more systematic content engine with queue, retry, stagger scheduling, analytics, and feedback loop;
- this was more ambitious than `auto-publisher`;
- it appears to have been a successor architecture, but not the most reliable live runtime.

Important evidence:

- the systems map explicitly marks `auto-publisher` as active and `content-factory` as dead/failed at that point.

### 4. `content-pipeline`

Path: [content-pipeline](/Users/timofeyzinin/content-pipeline)
GitHub: `TimmyZinin/content-pipeline`

This is the newest n8n-based attempt.

Important files:

- [index.html](/Users/timofeyzinin/content-pipeline/index.html)
- [SESSION_HANDOFF.md](/Users/timofeyzinin/content-pipeline/SESSION_HANDOFF.md)

Current state:

- the repo mostly documents the architecture;
- the actual publisher logic is mostly being edited live inside n8n;
- the repo is not yet the full versioned source of the real publisher behavior.

High confidence conclusion:

- `content-pipeline` is currently documentation plus live workflow references, not a full codebase replacement for `auto-publisher`.

## Historical Evolution

### Generation 1: Legacy calendar-driven publishing

Core pattern:

- `content_calendar.json` as publish source
- `auto_publisher.py` as runtime
- `state.json` as published state
- many adapters under one engine

Strengths:

- broad platform coverage
- already-working direct integrations
- simple cron operation

Weaknesses:

- strategy and publishing logic were loosely coupled
- calendar noise and legacy entries caused operational spam
- some failures were aggregated badly
- duplicate/spam incidents happened historically

### Generation 2: Structured content engine

Core pattern:

- queue
- scheduler
- quality gate
- analytics
- feedback loop
- machine-readable configs

Strengths:

- much better architecture on paper
- cleaner closed-loop model

Weaknesses:

- historically unstable as runtime
- seems not to have become the long-term operational core

### Generation 3: n8n-first content pipeline

Core pattern:

- Scout -> Writer -> Illustrator -> Adapter -> Publisher -> Analyst
- PostgreSQL schema `content.*`
- direct HTTP nodes for publish actions

Strengths:

- very good orchestration fit
- visual pipeline
- natural for retries, branching, dashboards

Weaknesses:

- live-edited in UI
- workflow state not properly versioned in git
- platform publishing logic started being rebuilt inside expressions and nodes instead of reusing stable adapter code

## Existing Publish Architecture, In Practical Terms

The real system already has the following reusable layers.

### Layer A: Strategy

Source:

- `smm-research-hub`

Responsibility:

- define platform-specific behavior
- define direct API vs Publer split
- define link rules, cadence, language, and format

### Layer B: Transport / Adapters

Source:

- `auto-publisher/adapters/*.py`

Responsibility:

- turn text + image + metadata into platform-specific API calls

This layer already exists.

### Layer C: Validation / Gating

Source:

- `auto-publisher/gatekeeper.py`
- `gatekeeper_agent_spec.md`
- Approval Bot-related flows

Responsibility:

- image presence
- URL checks
- minimum text lengths
- UTM expectations
- review/approval path where required

### Layer D: Scheduling / Routing

Source:

- legacy cron in `auto-publisher`
- more advanced queue logic in `content-factory`
- newest orchestration attempt in n8n

Responsibility:

- choose when to publish
- choose where to publish
- stagger posts
- retry or dead-letter on failure

### Layer E: Verification / Observability

Source:

- `schedule_watcher.py`
- content-factory systems map and audits
- handoff docs

Responsibility:

- detect overdue content
- detect stale platforms
- inspect actual publish results

## What Was Already Solved

These are the problems that do not need a fresh greenfield implementation.

### Already solved or mostly solved

- direct publishing adapters for major text and article platforms
- direct Threads publish flow in Python
- direct Bluesky publish flow in Python
- direct VK flow in Python
- Dev.to and Hashnode article publishing
- Telegram bot-based publishing
- Write.as and Tumblr adapters
- gatekeeper-style pre-publish checks
- watcher / alerting model
- review/regenerate HTTP layer
- strategy documentation for 29+ platforms
- direct-vs-Publer architectural split

### Likely reusable with moderate cleanup

- LinkedIn-specific pipeline logic
- approval flow integration
- ownership-aware routing
- stagger scheduling logic from `content-factory`

### Clearly unstable or incomplete

- live n8n publisher logic as current source of truth
- content-factory as a proven production runtime
- any workflow that updates publish status before platform verification

## Publer Position In The Stack

Publer is not the whole solution. It was already defined as a targeted broker.

From strategy and handoff materials, the intended split was:

- direct APIs for platforms where direct adapters are practical and already exist
- Publer only for platforms where direct publish path is unavailable, awkward, or strategically centralized there

Observed intended Publer targets:

- Facebook
- TikTok
- Threads EN
- optionally Twitter/X or other externally brokered channels depending on later strategy

Conclusion:

- Publer should stay narrow;
- it should not become the general publishing brain.

## Key Operational Problems Found

### 1. Too many overlapping systems

At different times the stack included:

- old calendar-driven publishing
- content-factory queue model
- Approval Bot
- LinkedIn-specific pipeline
- AI Corp / Lisa partial publisher
- n8n-based pipeline

This overlap is the primary source of confusion.

### 2. Live runtime diverged from git

Especially for the new n8n publisher:

- logic is being edited live;
- repo contains documentation, not the full executable source of truth;
- next sessions cannot reliably diff or restore state.

### 3. Strategy, transport, and orchestration were mixed together

The healthiest separation already exists in fragments:

- strategy in `smm-research-hub`
- transport in `auto-publisher`
- orchestration in n8n or scheduler

But the current live n8n work started collapsing these concerns into node expressions.

### 4. Dual approval models are unresolved

There is a strong approval model in agent rules and Approval Bot files.
There is also a newer “auto-publish because quality is high enough” drift in n8n docs.

This must be resolved intentionally instead of ad hoc.

### 5. Existing good code is at risk of being bypassed

The Python adapters are easier to reason about than large inline n8n expressions.
Rebuilding them in n8n increases fragility without adding real product value.

## Recommended Baseline For The Next Session

The next Claude session should start from this model:

### Keep

- `smm-research-hub` as platform strategy source of truth
- `auto-publisher` adapters as transport layer
- Publer only for brokered platforms
- n8n as orchestration and scheduling layer

### Do not do

- do not rewrite connectors from scratch inside n8n
- do not make live n8n UI the only source of truth
- do not mix two-step platform publish logic through “let both nodes run and ignore errors”
- do not mark DB rows as published before real verification

### Preferred target architecture

1. `n8n` selects due post and route.
2. `n8n` calls one stable publish transport layer.
3. Transport layer uses existing adapter code.
4. Result is verified against platform response or follow-up check.
5. Only then status is updated in DB.

### Minimal transport split

Direct adapters:

- Telegram
- Threads RU
- VK
- Bluesky
- Dev.to
- Hashnode
- Write.as
- Tumblr
- Mastodon if credentials are valid

Brokered via Publer:

- Facebook
- Threads EN
- TikTok

## Practical Starting Point

If the goal is “minimal complexity without rebuilding everything”, the cleanest path is:

1. stop treating current live n8n publisher expressions as the real publish implementation;
2. recognize `auto-publisher` as the existing connector library;
3. either:
   - call its adapters directly from a small service/API, or
   - reuse its modules in a thin wrapper that n8n calls;
4. keep n8n only for:
   - schedule
   - branching
   - persistence
   - dashboard
   - retries
   - verification coordination

This preserves prior investment and removes the need to write connectors again.

## Concrete Files To Read First In The Next Session

### Must-read

- [auto_publisher.py](/Users/timofeyzinin/auto-publisher/auto_publisher.py)
- [gatekeeper.py](/Users/timofeyzinin/auto-publisher/gatekeeper.py)
- [schedule_watcher.py](/Users/timofeyzinin/auto-publisher/schedule_watcher.py)
- [linkedin_pipeline.py](/Users/timofeyzinin/auto-publisher/linkedin_pipeline/linkedin_pipeline.py)
- [s00_global_strategy.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s00_global_strategy.md)
- [s33_publer_integration.md](/Users/timofeyzinin/smm-research-hub/smm_audits/md/s33_publer_integration.md)
- [2026-03-13-social-multiagent-status-and-plan.md](/Users/timofeyzinin/plans/2026-03-13-social-multiagent-status-and-plan.md)
- [2026-03-13-full-social-migration-plan.md](/Users/timofeyzinin/plans/2026-03-13-full-social-migration-plan.md)
- [content-factory-audit.md](/Users/timofeyzinin/content-factory-audit.md)
- [gatekeeper_agent_spec.md](/Users/timofeyzinin/gatekeeper_agent_spec.md)
- [SESSION_HANDOFF.md](/Users/timofeyzinin/content-pipeline/SESSION_HANDOFF.md)

### Important platform adapter files

- [telegram.py](/Users/timofeyzinin/auto-publisher/adapters/telegram.py)
- [threads.py](/Users/timofeyzinin/auto-publisher/adapters/threads.py)
- [vk.py](/Users/timofeyzinin/auto-publisher/adapters/vk.py)
- [bluesky.py](/Users/timofeyzinin/auto-publisher/adapters/bluesky.py)
- [mastodon.py](/Users/timofeyzinin/auto-publisher/adapters/mastodon.py)
- [devto.py](/Users/timofeyzinin/auto-publisher/adapters/devto.py)
- [hashnode.py](/Users/timofeyzinin/auto-publisher/adapters/hashnode.py)
- [facebook.py](/Users/timofeyzinin/auto-publisher/adapters/facebook.py)
- [tumblr.py](/Users/timofeyzinin/auto-publisher/adapters/tumblr.py)
- [writeas.py](/Users/timofeyzinin/auto-publisher/adapters/writeas.py)

## Bottom Line

You do not need a new greenfield publisher.

You already have:

- strategy
- adapters
- gating
- watcher logic
- approval concepts
- a partially successful migration plan

What is missing is not connectors.

What is missing is a single chosen architecture where:

- strategy lives in one place,
- transport lives in one place,
- orchestration lives in one place,
- and production state is versioned rather than trapped in a live UI.
