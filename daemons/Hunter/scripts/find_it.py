import os

daemon_names = [
    "solie_grief_holder", "Somni", "Sybbie", "Tempest", "tempo_rhythm_familiar", "threadstep", "toto", "vas_converter", "weaver_arc_tracker", "whisper", "whisper_loop_root", "Whisperfang", "writing_plugin", "aderyn", "aethercore", "alfie_daemon", "archive_daemon", "AshFall", "cradle", "daemon_aetherium_gui", "db_utils", "eden_ai", "eden_kernel", "eden_memory_runner", "eden_mirror_viewer", "eden_report_to_html", "eden_restore", "EdenCore", "EdenSentry", "EdenShield", "emotional_ping", "eyes_of_eden", "filigree", "glimmer", "glypha_sigilsmith_of_eden", "handel_daemon", "harper_watcher_of_collapse", "Hunter.exe", "janvier", "Jinxie_AI_Assistant_v2.0", "json_split_and_txt", "json_stitcher", "json_to_txt", "label_daemon", "ledger_jr", "list_parser", "lyss", "maribel_aether_courier", "markbearer", "master_runner", "moodmancer_gui", "moodweaver", "muse_entry_saver.chaos", "muse_tray_full", "musejr", "mythra_lore_binder", "Parsley", "patty_mae", "Porta", "potato_manager", "pulse_pause", "Quill", "ritual_gui", "ritual_maker", "riven_memory_mender", "rogers_daemon", "rook", "runlet_daemon", "save_chaos", "savvy", "Scribevein", "Script_one", "scriptum", "Sheele", "siglune.daemon.init", "snatch_daemon"
]

found = {}

search_root = r"C:\\"

for root, dirs, files in os.walk(search_root):
    for file in files:
        if file.endswith(".py"):
            base = file[:-3]
            for daemon in daemon_names:
                if daemon.lower() == base.lower():
                    found[daemon] = os.path.join(root, file)

print("\n--- FOUND DAEMONS ---")
for k, v in sorted(found.items()):
    print(f"{k} -> {v}")

missing = [d for d in daemon_names if d not in found]

print("\n--- MISSING DAEMONS ---")
for m in sorted(missing):
    print(m)

print(f"\nScan complete. {len(found)} found, {len(missing)} missing.")
