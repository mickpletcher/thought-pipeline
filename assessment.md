# Thought Pipeline Assessment

Last reviewed: 2026-05-07

## Purpose

This file is the repo level source of truth for the current project state. It is meant to save future work from having to rescan the full repo to understand what exists, what is missing, and what should happen next.

## Repo Summary

The repo currently describes a larger product vision than it implements.

The README presents Thought Pipeline as an iPhone to Apple Shortcuts to n8n to LLM idea capture and enrichment system with structured storage and optional GitHub output.

The actual tracked implementation is much smaller:

1. `README.md`
   Product vision, target architecture, installation outline, and sample payloads.
2. `iPhone-shortcut.json`
   Canonical payload example for an iPhone Shortcut.
3. `schemas/`
   Input and output JSON schemas for the MVP contract.
4. `samples/`
   Checked in sample input and sample output payloads.
5. `scripts/`
   Local enrichment, sample posting, and contract validation helpers.
6. `workflows/`
   n8n MVP workflow export draft.
7. `requirements.txt`
   Python dependencies for local validation and replay.
8. `LICENSE`
9. `.gitignore`

## What Is Implemented

### 1. Repo positioning

The project goal is clear. The README explains the intended user flow and the end state well enough for someone to understand the product direction quickly.

### 2. Shortcut payload shape

The shortcut sample establishes a basic inbound request shape:

```json
{
  "idea": "Dictated Text",
  "source": "iphone_shortcut",
  "created_at": "Current Date"
}
```

This contract is now backed by checked in JSON schemas.

## What Is Not Implemented

The following parts are still not present as fully finished working repo artifacts:

1. Persisted JSON output directory managed by the workflow itself
2. Markdown output writer
3. GitHub output or commit automation
4. Ollama integration
5. Automated tests in CI
6. Production secret validation inside the workflow
7. Duplicate detection
8. A complete hosted storage and review path beyond the raw response

## Main Gaps

### 1. README and repo are out of sync

The README reads like an active MVP. The repo is still in concept plus prototype territory.

### 2. Runnable path exists, but the hosted path is still partial

A new user can now validate schemas, run local enrichment, and post the sample payload to a webhook. The full hosted workflow still needs real n8n import validation and storage wiring.

### 3. The direct shortcut path is the only active ingestion path

The repo now centers on one ingestion path:

1. Direct iPhone Shortcut payload submission

### 4. Storage is not finished

The contract now exists as schemas and samples, but persistent workflow managed storage is still missing.

### 5. Validation exists, but CI does not

There is now a local validation script for the sample contracts, but there is still no automated CI safety net.

## Recommended MVP Direction

The cleanest next step is:

1. Make the iPhone Shortcut payload the only ingestion path for MVP.
2. Build one working n8n flow that accepts the payload, normalizes fields, calls one LLM provider, and writes one JSON artifact.
3. Add Markdown export only after JSON output is stable.

Why this path:

1. It matches the main README story.
2. It removes polling complexity.
3. It reduces platform dependence.
4. It creates a clean base for later GitHub commits, ranking, search, and dashboards.

## Suggested Target Contract

The repo should promote one canonical inbound payload and one canonical enriched output.

Suggested inbound payload for MVP:

```json
{
  "raw_idea": "Dictated text from the shortcut",
  "captured_at": "2026-05-07T15:22:00Z",
  "source": "iphone_shortcut",
  "capture_id": "uuid-or-short-id"
}
```

Suggested initial enriched output:

```json
{
  "id": "idea-20260507-152200",
  "raw_idea": "Dictated text from the shortcut",
  "captured_at": "2026-05-07T15:22:00Z",
  "source": "iphone_shortcut",
  "summary": "Short normalized summary",
  "tags": [
    "example"
  ],
  "next_steps": [
    "First follow up action"
  ]
}
```

This is intentionally smaller than the README example. Start with a narrow contract that is easy to validate.

## Recommended Repo Shape

The next useful structure would be:

1. `README.md`
   Vision plus setup summary.
2. `assessment.md`
   Current truth and gap analysis.
3. `roadmap.md`
   Short execution order.
4. `workflows/`
   n8n export files.
5. `samples/`
   Sample input and sample output payloads.
6. `schemas/`
   Request and response contracts.
7. `scripts/`
   Replay or local verification helpers.

## Decision Notes For Future Work

1. Keep one ingestion path primary.
2. Make the JSON contract real before adding more AI fields.
3. Do not add multiple providers at the start. One provider is enough for MVP.
4. Add a replayable test payload early.
5. Keep the repo honest. If the README describes a feature, a tracked artifact should back it up.
