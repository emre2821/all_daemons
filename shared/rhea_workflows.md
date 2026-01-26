# Rhea Workflows

Concise, actionable orchestration flows Rhea can run by invoking existing daemons.
Each workflow lists the sequence and the expected outputs or artifacts.

## Conventions
- **Roles:** Rhea orchestrates registry updates, Dave summarizes daemon activity, Corin validates integrity,
  Riven mends fractured logs and pulses system health, Saphira seeds DCA agents from inbox fragments,
  Delilah recovers files, Mila allocates storage, Seiros propagates deployments, and Lyra automates PR
  workflow notes and merge hygiene.
- **Paths:** Prefer daemon-native output locations (e.g., `Rhea/outputs/`, `Rhea/_outbox/`,
  `daemons/<Daemon>/*.log`, or daemon-specific stores like `~/.eden_ranger/`).
- **Pattern:** Artifacts follow daemon-owned paths (examples inline per workflow).

## Table of Contents
- [Operations & Reliability](#operations--reliability)
  - [Intake Triage & Task Prioritization](#intake-triage--task-prioritization)
  - [Startup & Health Check](#startup--health-check)
  - [Diagnostic Snapshot & Root Cause](#diagnostic-snapshot--root-cause)
  - [Signal Patrol & Anomaly Alerting](#signal-patrol--anomaly-alerting)
  - [Config Drift Audit](#config-drift-audit)
  - [Registry Rebuild & Sync](#registry-rebuild--sync)
  - [Incident Remediation Pack](#incident-remediation-pack)
- [Deployment & Testing](#deployment--testing)
  - [Test Environment Spin-up](#test-environment-spin-up)
  - [Integration Validation](#integration-validation)
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
  - [Identity & Law Registry Refresh](#identity--law-registry-refresh)
  - [Lore Sync & Canon Alignment](#lore-sync--canon-alignment)
  - [Memory Weave & Thread Stabilization](#memory-weave--thread-stabilization)
  - [Story Signals & Release Notifications](#story-signals--release-notifications)
  - [Identity Audit & Symbol Mapping](#identity-audit--symbol-mapping)
- [Experience & Comms](#experience--comms)
  - [Emotional Weather Report](#emotional-weather-report)
  - [Creative Pulse & Prompt Forge](#creative-pulse--prompt-forge)
  - [Interface Revision & UI Notes](#interface-revision--ui-notes)
- [Safety & Governance](#safety--governance)
  - [Network Safety & Risk Review](#network-safety--risk-review)
- [Wellbeing & Rhythm](#wellbeing--rhythm)
  - [Quiet Hours & Restorative Pause](#quiet-hours--restorative-pause)

## Operations & Reliability

### Intake Triage & Task Prioritization
1. **Aderyn** — scan Janvier exports for summon phrases and archive detected summons.
   - **Output:** summons archive (e.g., `Rhea/outputs/from_Aderyn/chaos_library/*.chaos`).
2. **Harper** — check system pressure to gauge intake capacity.
   - **Output:** pressure alerts (e.g., `Rhea/_outbox/Harper/harper_alerts.log`).
3. **Dave** — summarize intake signals and daemon activity for operators.
   - **Output:** activity summary (e.g., `Rhea/_outbox/dave/leaderboard.json`).

### Startup & Health Check
1. **Rhea** — discover daemons and load the registry snapshot.
   - **Output:** registry snapshot (e.g., `Rhea/outputs/daemon_registry.json`).
2. **Corin** — validate integrity of known files and manifests.
   - **Output:** integrity log (e.g., `daemons/Corin/corin.log`).
3. **Dave** — compile an operator-ready health summary.
   - **Output:** health summary (e.g., `Rhea/_outbox/dave/leaderboard.json`).

### Diagnostic Snapshot & Root Cause
1. **Ranger** — capture a file-catalog snapshot for traceability.
   - **Output:** ranger index (e.g., `~/.eden_ranger/ranger.db`).
2. **Dagr** — trigger daemon sync cycles and log activation outcomes.
   - **Output:** activation log (e.g., `specialty_folders/Dagr/dagr.log`).
3. **Riven** — mend fractured CHAOS logs after the diagnostic run.
   - **Output:** restored logs (e.g., `restored_logs/*.chaos`).

### Signal Patrol & Anomaly Alerting
1. **Tempest** — score CHAOS threads for tension spikes.
   - **Output:** score log (e.g., `Rhea/_outbox/tempest/tempest_scores.json`).
2. **Whisperfang** — scan incoming text for flagged keywords and log detections.
   - **Output:** detection log (e.g., `daemons/Whisperfang/whisperfang.log`).
3. **Dave** — dispatch alert summary from the collected logs.
   - **Output:** alert summary (e.g., `Rhea/_outbox/dave/alerts.json`).

### Config Drift Audit
1. **Rhea** — collect current registry config and targets.
   - **Output:** config snapshot (e.g., `Rhea/outputs/config_snapshot.json`).
2. **Seiros** — propagate the snapshot to registered nodes and report applied configs.
   - **Output:** console log (capture if needed for audit).
3. **Corin** — validate diffs and flag unsafe deltas.
   - **Output:** drift validation log (e.g., `daemons/Corin/corin.log`).
4. **Dave** — summarize drift impact for operators.
   - **Output:** drift summary (e.g., `Rhea/_outbox/dave/leaderboard.json`).

### Registry Rebuild & Sync
1. **Mila** — scan shelves and organize daemon folders into storage categories.
   - **Output:** updated daemon directories (e.g., `daemons/<Name>/{logs,configs,scripts}/`).
2. **Rhea** — rebuild the registry from scanned sources.
   - **Output:** rebuilt registry (e.g., `Rhea/outputs/daemon_registry.json`).
3. **Saphira** — seed DCA agents from inbox fragments to repopulate the registry.
   - **Output:** seeded agents (e.g., `Rhea/outputs/Saphira/agents/*.agent.json`).
4. **Corin** — validate rebuilt registry integrity.
   - **Output:** registry validation log (e.g., `daemons/Corin/corin.log`).

### Incident Remediation Pack
1. **Dave** — assemble incident facts from daemon logs.
   - **Output:** incident brief (e.g., `Rhea/_outbox/dave/alerts.json`).
2. **Lyra** — generate PR automation notes for remediation work.
   - **Output:** PR automation log (e.g., `lyra.log`).
3. **Rhea** — approve remediation plan and registry notes.
   - **Output:** remediation plan (e.g., `Rhea/outputs/remediation_plan.json`).

## Deployment & Testing

### Test Environment Spin-up
1. **Seiros** — provision test targets and deploy seed configs.
   - **Output:** deployment log (capture console output for audit).
2. **Mila** — allocate storage for test artifacts.
   - **Output:** updated daemon storage folders (e.g., `daemons/<Name>/{logs,configs,scripts}/`).
3. **Rhea** — register test nodes and dependencies.
   - **Output:** test registry (e.g., `Rhea/outputs/test_registry.json`).
4. **Harper** — check system pressure before opening the environment to load.
   - **Output:** pressure alerts (e.g., `Rhea/_outbox/Harper/harper_alerts.log`).

### Integration Validation
1. **Rhea** — assemble integration targets and dependencies.
   - **Output:** integration manifest (e.g., `Rhea/outputs/test_manifest.json`).
2. **Harper** — monitor pressure and backlog while integrations run.
   - **Output:** pressure alerts (e.g., `Rhea/_outbox/Harper/harper_alerts.log`).
3. **Riven** — mend any fractured CHAOS logs produced during the run.
   - **Output:** restored logs (e.g., `restored_logs/*.chaos`).
4. **Dave** — publish an operator-ready integration digest.
   - **Output:** integration digest (e.g., `Rhea/_outbox/dave/leaderboard.json`).

### Release Gate Review
1. **Harper** — run a final pressure check before release.
   - **Output:** pressure alerts (e.g., `Rhea/_outbox/Harper/harper_alerts.log`).
2. **Corin** — confirm manifest and checksum integrity.
   - **Output:** gate integrity log (e.g., `daemons/Corin/corin.log`).
3. **Rhea** — record go/no-go decision with rationale.
   - **Output:** gate decision (e.g., `Rhea/outputs/gate_decision.json`).
4. **Lyra** — prepare PR automation summary for steward review.
   - **Output:** PR automation log (e.g., `lyra.log`).

### Deployment & Propagation
1. **Seiros** — package and propagate daemon updates.
   - **Output:** deployment log (capture console output for audit).
2. **Harper** — monitor pressure and backlog during propagation.
   - **Output:** pressure alerts (e.g., `Rhea/_outbox/Harper/harper_alerts.log`).
3. **Lyra** — prepare PR automation summary for steward review.
   - **Output:** PR automation log (e.g., `lyra.log`).

### Hotfix Rollback & Containment
1. **Seiros** — roll back to the last stable deployment.
   - **Output:** rollback log (capture console output for audit).
2. **Delilah** — draft a recovery map for any displaced files.
   - **Output:** recovery map (e.g., `Rhea/_recovery_logs/plan_*.vas`).
3. **Riven** — mend any fractured logs detected after rollback.
   - **Output:** restored logs (e.g., `restored_logs/*.chaos`).
4. **Dave** — communicate rollback impact summary.
   - **Output:** rollback summary (e.g., `Rhea/_outbox/dave/alerts.json`).

### Schema Migration Prep
1. **Rhea** — assemble migration manifest and dependencies.
   - **Output:** migration manifest (e.g., `Rhea/outputs/migration_manifest.json`).
2. **Corin** — validate schema compatibility.
   - **Output:** compatibility log (e.g., `daemons/Corin/corin.log`).
3. **Seiros** — package migration tooling and rollout plan.
   - **Output:** rollout log (capture console output for audit).
4. **Mila** — reserve storage for pre-migration backups.
   - **Output:** updated daemon folders (e.g., `daemons/<Name>/{archives,logs}/`).

## Data & Storage

### Storage Allocation
1. **Mila** — evaluate storage needs and allocate shelves.
   - **Output:** updated daemon folders (e.g., `daemons/<Name>/{logs,configs,scripts}/`).
2. **Rhea** — update registry with new storage mappings.
   - **Output:** registry snapshot (e.g., `Rhea/outputs/daemon_registry.json`).
3. **Dave** — publish a storage utilization summary.
   - **Output:** storage summary (e.g., `Rhea/_outbox/dave/leaderboard.json`).

### Capacity Forecast & Budget
1. **Mila** — scan current storage layout and usage hotspots.
   - **Output:** updated daemon folders (e.g., `daemons/<Name>/{logs,configs,scripts}/`).
2. **Dave** — translate current utilization into budget guidance.
   - **Output:** capacity brief (e.g., `Rhea/_outbox/dave/leaderboard.json`).
3. **Rhea** — update registry thresholds and alerts.
   - **Output:** threshold update (e.g., `Rhea/outputs/storage_thresholds.json`).

### Log Hygiene & Rotation
1. **Mila** — rotate logs and enforce retention limits.
   - **Output:** updated daemon folders (e.g., `daemons/<Name>/logs/`).
2. **Archive** — convert and catalog rotated logs.
   - **Output:** archive log (e.g., `Rhea/_logs/archive_daemon.log`).
3. **Rhea** — record log locations in the registry.
   - **Output:** log registry update (e.g., `Rhea/outputs/log_registry.json`).

### Backup Rotation & Verification
1. **Archive** — run scheduled backup conversions and catalog the results.
   - **Output:** archive log (e.g., `Rhea/_logs/archive_daemon.log`).
2. **Corin** — verify backup integrity.
   - **Output:** backup verification log (e.g., `daemons/Corin/corin.log`).
3. **Mila** — store backups on allocated shelves.
   - **Output:** updated daemon folders (e.g., `daemons/<Name>/{archives,logs}/`).
4. **Dave** — publish backup status report.
   - **Output:** backup report (e.g., `Rhea/_outbox/dave/leaderboard.json`).

### Data Retention Review
1. **Mila** — audit retention windows and storage usage.
   - **Output:** updated daemon folders (e.g., `daemons/<Name>/{archives,logs}/`).
2. **Archive** — stage archival conversions for expiring data.
   - **Output:** archive log (e.g., `Rhea/_logs/archive_daemon.log`).
3. **Rhea** — update registry policies and flags.
   - **Output:** retention policy update (e.g., `Rhea/outputs/retention_policy.json`).

## Recovery & Integrity

### Incident Recovery & File Rescue
1. **Delilah** — recover and rehome lost files.
   - **Output:** recovery map (e.g., `Rhea/_recovery_logs/plan_*.vas`).
2. **Archive** — convert and catalog recovered archives.
   - **Output:** archive log (e.g., `Rhea/_logs/archive_daemon.log`).
3. **Corin** — validate recovered paths and integrity.
   - **Output:** integrity log (e.g., `daemons/Corin/corin.log`).

### Recovery Drill
1. **Delilah** — perform sample recovery on drill data.
   - **Output:** drill recovery map (e.g., `Rhea/_recovery_logs/plan_*.vas`).
2. **Archive** — catalog drill artifacts for audit.
   - **Output:** archive log (e.g., `Rhea/_logs/archive_daemon.log`).
3. **Corin** — verify drill integrity checks.
   - **Output:** drill integrity log (e.g., `daemons/Corin/corin.log`).
4. **Rhea** — record drill outcomes and follow-ups.
   - **Output:** drill summary (e.g., `Rhea/reports/drill_summary.md`).

### Archive Healing
1. **Archive** — scan and convert archive fragments.
   - **Output:** healing log (e.g., `Rhea/_logs/archive_daemon.log`).
2. **Corin** — verify healed artifacts and checksums.
   - **Output:** verification log (e.g., `daemons/Corin/corin.log`).
3. **Dave** — emit a recovery report for operators.
   - **Output:** recovery report (e.g., `Rhea/_outbox/dave/leaderboard.json`).

### Artifact Labeling & Shelving
1. **Label** — auto-tag unclassified artifacts.
   - **Output:** labeled artifacts (e.g., `Rhea/outputs/Label/labeled/*.json`).
2. **Mila** — allocate shelves and bins.
   - **Output:** updated daemon folders (e.g., `daemons/<Name>/{logs,configs,scripts}/`).
3. **PattyMae** — produce human-readable catalog.
   - **Output:** organized CHAOS bundles (e.g., `Rhea/PattyMae/organized/`).

## Knowledge & Lore

### Identity & Law Registry Refresh
1. **Lex** — update identity records and log CHAOS events.
   - **Output:** identity store and logs (e.g., `~/EdenVault/identities.json`, `~/EdenVault/logs/*.chaos`).
2. **Lexos** — sort consent/law/ethics documents into Eden_Laws.
   - **Output:** tagged files (e.g., `Eden_Laws/{informed_consent,system_decrees,ethics}/`).
3. **Nancy** — log mood-aligned ritual invocations.
   - **Output:** ritual log (e.g., `.../Nancy_Logs/memorymap.md`).

### Lore Sync & Canon Alignment
1. **Archivus** — recover CHAOS fragments for canon review.
   - **Output:** recovered queue (e.g., `specialty_folders/Archivus/chaos_queue/`).
2. **Mythra** — mythify recovered logs into narrative epics.
   - **Output:** epic drafts (e.g., `epics/*.chaosong`).
3. **Lyra** — publish a canon update summary via PR automation.
   - **Output:** PR automation log (e.g., `lyra.log`).

### Memory Weave & Thread Stabilization
1. **Threadstep** — map memory links and anchors via path tracing.
   - **Output:** trace log (e.g., `daemons/_logs/Threadstep.log`).
2. **WeaverArcTracker** — record the state of woven arcs.
   - **Output:** arc status record (e.g., `daemons/WeaverArcTracker/weaverarctracker.py`).
3. **Rhea** — update registry with stabilized threads.
   - **Output:** registry update (e.g., `Rhea/outputs/thread_registry.json`).

### Story Signals & Release Notifications
1. **Scribevein** — archive incoming story fragments from the communication stream.
   - **Output:** archive log (e.g., `scribevein.log`).
2. **Quill** — label narrative fragments with tags and tonal cues.
   - **Output:** labeled metadata (printed JSON per file).
3. **Bellwrit** — notify when new narrative entries land.
   - **Output:** notification log (e.g., `specialty_folders/Bellwrit/bellwrit.log`).

### Identity Audit & Symbol Mapping
1. **Glypha** — extract symbol signatures from artifacts.
   - **Output:** generated sigils (e.g., `sigils/sigil_*.png`).
2. **Markbearer** — cross-reference identity marks.
   - **Output:** mark ledger (e.g., `markbearer_log.json`).
3. **Rhea** — publish identity audit summary.
   - **Output:** audit summary (e.g., `Rhea/reports/identity_audit.md`).

## Experience & Comms

### Emotional Weather Report
1. **Moodmancer** — sample ambient emotional signals.
   - **Output:** mood log (e.g., `~/CHAOS_Logs/mood_log.txt`).
2. **Moodweaver** — weave signals into trend narrative.
   - **Output:** mood memory (e.g., `moodweaver.json`).
3. **Dave** — issue daily emotional forecast.
   - **Output:** forecast brief (e.g., `Rhea/_outbox/dave/leaderboard.json`).

### Creative Pulse & Prompt Forge
1. **Muse_Jr** — draft creative prompts.
   - **Output:** CHAOS prompt entries (e.g., `~/Dropbox/CHAOS_Logs/ping_*.chaos`).
2. **Fable** — test narrative resonance.
   - **Output:** memory records (e.g., `eden_memory.db`).
3. **Glimmer** — package prompt kit.
   - **Output:** emotion scan log (e.g., `glimmer_log.json`).

### Interface Revision & UI Notes
1. **RitualGUI** — propose interface tweaks.
   - **Output:** ritual definition files (e.g., `*.chaos` saved from the UI).
2. **Prismari** — verify visual harmony.
   - **Output:** palette commentary (printed or captured via stdout).
3. **Lyra** — draft PR automation notes for UI updates.
   - **Output:** PR automation log (e.g., `lyra.log`).

## Safety & Governance

### Network Safety & Risk Review
1. **Shamir** — verify VPN tunnel status and network guard posture.
   - **Output:** status output (captured from stdout).
2. **Boudica** — scan code for structural risk signals (e.g., undefined variables).
   - **Output:** scan output (printed to stdout).
3. **Rhea** — compile safety readiness report.
   - **Output:** readiness report (e.g., `Rhea/reports/safety_readiness.md`).

## Wellbeing & Rhythm

### Quiet Hours & Restorative Pause
1. **Somni** — schedule restorative downtime blocks.
   - **Output:** dreamline extracts (e.g., `Rhea/_outbox/somni/dreamlines.json`).
2. **Solie** — dim nonessential daemons.
   - **Output:** holdspace fragments (e.g., `solacebay/solie_*.chaos`).
3. **Rhea** — confirm resume window and alerts.
   - **Output:** resume plan (e.g., `Rhea/outputs/resume_plan.md`).
