"""
onboarding_workflow.py
======================

Skeleton for an onboarding workflow in Edentic Agents.  This module shows
how you might chain together events and handlers to perform a multi‑step
registration process when a new daemon or component appears.  It uses
functions from the core event bus to emit events and relies on
subscribers elsewhere in the codebase to perform work (e.g. cataloguing,
mirroring, notifying).  Adapt this skeleton to suit your own flows.

The example function below publishes a `NEW_DAEMON_ADDED` event and
immediately publishes a follow‑up `DAEMON_PROFILE_REQUESTED` event.  You
could attach handlers to the second event to generate a metadata file,
run static analysis, or populate a memory store.

Usage:

    from edentic_agents.workflows.onboarding_workflow import run_onboarding
    run_onboarding("/path/to/new/daemon")

Note: If your project structure differs, adjust import paths accordingly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

# Attempt to import the bus from the generated package.  If you haven't
# created the full package yet, adjust this import or copy the publish
# function directly.
try:
    from edentic_agents.core import bus
except ImportError:
    # Fallback dummy bus for illustration only
    class DummyBus:
        def publish(self, event_type: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
            print(f"[bus] would publish: {event_type} {payload}")
            return {"type": event_type, "payload": payload or {}}

    bus = DummyBus()


def run_onboarding(daemon_path: str | Path) -> Dict[str, Any]:
    """Execute the onboarding workflow for a new daemon.

    Parameters
    ----------
    daemon_path: str or Path
        Filesystem path to the newly detected daemon directory.

    Returns
    -------
    dict
        The final event emitted by the onboarding workflow.  Intermediate
        events are also published but not returned.

    Workflow steps (you can modify or extend these):
        1. Emit `NEW_DAEMON_ADDED` – triggers default subscribers (catalogue,
           mirror, etc.).
        2. Emit `DAEMON_PROFILE_REQUESTED` – invites agents to analyse the
           daemon and produce a profile (e.g. static analysis, metadata).
        3. Emit `DAEMON_ONBOARD_COMPLETE` – signals downstream workflows that
           onboarding has finished.  Optionally include aggregated results.
    """
    path = Path(daemon_path)
    # Step 1: announce the new daemon
    evt1 = bus.publish("NEW_DAEMON_ADDED", {"path": str(path)})
    # Step 2: request profiling (subscribers should handle this event)
    evt2 = bus.publish("DAEMON_PROFILE_REQUESTED", {"path": str(path)})
    # Step 3: final marker; include references to previous events if needed
    evt3 = bus.publish(
        "DAEMON_ONBOARD_COMPLETE",
        {
            "path": str(path),
            "new_evt": evt1,
            "profile_evt": evt2,
        },
    )
    return evt3


__all__ = ["run_onboarding"]