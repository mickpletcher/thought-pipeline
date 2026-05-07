# Thought Pipeline Roadmap

Last updated: 2026-05-07

## Priority 1

Make the repo runnable from one simple path.

1. Choose direct iPhone Shortcut to n8n as the MVP ingestion path.
2. Add a real n8n workflow export under `workflows/`.
3. Add a sample input payload under `samples/`.
4. Add a `.env.example` or equivalent setup document for required secrets and endpoints.

## Priority 2

Define and prove the data contract.

1. Add a checked in input schema.
2. Add a checked in enriched output schema.
3. Save one real sample output artifact.
4. Add a replay script or curl example that posts a sample idea and shows the expected result.

## Priority 3

Add the first useful AI output.

1. Normalize the raw idea.
2. Generate a short summary.
3. Generate a small tag list.
4. Generate next steps.

## Priority 4

Add storage and review paths.

1. Write enriched results to JSON files.
2. Add Markdown export if it still adds value after JSON is stable.
3. Decide whether GitHub commit automation belongs in MVP or after manual review.

## Priority 5

Add hardening.

1. Add duplicate detection.
2. Add error handling for missing fields and provider failures.
3. Add a basic test or smoke validation path.
4. Update the README to match the real implementation after each milestone.
