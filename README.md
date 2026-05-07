# Thought Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![n8n](https://img.shields.io/badge/n8n-workflow-orange)](https://n8n.io)
[![Apple Shortcuts](https://img.shields.io/badge/Apple-Shortcuts-blue)](https://support.apple.com/guide/shortcuts/welcome/ios)
[![OpenAI](https://img.shields.io/badge/OpenAI-Structured%20JSON-black)](https://platform.openai.com/docs/api-reference/chat/create)

This project takes ideas captured in iOS Notes and turns them into structured JSON.

The goal is simple.

1. Capture a thought in Apple Notes on iPhone
2. Pull the synced note from Apple Notes on a Mac
3. Send it to a webhook or process it locally
4. Return a result you can save, search, or build on later

If you are new to this kind of setup, read this file from top to bottom once, then follow the Quick Start section.

## What This Project Does

You capture an idea in Apple Notes on iPhone.

That note syncs through iCloud to Apple Notes on a Mac.

A local Mac side script reads the notes, converts them to the project JSON contract, and can then:

1. Save the normalized payload locally
2. Send the payload to an n8n workflow

There is also an optional direct Shortcut payload path in the repo, but Apple Notes pull is now the main ingestion path.

That payload is then turned into a structured result with these fields:

1. `summary`
2. `tags`
3. `next_steps`
4. Metadata such as `capture_id` and `processed_at`

## What n8n Is

n8n is an automation tool.

Think of it as a visual workflow builder.

You connect steps together such as:

1. Receive a webhook
2. Validate input
3. Call OpenAI
4. Return JSON

If you do not want to learn n8n first, you can still use the local Python path in this repo.

## What Is In This Repo

1. [assessment.md](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/assessment.md>)
   Current project assessment and gap notes
2. [roadmap.md](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/roadmap.md>)
   Short priority list for future work
3. [iPhone-shortcut.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/iPhone-shortcut.json>)
   Optional direct Shortcut request body
4. [schemas/input.schema.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/schemas/input.schema.json>)
   Input contract
5. [schemas/output.schema.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/schemas/output.schema.json>)
   Output contract
6. [samples/sample-input.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/samples/sample-input.json>)
   Default Apple Notes request sample
7. [samples/sample-ios-note-payload.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/samples/sample-ios-note-payload.json>)
   Apple Notes request sample
8. [samples/sample-output.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/samples/sample-output.json>)
   Sample response
9. [scripts/enrich_idea.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/enrich_idea.py>)
   Main local processing script
10. [scripts/validate_samples.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/validate_samples.py>)
   Checks that samples match the schemas
11. [scripts/pull_ios_notes.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/pull_ios_notes.py>)
    Pulls synced Apple Notes on macOS and converts them to the input contract
12. [scripts/install_macos_worker.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/install_macos_worker.py>)
    Creates a launchd job for the Mac mini worker
13. [scripts/post_sample.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/post_sample.py>)
    Sends the sample request to a live webhook
14. [workflows/thought-pipeline-mvp.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/workflows/thought-pipeline-mvp.json>)
    n8n workflow export
15. [templates/macos/com.thoughtpipeline.notespull.plist.template](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/templates/macos/com.thoughtpipeline.notespull.plist.template>)
    Reference launchd template
16. [.env.example](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/.env.example>)
    Example environment settings

## Quick Start

If you want the fastest path to a working test, do this:

### Option 1: Local contract and enrichment test only

Use this if you want to understand the project before touching n8n or the Mac mini.

1. Install Python 3.11 or newer
2. Open PowerShell in the repo root
3. Run:

```powershell
python -m pip install -r requirements.txt
python scripts/validate_samples.py
python scripts/enrich_idea.py --input samples/sample-input.json --output output/sample-output.json --provider local --pretty
```

4. Open [output/sample-output.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/output/sample-output.json>)

If that file exists and looks correct, the local path works.

### Option 2: Apple Notes path with n8n

Use this if you want notes created on your iPhone to be pulled from Apple Notes and sent into the hosted workflow.

1. Make sure your iPhone Notes sync to a Mac
2. Get n8n running
3. Import the workflow file
4. Set your OpenAI key in n8n
5. Run the Apple Notes pull script on the Mac

The rest of this README explains each of those steps.

## Prerequisites

You do not need everything on day one.

### Required for local testing

1. Windows PowerShell
2. Python 3.11 or newer
3. This repo cloned locally

### Required for the Apple Notes path

1. An iPhone using Apple Notes
2. A Mac signed into the same Apple ID with Notes sync enabled
3. An n8n instance if you want hosted processing
4. An OpenAI API key if you want hosted AI enrichment

## Step 1: Clone The Repo

If you have not cloned the repo yet:

```powershell
git clone https://github.com/mickpletcher/thought-pipeline.git
cd thought-pipeline
```

## Step 2: Install Python Dependencies

Run:

```powershell
python -m pip install -r requirements.txt
```

What this installs:

1. `requests`
   Used to call web APIs
2. `jsonschema`
   Used to validate the request and response contracts

## Step 3: Understand The Input And Output

This project expects one input format no matter where the idea came from.

Input:

```json
{
  "raw_idea": "Idea text pulled from Apple Notes",
  "captured_at": "2026-05-07T18:15:00Z",
  "source": "ios_notes",
  "capture_id": "ICLOUD.COM.APPLE.NOTES.example-note-001"
}
```

What the fields mean:

1. `raw_idea`
   The exact idea text
2. `captured_at`
   The timestamp taken from the note modification time
3. `source`
   Where the idea came from such as `ios_notes` or `iphone_shortcut`
4. `capture_id`
   A unique value so each capture can be tracked

Output:

```json
{
  "id": "idea-20260507-181500-ICLOUD.COM.APPLE.NOTES.sample-note-001",
  "raw_idea": "Build a small workflow that reads ideas from Apple Notes, converts each note to a standard JSON payload, and sends only new notes to n8n.",
  "captured_at": "2026-05-07T18:15:00Z",
  "source": "ios_notes",
  "capture_id": "ICLOUD.COM.APPLE.NOTES.sample-note-001",
  "summary": "Build a small workflow that reads ideas from Apple Notes, converts each note to a standard JSON payload, and sends only new notes to n8n.",
  "tags": [
    "apple",
    "build",
    "converts",
    "ideas",
    "notes",
    "workflow"
  ],
  "next_steps": [
    "Rewrite the idea into a one sentence problem statement",
    "List the first buildable workflow that proves the concept",
    "Review whether this idea needs research, automation, or storage first: Build a small workflow that reads ideas from Apple Notes, converts each note t..."
  ],
  "provider": "local",
  "processed_at": "2026-05-07T18:15:05Z"
}
```

What the output adds:

1. `summary`
   A shorter cleaned up version of the idea
2. `tags`
   Quick labels for search and grouping
3. `next_steps`
   Immediate actions you can take
4. `provider`
   Shows whether the result came from the local fallback or OpenAI
5. `processed_at`
   When the pipeline created the output

## Step 4: Validate The Sample Files

This is the safest first test because it does not depend on OpenAI or n8n.

Run:

```powershell
python scripts/validate_samples.py
```

Expected result:

```text
SAMPLES_OK
```

If you see `SAMPLES_OK`, the checked in examples match the checked in schemas.

## Step 5: Pull Notes From Apple Notes

This path requires macOS.

Why:

1. Apple Notes does not expose a simple cross platform file store you can read from Windows
2. The script uses `osascript` to read notes from the Mac Notes app
3. If your iPhone and Mac sync the same Notes account, the Mac can pull the notes your phone created

Before you run the script:

1. Make sure the idea note exists in Apple Notes on your iPhone
2. Make sure that note appears in the same folder on your Mac
3. Make sure the Mac is signed into the same Apple ID and Notes sync is enabled
4. Make sure Python is installed on the Mac mini

Basic command:

```powershell
python scripts/pull_ios_notes.py --folder Ideas --dry-run --stdout
```

What this does:

1. Connects to Apple Notes on the Mac
2. Reads notes from the `Ideas` folder
3. Converts each note to the input JSON contract
4. Prints the payloads without writing state or posting them

When you are ready to export note payloads locally:

```powershell
python scripts/pull_ios_notes.py --folder Ideas
```

That writes payload files under `output/ios-notes` and stores processed state in `output/ios-notes-state.json`.

If you want to send pulled notes straight to n8n:

```powershell
python scripts/pull_ios_notes.py --folder Ideas --url "https://your-n8n-host/webhook/thought-pipeline" --secret "replace-me"
```

What gets created on the Mac mini:

1. `output/ios-notes`
   One normalized JSON file per pulled note
2. `output/ios-notes-state.json`
   Tracks which notes were already processed
3. `output/pending-webhook`
   Retry queue for payloads that could not be posted
4. `output/ios-notes-run.log`
   Run log in JSON line format

## Step 6: Turn The Mac Mini Into A Scheduled Worker

This is the recommended setup for your 2012 Mac mini.

Use the Mac mini as a lightweight ingestion worker:

1. iPhone writes to Notes
2. Mac mini syncs Notes
3. Mac mini pulls new notes every few minutes
4. Mac mini posts normalized payloads to n8n
5. If posting fails, the payload is queued and retried on the next run

Install the launchd job on the Mac mini:

```bash
python3 scripts/install_macos_worker.py --folder Ideas --url "https://your-n8n-host/webhook/thought-pipeline" --secret "replace-me" --interval-seconds 300 --load
```

What that command does:

1. Creates a LaunchAgent plist in `~/Library/LaunchAgents`
2. Sets the worker to run at login
3. Runs it every 300 seconds
4. Writes launchd stdout and stderr logs under `output`
5. Loads the job immediately when `--load` is used

If you want to inspect the generated plist before loading it:

```bash
python3 scripts/install_macos_worker.py --folder Ideas --url "https://your-n8n-host/webhook/thought-pipeline" --secret "replace-me"
```

To unload the job later on the Mac mini:

```bash
launchctl unload ~/Library/LaunchAgents/com.thoughtpipeline.notespull.plist
```

To load it again:

```bash
launchctl load ~/Library/LaunchAgents/com.thoughtpipeline.notespull.plist
```

## Step 7: Check Logs On The Mac Mini

After the worker runs, check these files:

1. `output/ios-notes-run.log`
   High level run events and retry events
2. `output/launchd.stdout.log`
   launchd standard output
3. `output/launchd.stderr.log`
   launchd errors
4. `output/pending-webhook`
   Files waiting to be retried

If `pending-webhook` contains files, the Mac mini pulled the notes successfully but could not deliver them to the webhook on that run.

## Step 8: Run The Local Pipeline

This test processes the default Apple Notes style sample input without calling OpenAI.

Run:

```powershell
python scripts/enrich_idea.py --input samples/sample-input.json --output output/sample-output.json --provider local --pretty
```

What this command does:

1. Reads `samples/sample-input.json`
2. Validates it against the input schema
3. Builds a local output object
4. Validates the output against the output schema
5. Writes the result to `output/sample-output.json`

Open the result here:

[output/sample-output.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/output/sample-output.json>)

## Step 9: Use OpenAI Instead Of The Local Fallback

This part is optional.

If you want the local script to call OpenAI, set your API key first.

In PowerShell for the current session:

```powershell
$env:OPENAI_API_KEY="your-api-key"
```

Optional settings:

```powershell
$env:OPENAI_MODEL="gpt-4.1-mini"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"
```

Then run:

```powershell
python scripts/enrich_idea.py --input samples/sample-input.json --output output/sample-output-openai.json --provider openai --pretty
```

If you want the script to choose automatically:

```powershell
python scripts/enrich_idea.py --input samples/sample-input.json --output output/sample-output-auto.json --provider auto --pretty
```

How `--provider auto` works:

1. If `OPENAI_API_KEY` exists, it uses OpenAI
2. If `OPENAI_API_KEY` does not exist, it uses the local fallback

## Step 10: Get n8n Running

You have two common options.

### Option 1: n8n Cloud

1. Create an account at [n8n](https://n8n.io/)
2. Open your workspace
3. Create a new workflow

### Option 2: Local Docker run

If Docker is installed:

```powershell
docker run -it --rm --name n8n -p 5678:5678 -v ${HOME}/.n8n:/home/node/.n8n n8nio/n8n
```

Then open:

[http://localhost:5678](http://localhost:5678)

## Step 11: Import The Workflow Into n8n

This repo includes a workflow export here:

[workflows/thought-pipeline-mvp.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/workflows/thought-pipeline-mvp.json>)

To import it:

1. Open n8n
2. Create a new workflow if needed
3. Use the import option in n8n
4. Select `workflows/thought-pipeline-mvp.json`

What the workflow does:

1. `Inbound Webhook`
   Receives the incoming request
2. `Normalize Input`
   Checks that required fields exist
3. `OpenAI Enrichment`
   Sends the request to OpenAI
4. `Shape Output`
   Builds the final JSON response
5. `Return Response`
   Sends JSON back to the caller

## Step 12: Configure OpenAI In n8n

The workflow uses environment variables.

Set these in the environment where n8n runs:

1. `OPENAI_API_KEY`
2. `OPENAI_MODEL`
3. `OPENAI_BASE_URL`

Minimum required value:

1. `OPENAI_API_KEY`

Suggested default model:

1. `gpt-4.1-mini`

The repo includes an example file here:

[.env.example](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/.env.example>)

Important note:

That file is only an example. It does not automatically load into n8n by itself. You still need to set those values in the environment that starts n8n.

## Step 13: Test The n8n Webhook From Your Computer

Once the workflow is imported and active, get the webhook URL from n8n.

Then run:

```powershell
python scripts/post_sample.py --url "https://your-n8n-host/webhook/thought-pipeline" --secret "replace-me"
```

If you prefer environment variables:

```powershell
$env:THOUGHT_PIPELINE_WEBHOOK_URL="https://your-n8n-host/webhook/thought-pipeline"
$env:THOUGHT_PIPELINE_WEBHOOK_SECRET="replace-me"
python scripts/post_sample.py
```

What success looks like:

1. You get an HTTP `200` response
2. The body contains JSON
3. The JSON includes `summary`, `tags`, and `next_steps`

## Step 14: Optional Direct Shortcut Path

You may still want a direct Shortcut path.

This is optional now.

Use it only if you want the phone to send payloads directly instead of relying on Apple Notes sync.

The request shape is defined in [iPhone-shortcut.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/iPhone-shortcut.json>).

## Step 15: Build The iPhone Shortcut

On your iPhone:

1. Open the Shortcuts app
2. Create a new Shortcut
3. Add a `Dictate Text` action
4. Add a `Text` or variable step if you want to inspect the dictated text
5. Add a `Get Contents of URL` action

Set `Get Contents of URL` like this:

1. URL
   Your n8n webhook URL
2. Method
   `POST`
3. Headers
   `Content-Type: application/json`
4. Optional header
   `X-Webhook-Secret: your-secret`
5. Request body
   JSON

Use this body shape:

```json
{
  "raw_idea": "[Dictated Text]",
  "captured_at": "[Current Date]",
  "source": "iphone_shortcut",
  "capture_id": "[UUID]"
}
```

Important beginner note:

The square bracket values above are placeholders. In Shortcuts, each one should be replaced with the real Shortcut variable token, not the literal text in brackets.

## Step 16: Test The Shortcut

Do one simple test first.

Say something like:

`Build a small app that turns voice notes into project tasks`

What should happen:

1. The Shortcut sends your JSON payload
2. n8n receives it
3. OpenAI returns structured content
4. n8n responds with JSON

If you want, you can add more Shortcut actions after the webhook call to:

1. Show the response
2. Save the response
3. Copy the response to the clipboard
4. Send the response to Notes or Files

## Common Problems

### Problem: `python` is not recognized

Fix:

1. Install Python
2. Reopen PowerShell
3. Run `python --version`

### Problem: `SAMPLES_OK` does not appear

Fix:

1. Read the error text
2. Check the JSON file it names
3. Check the schema field it names

### Problem: OpenAI call fails

Fix:

1. Make sure `OPENAI_API_KEY` is set
2. Make sure the key is valid
3. Make sure your network can reach `api.openai.com`

### Problem: n8n webhook test fails

Fix:

1. Make sure the workflow is active
2. Make sure you copied the correct webhook URL
3. Make sure any secret header matches what your workflow expects
4. Make sure n8n can reach OpenAI

### Problem: Apple Notes pull fails on Windows

Fix:

This is expected. The Apple Notes pull script only works on macOS because it talks to the local Notes app through AppleScript.

### Problem: Apple Notes folder is not found

Fix:

1. Make sure the folder exists in the Mac Notes app
2. Make sure the folder name passed to `--folder` matches exactly
3. Make sure the notes have finished syncing from iPhone to Mac

### Problem: Notes are pulled but not delivered

Fix:

1. Check `output/pending-webhook`
2. Check `output/ios-notes-run.log`
3. Check the webhook URL and secret
4. Wait for the next scheduled run or run the worker manually again

### Problem: launchd job does not run

Fix:

1. Check `output/launchd.stderr.log`
2. Make sure the Python path on the Mac mini is correct
3. Make sure the repo path did not change after installing the job
4. Unload and load the plist again

### Problem: The Shortcut sends literal bracket text

Fix:

You entered placeholder text instead of actual Shortcut variables. Replace each placeholder with the real token from the Shortcuts app.

## What Works Right Now

1. Checked in request schema
2. Checked in response schema
3. Sample request and sample response
4. Local validation
5. Apple Notes pull script
6. Scheduled Mac mini worker path
7. Retry queue for failed webhook delivery
8. Local processing
9. Sample webhook posting
10. n8n workflow export

## What Still Needs Work

1. Real n8n import testing
2. Persistent JSON storage from the workflow
3. Duplicate detection across pulled notes and direct payloads
4. CI checks
5. A real macOS validation pass for the Apple Notes pull script

## Good First Path For A Beginner

If you are not sure what to do first, use this order:

1. Install Python
2. Run `python scripts/validate_samples.py`
3. Confirm your note syncs from iPhone to Mac
4. Run `python scripts/pull_ios_notes.py --folder Ideas --dry-run --stdout`
5. Set up n8n
6. Import the workflow
7. Install the Mac mini launchd worker
8. Run the Apple Notes pull script against the webhook
9. Use the direct Shortcut path only if you still want it

## References

1. [n8n HTTP Request node docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
2. [n8n workflow import docs](https://docs.n8n.io/courses/level-one/chapter-6/)
3. [n8n Webhook docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/workflow-development/)
4. [OpenAI Chat Completions API reference](https://platform.openai.com/docs/api-reference/chat/create-chat-completion)

## License

This project is licensed under the [MIT License](LICENSE).
