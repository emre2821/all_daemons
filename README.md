# All Daemons

This repository gathers many small agents, tools, and experiment folders for Paradigm Eden / Echolace. Each directory functions mostly on its own, containing code, data, or assets for a specific daemon or prototype.

## Getting started

- Inspect a folder to learn its focus. Most contain self-contained scripts or canvases.
- Use Python 3.12 or later for any scripts. Some projects may have additional dependencies.
- Run `pytest` from the repository root to execute available tests (many subprojects currently have none).

## Create a downloadable snapshot

If you need an archive of the current repository state, generate it locally with Git. From the repository root run:

```bash
git archive --format=zip --output=all_daemons.zip HEAD
```

The resulting `all_daemons.zip` contains the tracked files for the latest commit without requiring binary archives to be stored in version control.

## Contributing

- Keep commits focused and describe the intent in the message.
- Add tests or examples when adding new functionality.
- Preserve existing licensing or attribution within each subproject.
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Disclaimer

The repository is heterogeneous and experimental. Expect varying levels of completeness and documentation across subdirectories.

## License

This project is licensed under the [MIT License](LICENSE).
