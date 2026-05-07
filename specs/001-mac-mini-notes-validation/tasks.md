# Tasks

## Validation Tasks

- [ ] Confirm macOS version and that Apple Notes opens normally on the Mac mini
- [ ] Confirm iCloud Notes sync is enabled on the Mac mini
- [ ] Create a test note in the target Notes folder on iPhone
- [ ] Confirm the same note appears on the Mac mini
- [ ] Run `python3 scripts/pull_ios_notes.py --folder Ideas --dry-run --stdout`
- [ ] Review the generated normalized payload
- [ ] Run `python3 scripts/pull_ios_notes.py --folder Ideas`
- [ ] Confirm `output/ios-notes` contains note payload files
- [ ] Confirm `output/ios-notes-state.json` exists
- [ ] Rerun the worker and confirm unchanged notes are not reposted

## Hosted Flow Tasks

- [ ] Import `workflows/thought-pipeline-mvp.json` into n8n
- [ ] Set required OpenAI environment values for n8n
- [ ] Run the worker against the live webhook
- [ ] Confirm the workflow returns valid enriched JSON
- [ ] Save a real successful response example for repo docs

## Retry Tasks

- [ ] Intentionally break webhook delivery
- [ ] Run the worker and confirm files appear in `output/pending-webhook`
- [ ] Restore webhook delivery
- [ ] Run the worker again and confirm queued files are cleared
- [ ] Review `output/ios-notes-run.log` for both failure and recovery evidence

## Scheduled Worker Tasks

- [ ] Run `python3 scripts/install_macos_worker.py --folder Ideas --url "<webhook>" --secret "<secret>" --interval-seconds 300 --load`
- [ ] Confirm `~/Library/LaunchAgents/com.thoughtpipeline.notespull.plist` exists
- [ ] Confirm `output/launchd.stdout.log` and `output/launchd.stderr.log` are created
- [ ] Confirm scheduled runs happen without manual execution
- [ ] Update README with any Mac mini specific corrections discovered during validation
