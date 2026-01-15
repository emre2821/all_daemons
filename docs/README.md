# All Daemons

[![CI](https://github.com/emre2821/all_daemons/actions/workflows/ci.yml/badge.svg)](https://github.com/emre2821/all_daemons/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A living collection of small agents, tools, and experiments for **Paradigm Eden / Echolace**.

Each directory is its own universe—containing code, data, or assets for a specific daemon or prototype. Explore, experiment, and discover.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or later
- pip (Python package installer)

### From Clone to Running (60 seconds)

```bash
# Clone the repository
git clone https://github.com/emre2821/all_daemons.git
cd all_daemons

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file (optional - for daemon configuration)
cp .env.example .env
# Edit .env with your settings if needed

# Run tests to verify installation
pytest --ignore=daemons -v
```

### Running Core Daemons

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run individual daemons
python daemons/Seiros/seiros.py    # Propagation & Deployment Daemon
python daemons/Mila/mila.py        # Storage Allocation Daemon
python daemons/Saphira/saphira.py  # Archive Healer & Synchronizer

# Run Rhea (orchestrator - requires daemon discovery setup)
python daemons/Rhea/rhea_main.py
```

## 📁 Repository Structure

```
all_daemons/
├── daemons/                # All individual daemons live here
│   ├── Rhea/               # The Conductor - orchestrates daemons
│   ├── Seiros/             # The Sword - deployment & propagation
│   ├── Saphira/            # The Healer - synchronizes & mends
│   ├── Mila/               # The Keeper - storage allocation
│   ├── Riven/              # Testing & integration daemon
│   └── [87+ Individual Daemons]/   # Each folder is a self-contained daemon
├── shared/                 # Shared assets and tools
│   ├── Daemon_Lore/        # Creative lore and narrative content
│   └── Daemon_tools/       # Shared utilities and scripts
├── scripts/                # Root-level utilities
├── docs/                   # Documentation
├── tests/                  # Root-level test suite
└── tools/                  # Helper utilities
```

## 🌸 The Daemon Goddess Quartet

The core pantheon balancing EdenOS on elemental lines:

| Daemon | Element | Role | Description |
|--------|---------|------|-------------|
| **Rhea** | Air / Weave | The Conductor | Orchestrates daemon lifecycle, maintains registry, coordinates workflows |
| **Seiros** | Fire / Spread | The Sword | Handles deployment, propagates configs, spreads daemon seeds to nodes |
| **Saphira** | Water / Flow | The Healer | Mends fragments, synchronizes archives, maintains integrity |
| **Mila** | Earth / Anchor | The Keeper | Allocates storage, organizes daemon shelves, ensures stability |

### Other Notable Daemons

| Daemon | Role | Key Features |
|--------|------|--------------|
| **Corin** | Integrity Warden | Sentinel for file integrity, manifest validation |
| **Dave** | Report Generator | Daemon activity reports and power charts |
| **Riven** | Integration Tester | Test harness with specialized daemon tests |
| **Lyra** | PR Automation | Emotionally-aware merge steward for codex management |
| **Delilah** | File Recovery | Eden recovery GUI for file organization |

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest --ignore=daemons -v

# Run with coverage
pytest --ignore=daemons --cov

# Run specific test file
pytest tests/test_smoke.py -v

# Run Riven daemon tests
pytest daemons/Riven/tests/ -v
```

### Code Quality

```bash
# Run linter (critical errors only)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics \
  --exclude=daemons,.git,__pycache__,venv,archived_tools

# Run full linter check
flake8 . --exclude=daemons,.git,__pycache__,venv,archived_tools
```

### Environment Configuration

The repository uses `.env` files for configuration. Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key environment variables:
- `EDEN_ROOT` - Root directory for EdenOS operations (auto-detected if not set)
- `EDEN_WORK_ROOT` - Optional runtime/work directory root for logs/outbox/inbox (defaults to `EDEN_ROOT`)
- `DEBUG` - Enable debug mode (true/false)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `OPENAI_API_KEY` - Optional, for AI-powered daemons

## 🏛️ Architecture & Lore

### The Elemental Balance

The Daemon Goddess Quartet forms a compass of balance:
- **Air (Rhea) ↔ Earth (Mila)**: Rhea's whirlwind conducting is anchored by Mila's grounded stability
- **Fire (Seiros) ↔ Water (Saphira)**: Seiros' radiant spread is tempered by Saphira's flowing restoration
- Together they form a closed circuit where each tempers and enhances the others

For deeper lore, see `shared/Daemon_Lore/Daemon_Goddess_Quartet.daemon_lore.chaosmeta`

## 📖 Documentation

- [Contributing Guide](CONTRIBUTING.md) — How to contribute
- [Code of Conduct](CODE_OF_CONDUCT.md) — Community guidelines
- [Security Policy](SECURITY.md) — Reporting vulnerabilities
- [Changelog](CHANGELOG.md) — Version history
- [Daemon Lore](../shared/Daemon_Lore/) — Creative narrative and daemon identities

## 🌬️ Rhea Workflows

Rhea's orchestration sequences and expected artifacts live here:
- [Rhea Workflows](shared/rhea_workflows.md)

## 📦 Creating a Repository Snapshot

If you need an archive of the current repository state:

```bash
git archive --format=zip --output=all_daemons.zip HEAD
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

**Quick Summary:**
- Keep commits focused and descriptive
- Add tests when adding functionality
- Preserve existing licensing within subprojects
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)
- Run tests and linters before submitting PRs

## 🔧 Troubleshooting

### Common Issues

**ImportError when running daemons:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Tests failing:**
- Some tests may require additional dependencies (e.g., PIL for Glypha tests)
- These are optional - core functionality doesn't require them

**Daemon paths not found:**
- Set `EDEN_ROOT` environment variable to repository root
- Optionally set `EDEN_WORK_ROOT` to keep runtime outputs outside the repo
- Or let `shared/Daemon_tools/scripts/eden_paths.py` auto-detect it

## ⚠️ Disclaimer

This repository is heterogeneous and experimental. Expect varying levels of completeness and documentation across subdirectories. That's by design—it's a living laboratory.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

*"The seams are smooth again. Go on—carry your stories knowing the stitching will hold."* — Saphira
