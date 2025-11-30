# Riven

Riven tends the fracture between systems. Five personas share the work:

- **Harper** watches load and backlog, warning when pressure spikes.
- **Maribel** ferries messages through the aether.
- **Glypha** forges sigils from words.
- **Tempo** taps the rhythm of mood.
- **Riven** herself mends broken CHAOS logs.

The roles live in a Python package so each can be invoked alone or through a
small command line interface.

## CLI

```bash
python -m riven check   # Harper
python -m riven deliver # Maribel
python -m riven forge "hope"  # Glypha
python -m riven pulse calm     # Tempo
python -m riven mend    # Riven
```

## Development

Tests use `pytest` and mock out filesystem state. From the repository root run:

```bash
pytest Riven/tests
```
