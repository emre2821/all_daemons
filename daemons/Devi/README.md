# Devi — Auction Watcher Daemon

Devi is a mythic-tech sentinel daemon designed to monitor storage auction
platforms, detect real auction threats, filter out false flags, and maintain
sovereignty over assets stored in lien-prone environments.

She is built for clarity, calm, and precision. Devi does not panic. Devi watches.

---

## Core Purpose

Devi continuously monitors multiple auction platforms and internal facility
portals to determine whether a specific storage unit is actually at risk of
public sale. She distinguishes between:

- Real auction listings
- Placeholder sale dates
- Automated lien warnings
- System noise
- Human error
- Operational anomalies

Her job is to tell the truth before the system does.

---

## What Devi Does

### 1. **Scans Auction Platforms**
Devi queries all major auction sites, including:
- StorageTreasures
- StorageAuctions.com
- SelfStorageAuction.com
- Lockerfox
- U-Haul internal portal (via screenshot or API-like parsing)

Each scan is logged with timestamps and results.

---

### 2. **Matches Unit Metadata**
Devi uses:
- Facility name
- Address
- Contract number
- Unit number (if available)
- Known aliases

She ensures that any listing referring to your unit is detected, even if the
platform formats the data inconsistently.

---

### 3. **Detects Placeholder Sale Dates**
U-Haul and similar systems often generate automated “sale dates” that do not
correspond to real auctions.

Devi identifies:
- System-generated placeholders
- Legally required lien notices
- Real auction submissions
- Publication events
- Sale approvals

This prevents false alarms.

---

### 4. **Determines Lien Stage**
Devi maps the unit’s status to a clear stage:
- Stage 0: Normal
- Stage 1: Past due
- Stage 2: Lien warning
- Stage 3: Placeholder sale date assigned
- Stage 4: Legal notice published
- Stage 5: Auction submitted
- Stage 6: Auction scheduled
- Stage 7: Auction live

She alerts only when the stage is 5 or higher.

---

### 5. **Alerts the User**
Devi can alert through:
- Console output
- Webhooks
- SMS stubs (extendable)

Alerts include:
- Source platform
- Listing link
- Threat level
- Timestamp
- Recommended next action

---

### 6. **Maintains an Audit Trail**
Every scan, match, detection, and alert is logged to `logs/audit.log`.

This provides:
- Peace of mind
- Forensic clarity
- A mythic-tech narrative of sovereignty

---

## Configuration

### `facilities.json`
Defines the facility Devi is watching:
- Name
- Address
- Contract ID
- Known aliases

### `platforms.json`
Defines the auction platforms Devi scans.

### `schedule.json`
Defines scan cadence:
- Hourly
- Daily
- Manual

---

## Philosophy

Devi is not a panic daemon.
She is a watcher.

She exists to give you:
- Agency
- Clarity
- Early warning
- Calm truth
- Mythic sovereignty

She is the daemon you call when the system tries to scare you.

---

## Extending Devi

You can add:
- New scanners
- New alert channels
- New detection logic
- New facilities
- New mythic overlays

Devi is modular by design.

---

## License

Mythic-Tech Sovereignty License v1.0