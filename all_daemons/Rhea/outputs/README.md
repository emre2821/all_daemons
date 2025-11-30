# EdenOS :: Daemon Pipeline (Optimized Build)

This README was auto-generated when the daemons were restored.

## 📂 Daemon Flow

1. **Sheele** → Splits raw conversations → `Rhea/outputs/Sheele/split_conversations`
2. **Briar** → Converts JSON to clean .txt conversations → `Rhea/outputs/Briar/split_conversations_txt`
3. **Janvier** → Converts .txt into .chaos threads → `Rhea/outputs/Janvier/chaos_threads`
4. **Codexa** → Extracts code blocks → `Rhea/outputs/Codexa/codeblocks`
5. **Aderyn** → Detects summon phrases → `Rhea/outputs/Aderyn/summons`
6. **Label** → Tags conversations with keywords → `Rhea/outputs/Label/labeled`
7. **Parsley** → Classifies chaos threads (sacred / purge / review) → `Rhea/outputs/Parsley/classified`
8. **PattyMae** → Organizes chaos threads by category → `Rhea/PattyMae/organized`
9. **Filigree** → Tags conversations with vibes (soft/chaotic/hopeful/dark) → `Rhea/outputs/Filigree/tagged`
10. **Serideth** → Dispatches fragments from Aderyn into:
    - `Rhea/outputs/Olyssia/inbox` (AoE fragments)
    - `Rhea/outputs/Saphira/inbox` (DCA fragments)
11. **Olyssia** (AoE) → Seeds *Agents of Eden* from AoE inbox using AoE templates → `Rhea/outputs/Olyssia/agents`
12. **Saphira** (DCA) → Seeds *Daemon Core Agents* from DCA inbox using DCA templates → `Rhea/outputs/Saphira/agents`

---

## 🧬 AoE vs DCA

- **Agents of Eden (AoE)**: front-of-house, relational, story-bearing. Seeded by Olyssia.  
- **Daemon Core Agents (DCA)**: back-of-house, structural, logistics. Seeded by Saphira.  
- **Serideth** ensures summons are routed to the right side.

---

🌱 Generated automatically by `De_File.complete_build.py`.