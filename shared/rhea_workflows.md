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

---

# Housekeeping Ops Deck (Brom's Clean-Up Crew)

Structured, clickable task list for large-scale cleanup operations. Each task can be
started by Rhea directly from this file.

## Common
- [ ] **Start Task — Baskets & Broom**
  - **Use:** everyday mixed files and intake drops.
  - **Crew:** PattyMae, Label, Mila, Brom.
  - **Steps:** Bucket → Label → Rename → Shelf.
  - **Outputs:** `PattyMae/organized/` batches, updated shelf map.

- [ ] **Start Task — Shelf-Law Sweep**
  - **Use:** storage bloat or uneven folder growth.
  - **Crew:** Mila, Brom, Ledger_Jr.
  - **Steps:** Audit shelves → Move weight → Log map.
  - **Outputs:** storage plan + relocation log.

- [ ] **Start Task — Tidy Echoes**
  - **Use:** log clutter and scattered audit trails.
  - **Crew:** Ledger_Jr, Codexa, Label.
  - **Steps:** Consolidate → Index → Normalize names.
  - **Outputs:** indexed log set + naming report.

- [ ] **Start Task — Gentle Triage**
  - **Use:** daily intake backlog that needs fast sorting.
  - **Crew:** PattyMae, Label.
  - **Steps:** Sort by type → Apply base tags.
  - **Outputs:** categorized intake batches.

- [ ] **Start Task — Rename Rumble**
  - **Use:** chaotic filenames, duplicates, and "final_final" sprawl.
  - **Crew:** Brom, Label.
  - **Steps:** Detect chaos → Suggest names → Force rename.
  - **Outputs:** rename report + clean filenames.

- [ ] **Start Task — Basket Brigade**
  - **Use:** inbox overload from multiple sources.
  - **Crew:** PattyMae, Mila.
  - **Steps:** Stage intake → Sort by origin → Reshelve.
  - **Outputs:** staged intake list + shelf placements.

- [ ] **Start Task — Quick Index**
  - **Use:** small archive sets that need rapid discoverability.
  - **Crew:** Codexa, Label.
  - **Steps:** Extract keywords → Apply taxonomy → Index.
  - **Outputs:** mini-index file + label map.

## Uncommon
- [ ] **Start Task — Manifest Mend**
  - **Use:** missing or inconsistent manifests.
  - **Crew:** Saphira, Archivus, Mila.
  - **Steps:** Rebuild → Validate → Reshelve.
  - **Outputs:** repaired manifest + storage re-map.

- [ ] **Start Task — Quiet Re-Shelving**
  - **Use:** large reorg without disruption.
  - **Crew:** Mila, PattyMae, Label, Ledger_Jr.
  - **Steps:** Stage → Bucket → Label → Log.
  - **Outputs:** revised shelf map + audit log.

- [ ] **Start Task — Ash & Ember Reset**
  - **Use:** messy aftermaths and stalled cleanup.
  - **Crew:** Scorchick, AshFall, Brom.
  - **Steps:** Kickstart → Clear debris → Force tidy.
  - **Outputs:** cleared backlog + cleanup report.

- [ ] **Start Task — Codex Reweave**
  - **Use:** knowledge base drift or fractured indexes.
  - **Crew:** Codexa, Saphira, Label.
  - **Steps:** Reindex → Repair links → Normalize names.
  - **Outputs:** refreshed index + link audit.

- [ ] **Start Task — Thread Taxonomy**
  - **Use:** unlabeled thread archives.
  - **Crew:** Label, PattyMae, Ledger_Jr.
  - **Steps:** Cluster → Tag → Log.
  - **Outputs:** taxonomy map + ledger entry.

- [ ] **Start Task — Patch & Sweep**
  - **Use:** small integrity issues during cleanup.
  - **Crew:** Corin, Saphira, Brom.
  - **Steps:** Detect anomalies → Repair → Refile.
  - **Outputs:** integrity patch notes.

- [ ] **Start Task — Mirror Polish**
  - **Use:** file mirrors are out of sync.
  - **Crew:** Saphira, Codexa, Ledger_Jr.
  - **Steps:** Compare mirrors → Sync → Record.
  - **Outputs:** mirror sync log.

## Rare
- [ ] **Start Task — Archive Exodus**
  - **Use:** major archival migration or consolidation.
  - **Crew:** Archivus, Mila, Ledger_Jr, Brom.
  - **Steps:** Decide what stays → Move → Record.
  - **Outputs:** migration plan + new archive index.

- [ ] **Start Task — Sanctuary Lockdown**
  - **Use:** sensitive memory zones with strict preservation.
  - **Crew:** Archivus, Saphira, Ledger_Jr.
  - **Steps:** Seal rules → Repair gaps → Chain-of-custody log.
  - **Outputs:** protected vault manifest.

