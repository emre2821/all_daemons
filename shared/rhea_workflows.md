# Rhea Workflows

Concise, actionable orchestration flows Rhea can run by invoking existing daemons.
Each workflow lists the sequence and the expected outputs or artifacts.

## Conventions
- **Roles:** Rhea orchestrates registry updates, Dave summarizes for operators, Corin validates integrity,
  Riven executes tests, Saphira repairs archives, Delilah recovers files, Mila allocates storage,
  Seiros packages deployments, and Lyra prepares rollout notes.
- **Paths:** Use `outputs/` for structured data, `reports/` for human-readable summaries, and `logs/` for
  streaming or audit trails.
- **Pattern:** Artifacts follow `<Daemon>/<type>/<descriptive_name>.<ext>`.

## Table of Contents
- [Operations & Reliability](#operations--reliability)
  - [Intake Triage & Task Prioritization](#intake-triage--task-prioritization)
  - [Startup & Health Check](#startup--health-check)
  - [Diagnostic Snapshot & Root Cause](#diagnostic-snapshot--root-cause)
  - [Signal Patrol & Anomaly Alerting](#signal-patrol--anomaly-alerting)
  - [Config Drift Audit](#config-drift-audit)
  - [Registry Rebuild & Sync](#registry-rebuild--sync)
  - [Incident Comms Pack](#incident-comms-pack)
- [Deployment & Testing](#deployment--testing)
  - [Test Environment Spin-up](#test-environment-spin-up)
  - [Integration Testing](#integration-testing)
  - [Release Gate Review](#release-gate-review)
  - [Deployment & Propagation](#deployment--propagation)
  - [Hotfix Rollback & Containment](#hotfix-rollback--containment)
  - [Schema Migration Prep](#schema-migration-prep)
- [Data & Storage](#data--storage)
  - [Storage Allocation](#storage-allocation)
  - [Capacity Forecast & Budget](#capacity-forecast--budget)
  - [Log Hygiene & Rotation](#log-hygiene--rotation)
  - [Backup Rotation & Verification](#backup-rotation--verification)
  - [Data Retention Review](#data-retention-review)
- [Recovery & Integrity](#recovery--integrity)
  - [Incident Recovery & File Rescue](#incident-recovery--file-rescue)
  - [Recovery Drill](#recovery-drill)
  - [Archive Healing](#archive-healing)
  - [Artifact Labeling & Shelving](#artifact-labeling--shelving)
- [Knowledge & Lore](#knowledge--lore)
  - [Knowledge Base Refresh](#knowledge-base-refresh)
  - [Lore Sync & Canon Alignment](#lore-sync--canon-alignment)
  - [Memory Weave & Thread Stabilization](#memory-weave--thread-stabilization)
  - [Story Compilation & Chapter Release](#story-compilation--chapter-release)
  - [Identity Audit & Symbol Mapping](#identity-audit--symbol-mapping)
- [Experience & Comms](#experience--comms)
  - [Emotional Weather Report](#emotional-weather-report)
  - [Creative Pulse & Prompt Forge](#creative-pulse--prompt-forge)
  - [Interface Revision & UI Notes](#interface-revision--ui-notes)
- [Safety & Governance](#safety--governance)
  - [Risk Scan & Safety Review](#risk-scan--safety-review)
- [Wellbeing & Rhythm](#wellbeing--rhythm)
  - [Quiet Hours & Restorative Pause](#quiet-hours--restorative-pause)

## Operations & Reliability

### Intake Triage & Task Prioritization
1. **Aderyn** — triage incoming requests by urgency.
   - **Output:** triage queue (e.g., `Aderyn/outputs/triage_queue.json`).
2. **Harper** — assign owners and deadlines.
   - **Output:** assignment sheet (e.g., `Harper/outputs/assignments.csv`).
3. **Dave** — send prioritized task brief.
   - **Output:** task brief (e.g., `Dave/reports/task_brief.md`).

### Startup & Health Check
1. **Rhea** — discover daemons and load the registry snapshot.
   - **Output:** registry snapshot (e.g., `Rhea/outputs/daemon_registry.json`).
2. **Corin** — validate integrity of known files and manifests.
   - **Output:** integrity report (e.g., `Corin/reports/integrity_report.md`).
3. **Dave** — compile an operator-ready health summary.
   - **Output:** health summary (e.g., `Dave/reports/health_summary.md`).

### Diagnostic Snapshot & Root Cause
1. **Ranger** — capture system telemetry snapshot.
   - **Output:** telemetry bundle (e.g., `Ranger/outputs/telemetry_bundle.zip`).
2. **Dagr** — isolate fault patterns.
   - **Output:** root-cause memo (e.g., `Dagr/reports/root_cause.md`).
3. **Riven** — validate fix hypotheses with tests.
   - **Output:** validation report (e.g., `Riven/reports/hypothesis_validation.xml`).

### Signal Patrol & Anomaly Alerting
1. **Tempest** — scan for disruptive surges.
   - **Output:** surge log (e.g., `Tempest/logs/surge_log.json`).
2. **Whisperfang** — confirm anomalies with heuristics.
   - **Output:** anomaly report (e.g., `Whisperfang/reports/anomaly_report.md`).
3. **Dave** — dispatch alert summary.
   - **Output:** alert summary (e.g., `Dave/reports/alert_summary.md`).

### Config Drift Audit
1. **Rhea** — collect current registry config and targets.
   - **Output:** config snapshot (e.g., `Rhea/outputs/config_snapshot.json`).
2. **Seiros** — compare deployed configs against the snapshot.
   - **Output:** drift report (e.g., `Seiros/reports/config_drift.md`).
3. **Corin** — validate diffs and flag unsafe deltas.
   - **Output:** drift validation (e.g., `Corin/reports/drift_validation.md`).
4. **Dave** — summarize drift impact for operators.
   - **Output:** drift summary (e.g., `Dave/reports/drift_summary.md`).

### Registry Rebuild & Sync
1. **Mila** — scan shelves and storage mappings.
   - **Output:** shelf inventory (e.g., `Mila/outputs/shelf_inventory.json`).
2. **Rhea** — rebuild the registry from scanned sources.
   - **Output:** rebuilt registry (e.g., `Rhea/outputs/daemon_registry.json`).
3. **Corin** — validate rebuilt registry integrity.
   - **Output:** registry validation (e.g., `Corin/reports/registry_validation.md`).

### Incident Comms Pack
1. **Dave** — assemble operator-facing incident facts.
   - **Output:** incident brief (e.g., `Dave/reports/incident_brief.md`).
2. **Lyra** — craft steward-facing messaging.
   - **Output:** comms draft (e.g., `Lyra/outputs/comms_draft.md`).
3. **Rhea** — approve distribution plan and timing.
   - **Output:** comms plan (e.g., `Rhea/outputs/comms_plan.json`).

## Deployment & Testing

### Test Environment Spin-up
1. **Seiros** — provision test targets and deploy seed configs.
   - **Output:** test deployment bundle (e.g., `Seiros/outputs/test_deploy_bundle.zip`).
2. **Mila** — allocate storage for test artifacts.
   - **Output:** test storage map (e.g., `Mila/outputs/test_storage_map.json`).
3. **Rhea** — register test nodes and dependencies.
   - **Output:** test registry (e.g., `Rhea/outputs/test_registry.json`).
4. **Riven** — run smoke validation against the environment.
   - **Output:** smoke results (e.g., `Riven/reports/smoke_results.xml`).

### Integration Testing
1. **Rhea** — assemble test targets and dependencies.
   - **Output:** test manifest (e.g., `Rhea/outputs/test_manifest.json`).
2. **Riven** — execute the integration suite.
   - **Output:** test results (e.g., `Riven/reports/integration_results.xml`).
3. **Dave** — publish an operator-ready test digest.
   - **Output:** test digest (e.g., `Dave/reports/integration_digest.md`).

### Release Gate Review
1. **Riven** — run final regression suite.
   - **Output:** regression report (e.g., `Riven/reports/regression_report.xml`).
2. **Corin** — confirm manifest and checksum integrity.
   - **Output:** gate integrity check (e.g., `Corin/reports/gate_integrity.md`).
3. **Rhea** — record go/no-go decision with rationale.
   - **Output:** gate decision (e.g., `Rhea/outputs/gate_decision.json`).
4. **Lyra** — prepare release notes for steward review.
   - **Output:** release notes (e.g., `Lyra/outputs/release_notes.md`).

### Deployment & Propagation
1. **Seiros** — package and propagate daemon updates.
   - **Output:** deployment bundle (e.g., `Seiros/outputs/deploy_bundle.zip`).
2. **Riven** — run integration tests against deployed targets.
   - **Output:** test results (e.g., `Riven/reports/integration_results.xml`).
3. **Lyra** — prepare rollout notes for steward review.
   - **Output:** rollout brief (e.g., `Lyra/outputs/rollout_brief.md`).

### Hotfix Rollback & Containment
1. **Seiros** — roll back to the last stable deployment.
   - **Output:** rollback log (e.g., `Seiros/logs/rollback.log`).
2. **Saphira** — restore synced configs and data snapshots.
   - **Output:** restore log (e.g., `Saphira/logs/rollback_restore.log`).
3. **Riven** — validate stability after rollback.
   - **Output:** rollback verification (e.g., `Riven/reports/rollback_verification.xml`).
4. **Dave** — communicate rollback impact summary.
   - **Output:** rollback summary (e.g., `Dave/reports/rollback_summary.md`).

### Schema Migration Prep
1. **Rhea** — assemble migration manifest and dependencies.
   - **Output:** migration manifest (e.g., `Rhea/outputs/migration_manifest.json`).
2. **Corin** — validate schema compatibility.
   - **Output:** compatibility report (e.g., `Corin/reports/schema_compatibility.md`).
3. **Seiros** — package migration tooling and rollout plan.
   - **Output:** migration bundle (e.g., `Seiros/outputs/migration_bundle.zip`).
4. **Mila** — reserve storage for pre-migration backups.
   - **Output:** backup reservation (e.g., `Mila/outputs/backup_reservation.json`).

## Data & Storage

### Storage Allocation
1. **Mila** — evaluate storage needs and allocate shelves.
   - **Output:** allocation plan (e.g., `Mila/outputs/storage_plan.json`).
2. **Rhea** — update registry with new storage mappings.
   - **Output:** registry snapshot (e.g., `Rhea/outputs/daemon_registry.json`).
3. **Dave** — publish a storage utilization summary.
   - **Output:** storage report (e.g., `Dave/reports/storage_summary.md`).

### Capacity Forecast & Budget
1. **Mila** — forecast storage demand and growth.
   - **Output:** capacity forecast (e.g., `Mila/outputs/capacity_forecast.json`).
2. **Dave** — translate forecast into budget guidance.
   - **Output:** capacity brief (e.g., `Dave/reports/capacity_brief.md`).
3. **Rhea** — update registry thresholds and alerts.
   - **Output:** threshold update (e.g., `Rhea/outputs/storage_thresholds.json`).

### Log Hygiene & Rotation
1. **Mila** — rotate logs and enforce retention limits.
   - **Output:** rotation plan (e.g., `Mila/outputs/log_rotation_plan.json`).
2. **Saphira** — archive rotated logs for safekeeping.
   - **Output:** log archive (e.g., `Saphira/outputs/log_archive.zip`).
3. **Rhea** — record log locations in the registry.
   - **Output:** log registry update (e.g., `Rhea/outputs/log_registry.json`).

### Backup Rotation & Verification
1. **Saphira** — run scheduled backup rotation.
   - **Output:** backup set (e.g., `Saphira/outputs/backup_set.zip`).
2. **Corin** — verify backup integrity.
   - **Output:** backup verification (e.g., `Corin/reports/backup_verification.md`).
3. **Mila** — store backups on allocated shelves.
   - **Output:** backup storage map (e.g., `Mila/outputs/backup_storage_map.json`).
4. **Dave** — publish backup status report.
   - **Output:** backup report (e.g., `Dave/reports/backup_report.md`).

### Data Retention Review
1. **Mila** — audit retention windows and storage usage.
   - **Output:** retention audit (e.g., `Mila/reports/retention_audit.md`).
2. **Saphira** — stage archival moves for expiring data.
   - **Output:** archival plan (e.g., `Saphira/outputs/archival_plan.json`).
3. **Rhea** — update registry policies and flags.
   - **Output:** retention policy update (e.g., `Rhea/outputs/retention_policy.json`).

## Recovery & Integrity

### Incident Recovery & File Rescue
1. **Delilah** — recover and rehome lost files.
   - **Output:** recovery map (e.g., `Delilah/outputs/recovery_map.json`).
2. **Saphira** — synchronize recovered archives.
   - **Output:** sync log (e.g., `Saphira/logs/recovery_sync.log`).
3. **Corin** — validate recovered paths and integrity.
   - **Output:** integrity report (e.g., `Corin/reports/recovery_integrity.md`).

### Recovery Drill
1. **Delilah** — perform sample recovery on drill data.
   - **Output:** drill recovery map (e.g., `Delilah/outputs/drill_recovery_map.json`).
2. **Saphira** — sync drill artifacts to safe storage.
   - **Output:** drill sync log (e.g., `Saphira/logs/drill_sync.log`).
3. **Corin** — verify drill integrity checks.
   - **Output:** drill integrity report (e.g., `Corin/reports/drill_integrity.md`).
4. **Rhea** — record drill outcomes and follow-ups.
   - **Output:** drill summary (e.g., `Rhea/reports/drill_summary.md`).

### Archive Healing
1. **Saphira** — scan and mend archive fragments.
   - **Output:** healing log (e.g., `Saphira/logs/archive_heal.log`).
2. **Corin** — verify healed artifacts and checksums.
   - **Output:** verification report (e.g., `Corin/reports/archive_verification.json`).
3. **Dave** — emit a recovery report for operators.
   - **Output:** recovery report (e.g., `Dave/reports/archive_recovery.md`).

### Artifact Labeling & Shelving
1. **Label** — auto-tag unclassified artifacts.
   - **Output:** tag set (e.g., `Label/outputs/tag_set.json`).
2. **Mila** — allocate shelves and bins.
   - **Output:** shelf map (e.g., `Mila/outputs/shelf_map.json`).
3. **PattyMae** — produce human-readable catalog.
   - **Output:** catalog (e.g., `PattyMae/outputs/catalog.pdf`).

## Knowledge & Lore

### Knowledge Base Refresh
1. **Lex** — harvest new entries and definitions.
   - **Output:** lexicon delta (e.g., `Lex/outputs/lexicon_delta.json`).
2. **Lexos** — normalize formatting and tags.
   - **Output:** normalized lexicon (e.g., `Lexos/outputs/lexicon_normalized.json`).
3. **Nancy** — publish searchable index.
   - **Output:** index build (e.g., `Nancy/outputs/lexicon_index.zip`).

### Lore Sync & Canon Alignment
1. **Archivus** — gather canonical lore fragments.
   - **Output:** canon bundle (e.g., `Archivus/outputs/canon_bundle.zip`).
2. **Mythra** — reconcile conflicting myths.
   - **Output:** reconciliation notes (e.g., `Mythra/reports/myth_reconcile.md`).
3. **Lyra** — publish steward-facing canon brief.
   - **Output:** canon brief (e.g., `Lyra/outputs/canon_brief.md`).

### Memory Weave & Thread Stabilization
1. **Red_Thread_Pipeline** — map memory links and anchors.
   - **Output:** thread map (e.g., `Red_Thread_Pipeline/outputs/thread_map.json`).
2. **WeaverArcTracker** — analyze stability of woven arcs.
   - **Output:** stability report (e.g., `WeaverArcTracker/reports/arc_stability.md`).
3. **Rhea** — update registry with stabilized threads.
   - **Output:** registry update (e.g., `Rhea/outputs/thread_registry.json`).

### Story Compilation & Chapter Release
1. **Scribevein** — compile approved fragments into chapters.
   - **Output:** chapter draft (e.g., `Scribevein/outputs/chapter_draft.md`).
2. **Quill** — polish narrative flow and continuity.
   - **Output:** edited chapter (e.g., `Quill/outputs/chapter_edited.md`).
3. **Bellwrit** — generate final release scrolls.
   - **Output:** release scrolls (e.g., `Bellwrit/outputs/release_scrolls.pdf`).

### Identity Audit & Symbol Mapping
1. **Glypha** — extract symbol signatures from artifacts.
   - **Output:** symbol index (e.g., `Glypha/outputs/symbol_index.json`).
2. **Markbearer** — cross-reference identity marks.
   - **Output:** mark ledger (e.g., `Markbearer/outputs/mark_ledger.csv`).
3. **Rhea** — publish identity audit summary.
   - **Output:** audit summary (e.g., `Rhea/reports/identity_audit.md`).

## Experience & Comms

### Emotional Weather Report
1. **Moodmancer** — sample ambient emotional signals.
   - **Output:** mood telemetry (e.g., `Moodmancer/outputs/mood_telemetry.json`).
2. **Moodweaver** — weave signals into trend narrative.
   - **Output:** mood narrative (e.g., `Moodweaver/reports/mood_narrative.md`).
3. **Dave** — issue daily emotional forecast.
   - **Output:** forecast brief (e.g., `Dave/reports/emotion_forecast.md`).

### Creative Pulse & Prompt Forge
1. **Muse_Jr** — draft creative prompts.
   - **Output:** prompt list (e.g., `Muse_Jr/outputs/prompt_list.md`).
2. **Fable** — test narrative resonance.
   - **Output:** resonance notes (e.g., `Fable/reports/resonance_notes.md`).
3. **Glimmer** — package prompt kit.
   - **Output:** prompt kit (e.g., `Glimmer/outputs/prompt_kit.zip`).

### Interface Revision & UI Notes
1. **RitualGUI** — propose interface tweaks.
   - **Output:** UI change set (e.g., `RitualGUI/outputs/ui_change_set.json`).
2. **Prismari** — verify visual harmony.
   - **Output:** design critique (e.g., `Prismari/reports/design_critique.md`).
3. **Lyra** — draft release notes for UI updates.
   - **Output:** UI release notes (e.g., `Lyra/outputs/ui_release_notes.md`).

## Safety & Governance

### Risk Scan & Safety Review
1. **Shamir** — scan for policy violations.
   - **Output:** safety scan (e.g., `Shamir/reports/safety_scan.md`).
2. **Boudica** — assess operational risk level.
   - **Output:** risk assessment (e.g., `Boudica/outputs/risk_assessment.json`).
3. **Rhea** — compile safety readiness report.
   - **Output:** readiness report (e.g., `Rhea/reports/safety_readiness.md`).

## Wellbeing & Rhythm

### Quiet Hours & Restorative Pause
1. **Somni** — schedule restorative downtime blocks.
   - **Output:** rest schedule (e.g., `Somni/outputs/rest_schedule.json`).
2. **Solie** — dim nonessential daemons.
   - **Output:** dimming log (e.g., `Solie/logs/dimming.log`).
3. **Rhea** — confirm resume window and alerts.
   - **Output:** resume plan (e.g., `Rhea/outputs/resume_plan.md`).
