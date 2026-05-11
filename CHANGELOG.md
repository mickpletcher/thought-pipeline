# Changelog

## 2026-05-11

### Added

1. Added [scripts/process_onedrive_shortcuts.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/process_onedrive_shortcuts.py>) to process iPhone Shortcut JSON files saved into OneDrive.
2. Added [scripts/run_ingestion.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/run_ingestion.py>) as a shared entry point that lets the user choose `apple-notes` or `onedrive`.
3. Added [samples/sample-onedrive-shortcut-payload.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/samples/sample-onedrive-shortcut-payload.json>) for the OneDrive Shortcut contract.
4. Added [shortcut-onedrive.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/shortcut-onedrive.json>) as the dedicated OneDrive Shortcut payload example.
5. Added [shortcut-direct-webhook.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/shortcut-direct-webhook.json>) as the dedicated direct Shortcut to webhook payload example.
6. Added [shortcut-dual-write.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/shortcut-dual-write.json>) for the Shortcut pattern that writes to Apple Notes and OneDrive in the same run.
7. Added explicit README guidance for three Shortcut patterns:
   OneDrive only
   direct webhook
   dual write to Apple Notes and OneDrive

### Changed

1. Updated [README.md](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/README.md>) to document both supported ingestion sources, the shared ingestion runner, the shared output layout, and the dual write Shortcut flow.
2. Updated [assessment.md](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/assessment.md>) so the repo summary reflects the OneDrive path, dual write Shortcut path, and shared source selection entry point.
3. Updated [.env.example](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/.env.example>) with source selection and new default output paths.
4. Updated [scripts/pull_ios_notes.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/pull_ios_notes.py>) so Apple Notes output uses the shared `output` tree:
   `output/captured/apple-notes`
   `output/state/apple-notes.json`
   `output/pending-webhook/apple-notes`
   `output/logs/apple-notes-run.log`
5. Updated [scripts/install_macos_worker.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/install_macos_worker.py>) and [templates/macos/com.thoughtpipeline.notespull.plist.template](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/templates/macos/com.thoughtpipeline.notespull.plist.template>) so launchd logs now go under `output/logs`.
6. Updated [scripts/validate_samples.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/validate_samples.py>) to validate the OneDrive sample payload.
7. Updated the Mac mini validation docs:
   [specs/001-mac-mini-notes-validation/plan.md](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/specs/001-mac-mini-notes-validation/plan.md>)
   [specs/001-mac-mini-notes-validation/spec.md](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/specs/001-mac-mini-notes-validation/spec.md>)
   [specs/001-mac-mini-notes-validation/tasks.md](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/specs/001-mac-mini-notes-validation/tasks.md>)
   so all documented artifact paths match the shared output structure.
8. Updated [future-upgrades.md](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/future-upgrades.md>) to remove stale ingestion roadmap items and replace them with remaining follow up work for validation, testing, and duplicate handling.

### Removed

1. Removed [iPhone-shortcut.json](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/iPhone-shortcut.json>) because it was ambiguous across Apple Notes, OneDrive, and direct webhook capture paths.

### Verified

1. Ran `python scripts/validate_samples.py` and confirmed `SAMPLES_OK`.
2. Ran the OneDrive path through [scripts/process_onedrive_shortcuts.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/process_onedrive_shortcuts.py>) and [scripts/run_ingestion.py](</C:/Users/mick0/OneDrive/Documents/Code & Dev/GitHub/thought-pipeline/scripts/run_ingestion.py>) against the checked in sample.
3. Confirmed the Apple Notes branch of the shared runner exits with the expected macOS only message on Windows.

### Notes

1. The repo now supports user choice between Apple Notes and OneDrive as the preferred ingestion source.
2. The dual write Shortcut pattern is documented, but it will create two later captures unless duplicate detection is added.
