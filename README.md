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

# Run tests
pytest
```

## 📁 Repository Structure

```
all_daemons/
├── 01_Daemon_Core_Agents/  # Core daemon implementations
├── Daemon_Lore/            # Creative lore and narrative content
├── Daemon_tools/           # Shared utilities and scripts
├── Digitari_v0_1/          # Digitari species schema and runtime
├── Riven/                  # Riven daemon with tests
├── tests/                  # Root-level test suite
├── tools/                  # Helper utilities
└── [Individual Daemons]/   # Each folder is a self-contained daemon
```

### Notable Daemons

| Daemon | Description |
|--------|-------------|
| **Rhea** | The Conductor — orchestrates and catalogs daemons |
| **Saphira** | The Healer — mends and synchronizes |
| **Riven** | Testing & integration daemon |
| **Digitari** | A minimal viable species schema |

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_smoke.py
```

### Code Quality

```bash
# Run linter
flake8 . --exit-zero
```

## 📖 Documentation

- [Contributing Guide](CONTRIBUTING.md) — How to contribute
- [Code of Conduct](CODE_OF_CONDUCT.md) — Community guidelines
- [Security Policy](SECURITY.md) — Reporting vulnerabilities
- [Changelog](CHANGELOG.md) — Version history

## 📦 Create a Snapshot

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

## ⚠️ Disclaimer

This repository is heterogeneous and experimental. Expect varying levels of completeness and documentation across subdirectories. That's by design—it's a living laboratory.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
