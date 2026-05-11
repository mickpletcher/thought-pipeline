# Specification

## Problem

The repo now has code and docs for an Apple Notes ingestion path, but it has not been proven in the real target environment.

The target environment is a 2012 Mac mini acting as the scheduled ingestion worker for notes created on iPhone.

Without a validated end to end path, the repo still depends on assumptions about:

1. Apple Notes script compatibility on the Mac mini
2. iCloud Notes sync timing
3. launchd job behavior
4. Webhook retry safety
5. Payload compatibility with the n8n workflow

## Proposed MVP Definition

The MVP is considered proven when the following path works end to end:

1. Create a new idea note in the configured Apple Notes folder on iPhone
2. Wait for the note to sync to the Mac mini
3. Run the worker manually or through launchd
4. Observe a normalized payload written under `output/captured/apple-notes`
5. Observe the payload delivered to n8n
6. Observe a valid enriched JSON response
7. Confirm rerunning the worker does not repost the unchanged note

## Interfaces

### Input Contract

The worker must emit the same input schema already checked in:

1. `raw_idea`
2. `captured_at`
3. `source`
4. `capture_id`

### Output Contract

The hosted flow must return the same output schema already checked in:

1. `id`
2. `raw_idea`
3. `captured_at`
4. `source`
5. `capture_id`
6. `summary`
7. `tags`
8. `next_steps`
9. `provider`
10. `processed_at`

## Data Locations

Mac mini worker artifacts:

1. `output/captured/apple-notes`
2. `output/state/apple-notes.json`
3. `output/pending-webhook/apple-notes`
4. `output/logs/apple-notes-run.log`
5. `output/logs/launchd.stdout.log`
6. `output/logs/launchd.stderr.log`

## Constraints

1. Apple Notes pull is macOS only.
2. The Mac mini may be older hardware, so the worker should stay lightweight.
3. The worker should not perform heavy enrichment locally when n8n can do it.
4. The normalized payload shape must stay stable across Apple Notes and optional direct Shortcut ingestion.

## Risks

1. AppleScript access to Notes may differ by macOS version.
2. Note body HTML cleanup may not be sufficient for all note formats.
3. Notes sync may lag enough to confuse first time testing.
4. n8n environment variables may not be configured correctly on first run.
5. Retry queue logic may hide repeated delivery failures if logs are not checked.

## Acceptance Criteria

1. Manual dry run on the Mac mini prints normalized JSON for synced notes.
2. Manual live run writes local payload files and state.
3. Failed webhook delivery writes queue files.
4. A later successful run clears queued files after delivery.
5. launchd can run the worker on schedule.
6. The README instructions are sufficient for a beginner to complete the test path.
