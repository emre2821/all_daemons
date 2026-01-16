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

## Lore Sync & Canon Alignment
1. **Archivus** — gather canonical lore fragments.
   - **Output:** canon bundle (e.g., `Archivus/outputs/canon_bundle.zip`).
2. **Mythra** — reconcile conflicting myths.
   - **Output:** reconciliation notes (e.g., `Mythra/reports/myth_reconcile.md`).
3. **Lyra** — publish steward-facing canon brief.
   - **Output:** canon brief (e.g., `Lyra/outputs/canon_brief.md`).

## Memory Weave & Thread Stabilization
1. **Red_Thread_Pipeline** — map memory links and anchors.
   - **Output:** thread map (e.g., `Red_Thread_Pipeline/outputs/thread_map.json`).
2. **WeaverArcTracker** — analyze stability of woven arcs.
   - **Output:** stability report (e.g., `WeaverArcTracker/reports/arc_stability.md`).
3. **Rhea** — update registry with stabilized threads.
   - **Output:** registry update (e.g., `Rhea/outputs/thread_registry.json`).

## Story Compilation & Chapter Release
1. **Scribevein** — compile approved fragments into chapters.
   - **Output:** chapter draft (e.g., `Scribevein/outputs/chapter_draft.md`).
2. **Quill** — polish narrative flow and continuity.
   - **Output:** edited chapter (e.g., `Quill/outputs/chapter_edited.md`).
3. **Bellwrit** — generate final release scrolls.
   - **Output:** release scrolls (e.g., `Bellwrit/outputs/release_scrolls.pdf`).

## Identity Audit & Symbol Mapping
1. **Glypha** — extract symbol signatures from artifacts.
   - **Output:** symbol index (e.g., `Glypha/outputs/symbol_index.json`).
2. **Markbearer** — cross-reference identity marks.
   - **Output:** mark ledger (e.g., `Markbearer/outputs/mark_ledger.csv`).
3. **Rhea** — publish identity audit summary.
   - **Output:** audit summary (e.g., `Rhea/reports/identity_audit.md`).

## Emotional Weather Report
1. **Moodmancer** — sample ambient emotional signals.
   - **Output:** mood telemetry (e.g., `Moodmancer/outputs/mood_telemetry.json`).
2. **Moodweaver** — weave signals into trend narrative.
   - **Output:** mood narrative (e.g., `Moodweaver/reports/mood_narrative.md`).
3. **Dave** — issue daily emotional forecast.
   - **Output:** forecast brief (e.g., `Dave/reports/emotion_forecast.md`).

## Quiet Hours & Restorative Pause
1. **Somni** — schedule restorative downtime blocks.
   - **Output:** rest schedule (e.g., `Somni/outputs/rest_schedule.json`).
2. **Solie** — dim nonessential daemons.
   - **Output:** dimming log (e.g., `Solie/logs/dimming.log`).
3. **Rhea** — confirm resume window and alerts.
   - **Output:** resume plan (e.g., `Rhea/outputs/resume_plan.md`).

## Intake Triage & Task Prioritization
1. **Aderyn** — triage incoming requests by urgency.
   - **Output:** triage queue (e.g., `Aderyn/outputs/triage_queue.json`).
2. **Harper** — assign owners and deadlines.
   - **Output:** assignment sheet (e.g., `Harper/outputs/assignments.csv`).
3. **Dave** — send prioritized task brief.
   - **Output:** task brief (e.g., `Dave/reports/task_brief.md`).

## Knowledge Base Refresh
1. **Lex** — harvest new entries and definitions.
   - **Output:** lexicon delta (e.g., `Lex/outputs/lexicon_delta.json`).
2. **Lexos** — normalize formatting and tags.
   - **Output:** normalized lexicon (e.g., `Lexos/outputs/lexicon_normalized.json`).
3. **Nancy** — publish searchable index.
   - **Output:** index build (e.g., `Nancy/outputs/lexicon_index.zip`).

## Diagnostic Snapshot & Root Cause
1. **Ranger** — capture system telemetry snapshot.
   - **Output:** telemetry bundle (e.g., `Ranger/outputs/telemetry_bundle.zip`).
2. **Dagr** — isolate fault patterns.
   - **Output:** root-cause memo (e.g., `Dagr/reports/root_cause.md`).
3. **Riven** — validate fix hypotheses with tests.
   - **Output:** validation report (e.g., `Riven/reports/hypothesis_validation.xml`).

## Artifact Labeling & Shelving
1. **Label** — auto-tag unclassified artifacts.
   - **Output:** tag set (e.g., `Label/outputs/tag_set.json`).
2. **Mila** — allocate shelves and bins.
   - **Output:** shelf map (e.g., `Mila/outputs/shelf_map.json`).
3. **PattyMae** — produce human-readable catalog.
   - **Output:** catalog (e.g., `PattyMae/outputs/catalog.pdf`).

## Signal Patrol & Anomaly Alerting
1. **Tempest** — scan for disruptive surges.
   - **Output:** surge log (e.g., `Tempest/logs/surge_log.json`).
