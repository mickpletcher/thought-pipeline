# Thought Pipeline Roadmap

Last updated: 2026-05-07

## Priority 1

Make the repo runnable from one simple path.

1. Keep Apple Notes pull as a supported MVP ingestion path.
2. Validate the Apple Notes pull script on a real Mac with synced iPhone notes.
3. Validate the scheduled Mac mini worker path with launchd, logging, and retry queue behavior.
4. Import and test the checked in n8n workflow export under `workflows/`.
5. Keep the sample input payload under `samples/` aligned with the Apple Notes pull contract.
6. Keep `.env.example` aligned with the real setup requirements.

## Priority 2

Define and prove the data contract.

1. Keep the checked in input schema aligned with real workflow expectations.
2. Keep the checked in output schema aligned with real workflow responses.
3. Regenerate the sample output artifact after contract changes.
4. Keep Apple Notes pulled payloads aligned with the same input schema.
5. Use the replay script or curl examples to verify the webhook path after workflow updates.

## Priority 3

Add the first useful AI output.

1. Keep the raw idea normalization step stable.
2. Generate a short summary.
3. Generate a small tag list.
4. Generate next steps.
5. Decide whether local fallback enrichment stays in the MVP or becomes dev only tooling.

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
