# Plan

## Phase 1

Validate the worker on the Mac mini without n8n.

1. Confirm Python is installed on the Mac mini.
2. Confirm the iPhone note syncs into the configured Notes folder.
3. Run `pull_ios_notes.py` with `--dry-run --stdout`.
4. Review normalized payload output.

## Phase 2

Validate local worker artifacts.

1. Run `pull_ios_notes.py` without `--dry-run`.
2. Confirm files are written under `output/captured/apple-notes`.
3. Confirm `output/state/apple-notes.json` is written.
4. Confirm rerun behavior skips unchanged notes.

## Phase 3

Validate n8n handoff.

1. Import the workflow into n8n.
2. Configure OpenAI environment variables.
3. Run the worker against the webhook.
4. Confirm the response shape matches expectations.

## Phase 4

Validate failure and retry behavior.

1. Run the worker with an unavailable webhook.
2. Confirm payloads land in `output/pending-webhook/apple-notes`.
3. Restore the webhook.
4. Run the worker again.
5. Confirm queued payloads are delivered and removed.

## Phase 5

Validate scheduled execution.

1. Install the launchd job.
2. Confirm logs are written.
3. Confirm scheduled runs process new notes.
4. Capture final evidence for docs.
