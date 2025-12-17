"""CLI wrapper that delegates to :mod:`Porta.porta`.

Keeping this script minimal avoids duplicating Porta's core logic. It simply
imports the main module and executes its entrypoint.
"""

from Porta import porta


def main():
    porta.main()


if __name__ == "__main__":
    main()
