""" Devi — Auction Watcher Daemon Core orchestrator.

Devi watches. She does not panic. """

from datetime import datetime
from typing import List, Dict, Any
from config import facilities, platforms, schedule  # type: ignore from scanners.base_scanner import BaseScanner from matchers.unit_matcher import match_unit from detectors.placeholder_detector import is_placeholder from detectors.lien_stage_detector import determine_lien_stage from alerts.alert_manager import AlertManager

AUDIT_LOG_PATH = "logs/audit.log"
ALERT_STAGE_THRESHOLD = 5  # alert only at Stage 5+

class Devi:
    def init(self, scanners: List[BaseScanner], alert_manager: AlertManager):
        self.scanners = scanners
        self.alerts = alert_manager

# ---- Core Loop ----
def run_scan(self) -> None:
    timestamp = datetime.utcnow().isoformat()
    self._audit(f"SCAN_START {timestamp}")

    for scanner in self.scanners:
        try:
            results = scanner.scan()
            self._audit(f"SCAN_OK {scanner.name} results={len(results)}")
            self._process_results(scanner.name, results)
        except Exception as e:
            self._audit(f"SCAN_FAIL {scanner.name} error={e}")

    self._audit(f"SCAN_END {datetime.utcnow().isoformat()}")

# ---- Processing ----
def _process_results(self, source: str, results: List[Dict[str, Any]]) -> None:
    for listing in results:
        matched = match_unit(listing, facilities.ALL)
        if not matched:
            self._audit(f"NO_MATCH source={source} listing_id={listing.get('id')}")
            continue

        if is_placeholder(listing):
            self._audit(f"PLACEHOLDER source={source} unit={matched.unit_id}")
            continue

        stage = determine_lien_stage(listing)
        self._audit(
            f"STAGE source={source} unit={matched.unit_id} stage={stage}"
        )

        if stage >= ALERT_STAGE_THRESHOLD:
            self._alert(source, matched, listing, stage)

# ---- Alerts ----
def _alert(self, source: str, matched, listing: Dict[str, Any], stage: int) -> None:
    payload = {
        "source": source,
        "unit": matched.unit_id,
        "facility": matched.facility_name,
        "stage": stage,
        "listing": listing,
        "timestamp": datetime.utcnow().isoformat(),
    }
    self.alerts.send(payload)
    self._audit(f"ALERT_SENT unit={matched.unit_id} stage={stage}")

# ---- Audit ----
def _audit(self, line: str) -> None:
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{line}\n")

# ---- Entry Helper ----

def build_and_run(): scanners = platforms.build_scanners()  # factory
    returns BaseScanner,
    list alert_manager = AlertManager(),
    devi = Devi(scanners=scanners,
    alert_manager=alert_manager),
    devi.run_scan()

if name == "main": build_and_run()
