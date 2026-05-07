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
   Minimal sample payload for an iPhone Shortcut.
3. `apple-notes-retrieval.py`
   Early Apple Notes extraction stub for macOS using AppleScript through `osascript`.
4. `LICENSE`
5. `.gitignore`

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

That is the only concrete contract in the repo today.

### 3. Apple Notes retrieval experiment

`apple-notes-retrieval.py` can read notes from the macOS Notes app by running AppleScript through `osascript`.

Current behavior:

1. Reads notes from the `Ideas` folder in Apple Notes.
2. Concatenates note title and body into a delimiter based string.
3. Splits the result into note records in Python.

Current limits:

1. No persistence.
2. No deduplication.
3. No outbound transport.
4. No retry or error handling.
5. No tests.
6. macOS only.

## What Is Not Implemented

The following parts are described in the README but are not present as working repo artifacts:

1. n8n workflow export
2. `workflows/` directory
3. LLM prompt and processing logic
4. JSON output writer
5. Markdown output writer
6. GitHub output or commit automation
7. Ollama or cloud provider integration
8. Environment file example
9. Dependency manifest such as `requirements.txt` or `pyproject.toml`
10. Tests
11. Replay script or local verification path
12. Output schema beyond the sample JSON in the README

## Main Gaps

### 1. README and repo are out of sync

The README reads like an active MVP. The repo is still in concept plus prototype territory.

### 2. No runnable path

A new user cannot clone the repo and execute a working end to end flow from the files in source control.

### 3. No single implementation direction

There are two different ingestion concepts mixed together:

1. Direct iPhone Shortcut payload submission
2. Apple Notes polling on macOS

Both can be valid, but the MVP should choose one primary path first.

### 4. No contract for enriched output

The README includes an example enriched object, but there is no checked in schema, validation, or serializer that makes it a real contract.

### 5. No validation or regression safety

There are no tests or smoke scripts for payload ingestion, dedupe, enrichment, or storage.

## Recommended MVP Direction

The cleanest next step is:

1. Make the iPhone Shortcut payload the only ingestion path for MVP.
2. Treat Apple Notes retrieval as optional future ingestion, not the core path.
3. Build one working n8n flow that accepts the payload, normalizes fields, calls one LLM provider, and writes one JSON artifact.
4. Add Markdown export only after JSON output is stable.

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
