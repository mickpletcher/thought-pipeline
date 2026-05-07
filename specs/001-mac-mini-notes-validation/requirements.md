# Requirements

## Goal

Validate the real world MVP path:

1. iPhone idea captured in Apple Notes
2. Notes sync to the 2012 Mac mini
3. Mac mini worker pulls notes
4. Worker normalizes notes into the shared JSON contract
5. Worker posts payloads to n8n
6. n8n returns enriched JSON
7. Failed deliveries are queued and retried safely

## Functional Requirements

1. The Mac mini worker must read notes from a configured Apple Notes folder.
2. Each pulled note must be converted into the checked in input schema.
3. The worker must avoid reposting unchanged notes by using local state.
4. The worker must write normalized payload files locally.
5. The worker must be able to post payloads to the webhook.
6. If webhook delivery fails, the payload must be written to the retry queue.
7. On the next run, the worker must retry queued payloads before processing new notes.
8. The worker must write structured run logs locally.
9. The n8n workflow must accept the normalized payload without manual edits to the payload shape.
10. The workflow response must match the checked in output schema.

## Non Functional Requirements

1. The setup must be understandable by a beginner.
2. The Mac mini path must not require manual note export.
3. The worker must be safe to run on a schedule every few minutes.
4. Failure states must leave enough evidence in logs or queue files for troubleshooting.
5. The direct Shortcut path must remain optional and must not become a dependency for the Apple Notes flow.

## Out Of Scope

1. Dashboard UI
2. Semantic search
3. Ollama support
4. GitHub auto commit
5. Rich scoring fields beyond the current output contract
