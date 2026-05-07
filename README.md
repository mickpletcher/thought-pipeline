# Thought Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![n8n](https://img.shields.io/badge/n8n-workflow-orange)](https://n8n.io)
[![Apple Shortcuts](https://img.shields.io/badge/Apple-Shortcuts-blue)](https://support.apple.com/guide/shortcuts/welcome/ios)
[![OpenAI](https://img.shields.io/badge/OpenAI-Structured%20JSON-black)](https://platform.openai.com/docs/api-reference/chat/create)

This project takes an idea you speak on your iPhone and turns it into structured JSON.

The goal is simple.

1. Capture a thought fast
2. Send it to a webhook
3. Clean it up with AI or a local fallback
4. Return a result you can save, search, or build on later

If you are new to this kind of setup, read this file from top to bottom once, then follow the Quick Start section.

## What This Project Does

You speak an idea into an iPhone Shortcut.

The Shortcut sends a JSON payload to either:

1. A local Python script for simple testing
2. An n8n workflow for hosted processing

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
   Example request body for the Shortcut
4. [schemas/input.schema.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/schemas/input.schema.json>)
   Input contract
5. [schemas/output.schema.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/schemas/output.schema.json>)
   Output contract
6. [samples/sample-input.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/samples/sample-input.json>)
   Sample request
7. [samples/sample-output.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/samples/sample-output.json>)
   Sample response
8. [scripts/enrich_idea.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/enrich_idea.py>)
   Main local processing script
9. [scripts/validate_samples.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/validate_samples.py>)
   Checks that samples match the schemas
10. [scripts/post_sample.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/post_sample.py>)
    Sends the sample request to a live webhook
11. [workflows/thought-pipeline-mvp.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/workflows/thought-pipeline-mvp.json>)
    n8n workflow export
12. [.env.example](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/.env.example>)
    Example environment settings

## Quick Start

If you want the fastest path to a working test, do this:

### Option 1: Local test only

Use this if you want to understand the project before touching n8n or your phone.

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

### Option 2: Full hosted path with n8n

Use this if you want your iPhone Shortcut to send real requests to a live workflow.

1. Get n8n running
2. Import the workflow file
3. Set your OpenAI key in n8n
4. Test the webhook from your computer
5. Point your iPhone Shortcut at that webhook

The rest of this README explains each of those steps.

## Prerequisites

You do not need everything on day one.

### Required for local testing

1. Windows PowerShell
2. Python 3.11 or newer
3. This repo cloned locally

### Required for the hosted n8n path

1. An n8n instance
2. An OpenAI API key
3. An iPhone with the Shortcuts app

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

This project expects one input format.

Input:

```json
{
  "raw_idea": "Dictated text from the shortcut",
  "captured_at": "2026-05-07T15:22:00Z",
  "source": "iphone_shortcut",
  "capture_id": "replace-with-uuid"
}
```

What the fields mean:

1. `raw_idea`
   The exact idea text
2. `captured_at`
   The timestamp from the Shortcut
3. `source`
   Where the idea came from
4. `capture_id`
   A unique value so each capture can be tracked

Output:

```json
{
  "id": "idea-20260507-152200-sample-001",
  "raw_idea": "A service that captures spoken project ideas on my phone, cleans them up, and turns them into a short action plan I can review later.",
  "captured_at": "2026-05-07T15:22:00Z",
  "source": "iphone_shortcut",
  "capture_id": "sample-001",
  "summary": "A service that captures spoken project ideas on my phone, cleans them up, and turns them into a short action plan I can review later.",
  "tags": [
    "action",
    "captures",
    "cleans",
    "ideas",
    "phone",
    "project"
  ],
  "next_steps": [
    "Rewrite the idea into a one sentence problem statement",
    "List the first buildable workflow that proves the concept",
    "Review whether this idea needs research, automation, or storage first: A service that captures spoken project ideas on my phone, cleans them up, and tu..."
  ],
  "provider": "local",
  "processed_at": "2026-05-07T15:41:36Z"
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

## Step 5: Run The Local Pipeline

This test processes the sample input without calling OpenAI.

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

## Step 6: Use OpenAI Instead Of The Local Fallback

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

## Step 7: Get n8n Running

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

## Step 8: Import The Workflow Into n8n

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

## Step 9: Configure OpenAI In n8n

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

## Step 10: Test The n8n Webhook From Your Computer

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

## Step 11: Build The iPhone Shortcut

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

## Step 12: Test The Shortcut

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

### Problem: The Shortcut sends literal bracket text

Fix:

You entered placeholder text instead of actual Shortcut variables. Replace each placeholder with the real token from the Shortcuts app.

## What Works Right Now

1. Checked in request schema
2. Checked in response schema
3. Sample request and sample response
4. Local validation
5. Local processing
6. Sample webhook posting
7. n8n workflow export

## What Still Needs Work

1. Real n8n import testing
2. Persistent JSON storage from the workflow
3. Duplicate detection
4. CI checks

## Good First Path For A Beginner

If you are not sure what to do first, use this order:

1. Install Python
2. Run `python scripts/validate_samples.py`
3. Run the local enrichment command
4. Read the output JSON
5. Set up n8n
6. Import the workflow
7. Test the webhook from your computer
8. Build the iPhone Shortcut last

## References

1. [n8n HTTP Request node docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
2. [n8n workflow import docs](https://docs.n8n.io/courses/level-one/chapter-6/)
3. [n8n Webhook docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/workflow-development/)
4. [OpenAI Chat Completions API reference](https://platform.openai.com/docs/api-reference/chat/create-chat-completion)

## License

This project is licensed under the [MIT License](LICENSE).