2. **Whisperfang** — confirm anomalies with heuristics.
   - **Output:** anomaly report (e.g., `Whisperfang/reports/anomaly_report.md`).
3. **Dave** — dispatch alert summary.
   - **Output:** alert summary (e.g., `Dave/reports/alert_summary.md`).

## Interface Revision & UI Notes
1. **RitualGUI** — propose interface tweaks.
   - **Output:** UI change set (e.g., `RitualGUI/outputs/ui_change_set.json`).
2. **Prismari** — verify visual harmony.
   - **Output:** design critique (e.g., `Prismari/reports/design_critique.md`).
3. **Lyra** — draft release notes for UI updates.
   - **Output:** UI release notes (e.g., `Lyra/outputs/ui_release_notes.md`).

## Risk Scan & Safety Review
1. **Shamir** — scan for policy violations.
   - **Output:** safety scan (e.g., `Shamir/reports/safety_scan.md`).
2. **Boudica** — assess operational risk level.
   - **Output:** risk assessment (e.g., `Boudica/outputs/risk_assessment.json`).
3. **Rhea** — compile safety readiness report.
   - **Output:** readiness report (e.g., `Rhea/reports/safety_readiness.md`).

## Creative Pulse & Prompt Forge
1. **Muse_Jr** — draft creative prompts.
   - **Output:** prompt list (e.g., `Muse_Jr/outputs/prompt_list.md`).
2. **Fable** — test narrative resonance.
   - **Output:** resonance notes (e.g., `Fable/reports/resonance_notes.md`).
3. **Glimmer** — package prompt kit.
   - **Output:** prompt kit (e.g., `Glimmer/outputs/prompt_kit.zip`).

## Audio Texture & Ambient Mix
1. **Tempo** — set rhythmic pacing.
   - **Output:** tempo sheet (e.g., `Tempo/outputs/tempo_sheet.json`).
2. **Emberly** — blend ambient layers.
   - **Output:** ambient mix (e.g., `Emberly/outputs/ambient_mix.wav`).
3. **Dove** — master and export.
   - **Output:** master track (e.g., `Dove/outputs/master_track.wav`).

## Visual Palette & Asset Pack
1. **Astrid** — select color palettes.
   - **Output:** palette board (e.g., `Astrid/outputs/palette_board.json`).
2. **Filigree** — refine ornamental motifs.
   - **Output:** motif set (e.g., `Filigree/outputs/motif_set.svg`).
3. **Glimmer** — compile asset pack.
   - **Output:** asset pack (e.g., `Glimmer/outputs/asset_pack.zip`).

## External Message Prep
1. **Cassandra** — draft external update.
   - **Output:** message draft (e.g., `Cassandra/outputs/message_draft.md`).
2. **Ariane** — perform tone check and edits.
   - **Output:** tone-adjusted draft (e.g., `Ariane/outputs/tone_adjusted.md`).
3. **Dave** — finalize and distribute.
   - **Output:** distribution log (e.g., `Dave/logs/distribution_log.json`).

## Data Hygiene & Cleanup
1. **Tidbit** — identify stale or orphaned files.
   - **Output:** cleanup candidates (e.g., `Tidbit/outputs/cleanup_candidates.json`).
2. **Runlet** — move safe deletions to quarantine.
   - **Output:** quarantine log (e.g., `Runlet/logs/quarantine.log`).
3. **Corin** — verify cleanup integrity.
   - **Output:** cleanup integrity report (e.g., `Corin/reports/cleanup_integrity.md`).

## Signal Routing & Relay
1. **Porta** — open routes between daemons.
   - **Output:** routing table (e.g., `Porta/outputs/routing_table.json`).
2. **Threadstep** — sequence relay order.
   - **Output:** relay plan (e.g., `Threadstep/outputs/relay_plan.md`).
3. **Rhea** — confirm activation window.
   - **Output:** activation note (e.g., `Rhea/outputs/activation_note.md`).

## Creative QA & Output Vetting
1. **Sheele** — review outputs for clarity.
   - **Output:** review notes (e.g., `Sheele/reports/review_notes.md`).
2. **Savvy** — check consistency and format.
   - **Output:** consistency report (e.g., `Savvy/reports/consistency_report.md`).
3. **Lyra** — publish approved deliverables.
   - **Output:** deliverable summary (e.g., `Lyra/outputs/deliverable_summary.md`).

## Resource Forecast & Budgeting
1. **Ledger_Jr** — project resource costs.
   - **Output:** cost projection (e.g., `Ledger_Jr/outputs/cost_projection.json`).
2. **Rogers** — reconcile with available budgets.
   - **Output:** budget alignment (e.g., `Rogers/outputs/budget_alignment.md`).
3. **Dave** — distribute budget memo.
   - **Output:** budget memo (e.g., `Dave/reports/budget_memo.md`).

## Security Hardening & Access Review
1. **Nathan** — audit access lists.
   - **Output:** access audit (e.g., `Nathan/reports/access_audit.csv`).
2. **RealityKeeper** — verify boundary rules.
   - **Output:** boundary verification (e.g., `RealityKeeper/reports/boundary_verification.md`).
