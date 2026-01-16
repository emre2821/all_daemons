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
- [Diagnostics & Operations](#diagnostics--operations)
  - [Startup & Health Check](#startup--health-check)
  - [Deployment & Propagation](#deployment--propagation)
  - [Integration Testing](#integration-testing)
- [Lore & Memory Stewardship](#lore--memory-stewardship)
  - [Archive Healing](#archive-healing)
  - [Incident Recovery & File Rescue](#incident-recovery--file-rescue)
  - [Artifact Labeling & Shelving](#artifact-labeling--shelving)
- [Capacity & Storage](#capacity--storage)
  - [Storage Allocation](#storage-allocation)

## Diagnostics & Operations

### Startup & Health Check
1. **Rhea** — discover daemons and load the registry snapshot.
   - **Output:** registry snapshot (e.g., `Rhea/outputs/daemon_registry.json`).
2. **Corin** — validate integrity of known files and manifests.
   - **Output:** integrity report (e.g., `Corin/reports/integrity_report.md`).
3. **Dave** — compile an operator-ready health summary.
   - **Output:** health summary (e.g., `Dave/reports/health_summary.md`).

### Deployment & Propagation
1. **Seiros** — package and propagate daemon updates.
   - **Output:** deployment bundle (e.g., `Seiros/outputs/deploy_bundle.zip`).
2. **Riven** — run integration tests against deployed targets.
   - **Output:** test results (e.g., `Riven/reports/integration_results.xml`).
3. **Lyra** — prepare rollout notes for steward review.
   - **Output:** rollout brief (e.g., `Lyra/outputs/rollout_brief.md`).

### Integration Testing
1. **Rhea** — assemble test targets and dependencies.
   - **Output:** test manifest (e.g., `Rhea/outputs/test_manifest.json`).
2. **Riven** — execute the integration suite.
   - **Output:** test results (e.g., `Riven/reports/integration_results.xml`).
3. **Dave** — publish an operator-ready test digest.
   - **Output:** test digest (e.g., `Dave/reports/integration_digest.md`).

## Lore & Memory Stewardship

### Archive Healing
1. **Saphira** — scan and mend archive fragments.
   - **Output:** healing log (e.g., `Saphira/logs/archive_heal.log`).
2. **Corin** — verify healed artifacts and checksums.
   - **Output:** verification report (e.g., `Corin/reports/archive_verification.json`).
3. **Dave** — emit a recovery report for operators.
   - **Output:** recovery report (e.g., `Dave/reports/archive_recovery.md`).

### Incident Recovery & File Rescue
1. **Delilah** — recover and rehome lost files.
   - **Output:** recovery map (e.g., `Delilah/outputs/recovery_map.json`).
2. **Saphira** — synchronize recovered archives.
   - **Output:** sync log (e.g., `Saphira/logs/recovery_sync.log`).
3. **Corin** — validate recovered paths and integrity.
   - **Output:** integrity report (e.g., `Corin/reports/recovery_integrity.md`).

### Artifact Labeling & Shelving
1. **Label** — auto-tag unclassified artifacts.
   - **Output:** tag set (e.g., `Label/outputs/tag_set.json`).
2. **Archivus** — place labeled artifacts into cataloged shelves.
   - **Output:** shelving manifest (e.g., `Archivus/outputs/shelving_manifest.json`).
3. **Rhea** — update the registry with new shelf mappings.
   - **Output:** registry snapshot (e.g., `Rhea/outputs/daemon_registry.json`).

## Capacity & Storage

### Storage Allocation
1. **Mila** — evaluate storage needs and allocate shelves.
   - **Output:** allocation plan (e.g., `Mila/outputs/storage_plan.json`).
2. **Rhea** — update registry with new storage mappings.
   - **Output:** registry snapshot (e.g., `Rhea/outputs/daemon_registry.json`).
3. **Dave** — publish a storage utilization summary.
   - **Output:** storage report (e.g., `Dave/reports/storage_summary.md`).
