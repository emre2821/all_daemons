# Rhea Workflows

Concise, actionable orchestration flows Rhea can run by invoking existing daemons.
Each workflow lists the sequence and the expected outputs or artifacts.

## Startup & Health Check
1. **Rhea** — discover daemons and load registry.
   - **Output:** registry snapshot (e.g., `Rhea/outputs/daemon_registry.json`).
2. **Corin** — validate integrity of known files/manifests.
   - **Output:** integrity report (e.g., `Corin/reports/integrity_report.md`).
3. **Dave** — compile status summary for operators.
   - **Output:** health summary (e.g., `Dave/reports/health_summary.md`).

## Archive Healing
1. **Saphira** — scan and mend archive fragments.
   - **Output:** healed archive log (e.g., `Saphira/logs/archive_heal.log`).
2. **Corin** — verify healed artifacts and checksums.
   - **Output:** verification manifest (e.g., `Corin/reports/archive_verification.json`).
3. **Dave** — emit final recovery report.
   - **Output:** recovery report (e.g., `Dave/reports/archive_recovery.md`).

## Deployment & Propagation
1. **Seiros** — package and propagate daemon updates.
   - **Output:** deployment bundle (e.g., `Seiros/outputs/deploy_bundle.zip`).
2. **Riven** — run integration tests against deployed targets.
   - **Output:** test results (e.g., `Riven/reports/integration_results.xml`).
3. **Lyra** — prepare merge/rollout notes for steward review.
   - **Output:** rollout brief (e.g., `Lyra/outputs/rollout_brief.md`).

## Storage Allocation
1. **Mila** — evaluate storage needs and allocate shelves.
   - **Output:** allocation plan (e.g., `Mila/outputs/storage_plan.json`).
2. **Rhea** — update registry with new storage mappings.
   - **Output:** updated registry snapshot (e.g., `Rhea/outputs/daemon_registry.json`).
3. **Dave** — publish storage utilization summary.
   - **Output:** storage report (e.g., `Dave/reports/storage_summary.md`).

## Integration Testing
1. **Rhea** — assemble test targets and dependencies.
   - **Output:** test manifest (e.g., `Rhea/outputs/test_manifest.json`).
2. **Riven** — execute integration suite.
   - **Output:** test report (e.g., `Riven/reports/integration_results.xml`).
3. **Dave** — provide human-readable test digest.
   - **Output:** test digest (e.g., `Dave/reports/integration_digest.md`).

## Incident Recovery & File Rescue
1. **Delilah** — recover and rehome lost files.
   - **Output:** recovery map (e.g., `Delilah/outputs/recovery_map.json`).
2. **Saphira** — synchronize recovered archives.
   - **Output:** sync log (e.g., `Saphira/logs/recovery_sync.log`).
3. **Corin** — validate recovered paths.
   - **Output:** post-recovery integrity report (e.g., `Corin/reports/recovery_integrity.md`).
