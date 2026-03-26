---
name: bulk-ip-upload
description: Guides bulk IP range import or update for a single organization from diverse inputs (paste, Word, Excel, CSV). Resolves organization name to Party.partyId in the DB, builds a five-column Excel keyed by party id (not NSTL serial id), runs BulkPartyLoadIPCheck, overlap filter, batch expire, and BulkPartyLoadIPRange. Requires user approval before destructive steps. Use when the user mentions bulk IP upload for one org, single institution IP update, lookup by institution name, paste IP list, doc/spreadsheet IP import, or non-NSTL bulk IP for one party.
---

# Bulk IP upload (single organization)

Use this skill when the user needs to **add or replace many IP ranges for one Party**, identified by **`partyId`** (primary key). The workflow uses **`BulkPartyLoadIPCheck.py`**, **`filter_bulk_party_ip_check_error_overlap_only.py`**, **`batch_expire_ip_ranges_from_excel.py`**, and **`BulkPartyLoadIPRange.py`**. It **does not** use **`NSTLLoadInsCheck.py`**, **`NSTLLoadIPCheck.py`**, **`NSTLLoadIPRange.py`**, or **`bulk_ip_load_pipeline.py`** (those are the NSTL / serial-id path).

## Analysis and approval (required)

Same rules as [bulk-nstl-ip-load](../bulk-nstl-ip-load/SKILL.md): **do not run DB-writing scripts** until the user approves each step. Prefer **`--dry-run`** for batch expire, then separate approval before apply.

## Scope

- **Single organization:** one Party on every row—**one `partyId`** once resolved.
- **Resolve `partyId` first:** From the **organization name**, locate the Party in the database. Use **`scripts/lookup_party_id_by_name.py`** (read-only) or a Django shell query on **`Party.name`** (normalize case/whitespace; if multiple rows match, disambiguate with the user). **Do not run `NSTLLoadInsCheck`.**
- **Canonical Excel columns (A–E):** **`party id`** | **`cn name`** | **`en name`** | **`start ip`** | **`end ip`**
  - **`party id`:** integer **`Party.partyId`**. Watch Excel float coercion (e.g. `354790.0`); the scripts normalize with **`normalize_excel_party_id`** in `common/party_ip_row_check.py`.
  - **`en name`:** use **`Party.name`** from the resolved row (or the agreed spelling). **`cn name`:** empty or a Chinese name only if you have a reliable source—**do not invent** one.

## Container and database

Run Django scripts in the **same environment** as production/staging DB (e.g. Docker Compose service). Paths must be readable inside the container. The **overlap filter** is Python 3 + **openpyxl** only—host `python3` or one-off `python:3.x-slim` Docker from project root (see **bulk-nstl-ip-load** skill for Docker patterns).

## Step 0 — Organization name + canonical Excel

**Goal:** Confirm **`partyId`**, then produce one `.xls` or `.xlsx` with headers exactly:

**party id** | **cn name** | **en name** | **start ip** | **end ip**

1. **Identify the organization name** from the user or source material.
2. **Resolve `partyId`:** e.g. `python scripts/lookup_party_id_by_name.py "Some University"` or `python scripts/lookup_party_id_by_name.py --exact "Full Name"`.
3. **start ip / end ip:** IPv4; single IP = same value in start and end.
4. **Sources:** **Paste:** `1.2.3.4`, `1.2.3.4 - 1.2.3.10`, `1.2.3.0/24` (expand CIDR to start/end). **Word / .docx:** extract tables or lines. **Excel / CSV:** map columns; duplicate **`party id`** and name fields on each row.
5. Save under a path the runtime can read (mounted volume for Docker). **Avoid committing** working files to git.

If the Party **does not exist** yet, create it per team process (e.g. **`NSTLCreateIns.py`** or admin workflow), then **look up the new `partyId`** and continue.

## Step 1 — IP check + overlap-only file

```bash
python scripts/BulkPartyLoadIPCheck.py <path_to_canonical.xlsx>
```

Produces **`bulk_party_ip_to_load.xlsx`** and **`bulk_party_ip_check_error.xlsx`** (written to the **current working directory**, like other load scripts—run from project root or move outputs as needed).

Overlap filter (Python 3 + openpyxl):

```bash
python3 scripts/filter_bulk_party_ip_check_error_overlap_only.py
```

Or pass explicit paths:

```bash
python3 scripts/filter_bulk_party_ip_check_error_overlap_only.py \
  --input bulk_party_ip_check_error.xlsx \
  --output bulk_party_ip_check_error_overlap_only.xlsx
```

**This step does not modify the DB.** Error semantics mirror NSTL-style checks (size, private, overlap, containment)—see **Error types** in [bulk-nstl-ip-load](../bulk-nstl-ip-load/SKILL.md) for interpretation.

## Step 2 — Review

Focus on **`bulk_party_ip_check_error_overlap_only.xlsx`** for overlap/containment decisions. Use the full **`bulk_party_ip_check_error.xlsx`** for validation errors (`too large`, `private`, `invalid`, `party id not found`).

Build or confirm **`ip range id`** values to expire before load (from error rows), if applicable.

## Step 3 — Batch expire (optional)

```bash
python scripts/batch_expire_ip_ranges_from_excel.py <expire_list.xlsx> --dry-run
```

Excel: column **`ip range id`** (or `ipRangeId` / `ip_range_id`). After approval, run without `--dry-run`.

## Step 4 — Load IP ranges

After overlaps are resolved:

```bash
python scripts/BulkPartyLoadIPRange.py bulk_party_ip_to_load.xlsx
```

This **writes** `IpRange` rows for the existing **`Party`** referenced by **`party id`**; it does **not** create new Party rows.

## Step 5 — Cleanup (reminder)

After the user confirms DB results, **delete** working copies: canonical input, **`bulk_party_*.xlsx`**, expire lists, and temp files—avoid leaving institution/IP data in the repo.

## Relationship to NSTL skill

- **bulk-nstl-ip-load:** multi-institution Excel, **serial id** column, **`NSTLLoadInsCheck`** / **`NSTLLoadIPCheck`** / **`NSTLLoadIPRange`**.
- **bulk-ip-upload:** **one org**, **`party id`** column, **`BulkPartyLoadIPCheck`** / **`BulkPartyLoadIPRange`**, **no** `NSTLLoadInsCheck`, **no** NSTL IP check/load scripts.

For Docker examples and detailed **error-type** notes, see [bulk-nstl-ip-load/SKILL.md](../bulk-nstl-ip-load/SKILL.md) or [reference.md](../bulk-nstl-ip-load/reference.md) when present.
