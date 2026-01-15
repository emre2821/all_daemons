# Contributing to All Daemons

Welcome, kindred spirit! ✨ Thank you for your interest in contributing to the All Daemons project. This repository is a living ecosystem of small agents, tools, and experiments for Paradigm Eden / Echolace.

## Getting Started

### Prerequisites

- Python 3.10 or later
- pip (Python package installer)

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/emre2821/all_daemons.git
   cd all_daemons
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest flake8  # Development dependencies
   ```

4. **Run tests to verify your setup:**
   ```bash
   pytest
   ```

## How to Contribute

### Reporting Issues

Found a bug or have a feature idea? Please [open an issue](https://github.com/emre2821/all_daemons/issues/new) with:
- A clear, descriptive title
- Steps to reproduce (for bugs)
- Expected behavior vs. actual behavior
- Any relevant error messages or screenshots

### Submitting Changes

1. **Fork the repository** and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Keep commits focused and atomic
   - Write clear, descriptive commit messages
   - Add tests for new functionality when possible

3. **Test your changes:**
   ```bash
   pytest              # Run tests
   flake8 . --exit-zero  # Check code style
   ```

4. **Submit a Pull Request:**
   - Fill out the PR template completely
   - Reference any related issues
   - Describe what changes you made and why

### Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code
- Use meaningful variable and function names
- Add docstrings to public functions and classes
- Keep functions focused and reasonably sized

### Working with Daemon Folders

Each daemon folder is mostly self-contained. When modifying a daemon:
- Preserve existing licensing/attribution within that folder
- Test your changes within that daemon's context
- Update any README files if behavior changes

## Preserving the Project's Voice

This project contains creative content (narrative files, lore, chaos-language elements) alongside technical code. When contributing:

### ✅ Do:
- Preserve original phrasing, metaphors, and emotional tone
- Add clarifying notes *around* creative content if needed
- Use comments or footnotes instead of rewrites for narrative text

### ❌ Don't:
- Edit the prose within narrative files
- Alter `.chaos`, `.chaosmeta`, or lore files
- Remove or modify stylized voice in creative content

**When in doubt:** Assume the file is narrative and preserve its voice.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all community members with respect and kindness.

## Questions?

If you have questions about contributing, feel free to:
- Open a discussion in the repository
- Leave a comment on the relevant issue

Thank you for helping make All Daemons better! 🌟