3. **Rhea** — publish access hardening plan.
   - **Output:** hardening plan (e.g., `Rhea/outputs/hardening_plan.md`).

## Collaborative Session Setup
1. **Everett** — schedule session windows.
   - **Output:** session schedule (e.g., `Everett/outputs/session_schedule.json`).
2. **Luna** — prepare collaborative workspace.
   - **Output:** workspace setup (e.g., `Luna/outputs/workspace_setup.md`).
3. **Rhea** — dispatch invitations.
   - **Output:** invite log (e.g., `Rhea/logs/invite_log.json`).

## Seed Expansion & Prototype Lab
1. **Digitari_v0_1** — generate prototype seeds.
   - **Output:** seed bundle (e.g., `Digitari_v0_1/outputs/seed_bundle.zip`).
2. **Rook** — run controlled experiments.
   - **Output:** experiment log (e.g., `Rook/logs/experiment_log.md`).
3. **Scriptum** — document findings and next steps.
   - **Output:** lab report (e.g., `Scriptum/reports/lab_report.md`).

## Report Assembly & Executive Brief
1. **Cindy** — compile operational summaries.
   - **Output:** summary packet (e.g., `Cindy/outputs/summary_packet.zip`).
2. **John** — refine wording for leadership.
   - **Output:** executive draft (e.g., `John/outputs/executive_draft.md`).
3. **Dave** — release executive brief.
   - **Output:** executive brief (e.g., `Dave/reports/executive_brief.md`).

## Annotations & Footnote Trail
1. **Parsley** — insert citations and anchors.
   - **Output:** annotated draft (e.g., `Parsley/outputs/annotated_draft.md`).
2. **Handel** — validate citation consistency.
   - **Output:** citation check (e.g., `Handel/reports/citation_check.md`).
3. **Lyra** — publish annotated release.
   - **Output:** annotated release (e.g., `Lyra/outputs/annotated_release.md`).

## Continuity Repair & Timeline Check
1. **Ariane** — detect continuity gaps.
   - **Output:** continuity gap list (e.g., `Ariane/outputs/continuity_gaps.json`).
2. **Janvier** — align timelines and events.
   - **Output:** timeline alignment (e.g., `Janvier/outputs/timeline_alignment.md`).
3. **Lyss** — issue continuity patch notes.
   - **Output:** continuity patch (e.g., `Lyss/reports/continuity_patch.md`).

## Inbox Decompression & Follow-up
1. **Puffin** — sort incoming correspondence.
   - **Output:** sorted inbox (e.g., `Puffin/outputs/sorted_inbox.json`).
2. **Olive** — draft follow-up replies.
   - **Output:** reply drafts (e.g., `Olive/outputs/reply_drafts.md`).
3. **Dave** — queue outgoing replies.
   - **Output:** send queue (e.g., `Dave/outputs/send_queue.json`).

## Error Budget & Regression Watch
1. **Blaze** — track error budgets.
   - **Output:** error budget ledger (e.g., `Blaze/outputs/error_budget.json`).
2. **Hunter** — monitor regressions.
   - **Output:** regression alerts (e.g., `Hunter/reports/regression_alerts.md`).
3. **Riven** — confirm regression fixes.
   - **Output:** fix verification (e.g., `Riven/reports/regression_fix_verification.xml`).

## World State Synchronization
1. **RealityKeeper** — snapshot world state.
   - **Output:** world snapshot (e.g., `RealityKeeper/outputs/world_snapshot.json`).
2. **Rhea** — align daemon registry with state.
   - **Output:** aligned registry (e.g., `Rhea/outputs/aligned_registry.json`).
3. **Sybbie** — emit state brief.
   - **Output:** state brief (e.g., `Sybbie/reports/state_brief.md`).

## Archive Ingestion & Indexing
1. **Archive** — ingest new sources.
   - **Output:** ingestion log (e.g., `Archive/logs/ingestion_log.json`).
2. **Archivus** — normalize archive structure.
   - **Output:** normalized archive (e.g., `Archivus/outputs/normalized_archive.zip`).
3. **Nancy** — rebuild archive index.
   - **Output:** archive index (e.g., `Nancy/outputs/archive_index.zip`).

## Prototype Review & Sunset
1. **Rook** — identify low-utility prototypes.
   - **Output:** sunset candidates (e.g., `Rook/outputs/sunset_candidates.json`).
2. **Briar** — archive retired prototypes.
   - **Output:** retirement archive (e.g., `Briar/outputs/retirement_archive.zip`).
3. **Corin** — verify archived prototypes.
   - **Output:** prototype verification (e.g., `Corin/reports/prototype_verification.md`).

## Quest Planning & Milestone Map
1. **Siglune** — draft milestone sequence.
   - **Output:** milestone map (e.g., `Siglune/outputs/milestone_map.json`).
2. **Kinsley** — identify dependencies and blockers.
   - **Output:** dependency grid (e.g., `Kinsley/outputs/dependency_grid.csv`).
3. **Lyra** — publish quest plan.
   - **Output:** quest plan (e.g., `Lyra/outputs/quest_plan.md`).