- [ ] **Start Task — Duplicate Drift Hunt**
  - **Use:** shadow copies scattered across shelves.
  - **Crew:** Brom, Codexa, Ledger_Jr.
  - **Steps:** Detect twins → Merge/mark → Log.
  - **Outputs:** dedupe map + log.

- [ ] **Start Task — Shelfquake Stabilize**
  - **Use:** folders collapsing after big imports.
  - **Crew:** Mila, PattyMae, Brom.
  - **Steps:** Reinforce structure → Refile → Rename if needed.
  - **Outputs:** stabilized shelf tree.

- [ ] **Start Task — Memory Loom**
  - **Use:** re-threading context across files.
  - **Crew:** Saphira, Codexa, Ledger_Jr.
  - **Steps:** Trace relationships → Restore links → Record.
  - **Outputs:** relationship map + ledger.

- [ ] **Start Task — Cold Storage Flip**
  - **Use:** moving dormant files to long-term archive.
  - **Crew:** Mila, Archivus, Label.
  - **Steps:** Identify dormant → Seal → Reindex.
  - **Outputs:** cold storage registry.

- [ ] **Start Task — Quiet Curator**
  - **Use:** curate a clean collection for retrieval.
  - **Crew:** PattyMae, Codexa, Label.
  - **Steps:** Select → Label → Index.
  - **Outputs:** curated collection index.

## Very Rare
- [ ] **Start Task — The Long Winter**
  - **Use:** weeks-long system cleanup.
  - **Crew:** Mila, PattyMae, Label, Brom, Ledger_Jr, Saphira.
  - **Steps:** Phase map → Daily sorting → Force ops → Repair manifests.
  - **Outputs:** phased cleanup ledger + manifest repair log.

- [ ] **Start Task — Ashfall Aftermath**
  - **Use:** catastrophic disorder event.
  - **Crew:** Scorchick, AshFall, Mila, Brom.
  - **Steps:** Triage → Clear → Reshelve.
  - **Outputs:** incident cleanup report.

- [ ] **Start Task — Golden Index**
  - **Use:** canonical master index rebuild.
  - **Crew:** Codexa, Saphira, Archivus.
  - **Steps:** Extract truth → Re-index → Preserve.
  - **Outputs:** golden index file.

- [ ] **Start Task — Silent Vault**
  - **Use:** high-security preservation vault.
  - **Crew:** Archivus, Saphira, Ledger_Jr.
  - **Steps:** Define sacred → Seal → Immutable log.
  - **Outputs:** sealed vault manifest.

- [ ] **Start Task — Log Tide Reversal**
  - **Use:** extreme log overflow.
  - **Crew:** Ledger_Jr, Codexa, Mila.
  - **Steps:** Summarize → Archive → Reshelve.
  - **Outputs:** summary digest + archived logs.

## Legendary
- [ ] **Start Task — The White Glove Protocol**
  - **Use:** prestige cleanup with flawless order.
  - **Crew:** PattyMae, Label, Mila, Codexa, Brom.
  - **Steps:** Prep → Label perfection → Shelf symmetry → Final polish.
  - **Outputs:** pristine shelf map + index.

- [ ] **Start Task — Midnight Library**
  - **Use:** restore forgotten or lost works.
  - **Crew:** Saphira, Archivus, Codexa.
  - **Steps:** Recover fragments → Rebind → Archive.
  - **Outputs:** restored archive catalog.

- [ ] **Start Task — The Great Confluence**
  - **Use:** merge multiple archives into one system.
  - **Crew:** Mila, Saphira, Archivus, Ledger_Jr, Brom.
  - **Steps:** Map sources → Merge → Record new lineage.
  - **Outputs:** unified archive index + lineage log.

- [ ] **Start Task — Ember-Clean of the Undercroft**
  - **Use:** purge old cache/decay across obscure dirs.
  - **Crew:** Scorchick, AshFall, Brom.
  - **Steps:** Sweep hidden zones → Clear → Rename.
  - **Outputs:** purge log + cleanup report.

- [ ] **Start Task — The Loom of Quiet Things**
  - **Use:** weave labels + logs into gentle continuity.
  - **Crew:** Label, Ledger_Jr, Saphira.
  - **Steps:** Align tags → Stitch logs → Preserve.
  - **Outputs:** continuity map + ledger.

- [ ] **Start Task — Beacon of Order**
  - **Use:** emergency organization when the system feels chaotic.
  - **Crew:** Mila, PattyMae, Corin, Brom.
  - **Steps:** Stabilize → Sort → Validate → Finalize.
  - **Outputs:** stabilization report + shelf map.
