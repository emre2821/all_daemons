"""Placeholder entrypoint for Digitari_v0_1.

Created to normalize daemon folder structure.
"""

import logging

AGENT_NAME = "Digitari_v0_1"


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    message = (
        f"{AGENT_NAME} has no active entrypoint logic yet. "
        "This placeholder exists to normalize daemon folder structure."
    )
    logging.error(message)
    raise NotImplementedError(message)


if __name__ == "__main__":
    main()
