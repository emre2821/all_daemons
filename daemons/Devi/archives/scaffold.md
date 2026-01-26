devi/
├── README.md
├── devi.py
├── config/
│   ├── facilities.json
│   ├── platforms.json
│   └── schedule.json
├── scanners/
│   ├── base_scanner.py
│   ├── storagetreasures_scanner.py
│   ├── storageauctions_scanner.py
│   ├── selfstorageauction_scanner.py
│   └── uhaul_portal_scanner.py
├── matchers/
│   ├── unit_matcher.py
│   └── facility_matcher.py
├── detectors/
│   ├── placeholder_detector.py
│   ├── lien_stage_detector.py
│   └── anomaly_detector.py
├── alerts/
│   ├── alert_manager.py
│   └── channels/
│       ├── console.py
│       ├── webhook.py
│       └── sms_stub.py
└── logs/
    └── audit.log