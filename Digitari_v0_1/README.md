# Digitari v0.1 - Minimal Viable Species

**What's here**

- JSON Schema for Digitari
- Two .vas canvases: `Digitari.seed.vas` and `TruthAnchor.vas`
- Tiny runtime hooks: refusal / audit / reinterpret
- Example citizen: `Lumen-Seed`
- Facts cache for auditing
- Eden agent profile + custom palettes (Mentor-Fox)

**Quick start**

1) Read `canvases/Digitari.seed.vas`
2) Inspect `data/digitari/example_digitari.json`
3) Wire `runtime/engine.py` into your task runner (call `should_refuse`, `audit`, `reinterpret`)
4) Expand `data/facts/cache.json` with your truths
5) Spawn more citizens by copying the example and changing `kernel.name` & `id`

**Notes**

- Consent default is private. Refusal is considered healthy when budgets/values demand it.
- TruthAnchor is tiny on purpose—extend it to your liking.
