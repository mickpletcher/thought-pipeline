# Thought Pipeline Assessment

Last reviewed: 2026-05-07

## Purpose

This file is the repo level source of truth for the current project state. It is meant to save future work from having to rescan the full repo to understand what exists, what is missing, and what should happen next.

## Repo Summary

The repo currently describes a larger product vision than it implements.

The project should support Apple Notes as an ingestion source for ideas created on iPhone.

The repo also supports a OneDrive folder ingestion path for ideas captured by an iPhone Shortcut.

Both ingestion paths now use the same repo side output layout with source named subfolders under `output`.

The repo now has a single ingestion entry point so the preferred source can be chosen by argument or environment setting.

The actual tracked implementation is much smaller:

1. `README.md`
   Product vision, target architecture, installation outline, and sample payloads.
2. `shortcut-onedrive.json`
   OneDrive Shortcut payload example.
3. `shortcut-direct-webhook.json`
   Direct Shortcut to webhook payload example.
4. `shortcut-dual-write.json`
   Shortcut example that writes to Apple Notes and OneDrive in the same run.
5. `schemas/`
   Input and output JSON schemas for the MVP contract.
6. `samples/`
   Checked in sample input and sample output payloads.
7. `scripts/`
   Local enrichment, sample posting, and contract validation helpers.
8. `workflows/`
   n8n MVP workflow export draft.
9. `templates/`
   macOS launchd template for the Mac mini worker path.
10. `requirements.txt`
   Python dependencies for local validation and replay.
11. `LICENSE`
12. `.gitignore`

## What Is Implemented

### 1. Repo positioning

The project goal is clear. The README explains the intended user flow and the end state well enough for someone to understand the product direction quickly.

### 2. Input payload shape

The repo now uses a standard inbound request shape that can be produced by Apple Notes pull or direct Shortcut submission:

```json
{
  "raw_idea": "Idea text",
  "captured_at": "2026-05-07T18:15:00Z",
  "source": "ios_notes",
  "capture_id": "ICLOUD.COM.APPLE.NOTES.note-id"
}
```

This contract is now backed by checked in JSON schemas.

### 3. Apple Notes pull path

The repo now includes a macOS script that reads notes from Apple Notes through `osascript`, converts each note to the input contract, tracks processed notes in a local state file, can post normalized payloads to the webhook, and can queue failed posts for retry.

### 4. OneDrive Shortcut path

The repo now includes a Windows friendly OneDrive ingestion script that reads shortcut generated JSON files from a synced folder, validates them against the same input contract, writes raw captures and enriched output into the shared `output` tree, optionally posts the raw payload to the webhook, and archives or isolates files based on success.

### 5. Dual write Shortcut path

The repo now documents a dual write Shortcut pattern where one Shortcut run writes the plain idea text into Apple Notes and writes the JSON payload into OneDrive. This keeps both ingestion paths available to the user, but it will create two later captures unless duplicate detection is added.

### 6. Mac mini worker path

The repo now includes a macOS worker installer that creates a launchd job for a scheduled pull on the Mac mini.

### 7. Source selection

The repo now includes `scripts/run_ingestion.py` so a user can choose `apple-notes` or `onedrive` as the preferred ingestion source without having to remember separate commands.

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

### 3. Apple Notes is now a required ingestion path

The repo should support this primary path:

1. Create or dictate ideas into Apple Notes on iPhone
2. Sync those notes to a Mac
3. Pull the synced notes from the Mac Notes app
4. Convert each note to the standard JSON contract
5. Send the result to the workflow

### 4. Storage is still partial

The contract now exists as schemas and samples, but persistent workflow managed storage is still missing.

### 5. Validation exists, but CI does not

There is now a local validation script for the sample contracts, but there is still no automated CI safety net.

## Recommended MVP Direction

The cleanest next step is:

1. Keep Apple Notes pull as a supported ingestion path for MVP.
2. Keep the direct Shortcut payload path optional.
3. Use the Mac mini as a scheduled ingestion worker.
4. Build one working n8n flow that accepts the normalized payload, calls one LLM provider, and writes one JSON artifact.
5. Add Markdown export only after JSON output is stable.

Why this path:

1. It matches the desired capture flow from iPhone Notes.
2. It keeps one normalized contract after ingestion.
3. It still allows a direct Shortcut path when needed.
4. It creates a clean base for later GitHub commits, ranking, search, and dashboards.

## Suggested Target Contract

The repo should promote one canonical inbound payload and one canonical enriched output.

Suggested inbound payload for MVP:

```json
{
  "raw_idea": "Idea text pulled from Apple Notes",
  "captured_at": "2026-05-07T18:15:00Z",
  "source": "ios_notes",
  "capture_id": "ICLOUD.COM.APPLE.NOTES.note-id"
}
```

Suggested initial enriched output:

```json
{
  "id": "idea-20260507-181500-ICLOUD.COM.APPLE.NOTES.note-id",
  "raw_idea": "Idea text pulled from Apple Notes",
  "captured_at": "2026-05-07T18:15:00Z",
  "source": "ios_notes",
  "capture_id": "ICLOUD.COM.APPLE.NOTES.note-id",
  "summary": "Short normalized summary",
  "tags": [
    "example"
  ],
  "next_steps": [
    "First follow up action"
  ],
  "provider": "openai",
  "processed_at": "2026-05-07T18:15:05Z"
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
