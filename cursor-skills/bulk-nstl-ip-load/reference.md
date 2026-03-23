# Bulk NSTL IP load – reference

Summary of the bulk IP load process. For full official steps, refer to https://phoenixbioinformatics.atlassian.net/wiki/spaces/TEC/pages/42369691/NSTL+IP+update

The initial Excel file can be provided on the fly: any path and any filename are accepted by all scripts and the pipeline (no fixed location or naming required).

**Approval workflow:** At every step, the agent must analyze what would change, give a brief report, and get your approval before running the script. No step runs until you confirm.

**Container and DB:** If you use Docker/Compose and a database, the agent should run analysis and the workflow scripts inside the container so reports use real DB data and scripts write to your DB. The Excel file must be reachable inside the container (e.g. via volume mount or copy into the project).

## Column meanings

| Column    | Description                    |
|----------|--------------------------------|
| serial id| Institution identifier         |
| cn name  | Chinese name                   |
| en name  | English name (used in DB)       |
| start ip | Range start (IPv4)             |
| end ip   | Range end (IPv4)               |

## Resolving errors

After `NSTLLoadIPCheck`, run the overlap filter ( **`scripts/filter_nstl_ip_check_error_overlap_only.py`** ). It is **Python 3**, **openpyxl** only — **no Django / DB / app code**; correct to run outside the application container.

- **Host:** `python3 -m pip install openpyxl` then `python3 scripts/filter_nstl_ip_check_error_overlap_only.py` (from project root).
- **No `python3` on host:** from project root, one-off container:  
  `docker run --rm -v "$PWD:/work" -w /work python:3.11-slim-bookworm bash -lc "pip install --no-cache-dir -q openpyxl && python scripts/filter_nstl_ip_check_error_overlap_only.py"`

Review **`NSTL_all_ip_check_error_overlap_only.xlsx`** for decisions; the full **`NSTL_all_ip_check_error.xlsx`** still holds exact matches (`ip range exists`) and validation errors.

- **Exists (exact match):** Stripped from the overlap-only file—no review needed; no load needed.
- **Contained, same institution:** The checker writes two rows; if both `serial id` values match, the overlap filter drops them (subset of your own range—skip like identical). **Contained, different institution:** Kept in the overlap-only file.
- **Overlap same institution:** Often resolve by expiring the older range and loading the new one.
- **Overlap different institution:** Requires manual decision (contact or process doc).

## Pipeline

**Python 2 (app container)** runs `NSTLLoadInsCheck`, `NSTLLoadIPCheck`, and (with `--load`) `NSTLLoadIPRange` via **`bulk_ip_load_pipeline.py`**.

**Overlap filter (Python 3, no app deps):** After the two check scripts, `bulk_ip_load_pipeline.py` runs `filter_nstl_ip_check_error_overlap_only.py` using:

1. **`python3`** on `PATH` if found, else  
2. **`docker run`** with **`python:3.11-slim-bookworm`** (override with env **`NSTL_PY3_FILTER_IMAGE`**) mounting the project at `/work`.

Use **`--no-docker-filter`** if you must not invoke Docker (then run the filter manually on a machine with Python 3). Requires network on first run (pip + optional image pull).

**Docker-from-inside-app-container:** If you invoke `bulk_ip_load_pipeline.py` *inside* the Paywall container, the embedded `docker run -v …` step only works when the Docker CLI can reach the daemon and volume paths resolve correctly (often: socket mounted + same bind-mount layout). If that fails, run the **standalone** `docker run -v "$PWD:/work" … filter` command from the **host** after the check step, with `$PWD` as the project root on the host.

Use `--load` to also run NSTLLoadIPRange on the generated "to load" file after checks pass. It does **not** run **batch expire**; expire is a separate step (**usually after review, before load**—see SKILL workflow Steps 5–6).

## Batch expire by Excel

Script: **`scripts/batch_expire_ip_ranges_from_excel.py`** (Python 2 / Django stack used elsewhere).

- **Typical order:** After reviewing overlap output, **expire** conflicting old ranges (**Step 5**), then **load** new ranges from `NSTL_all_ip_to_load.xlsx` (**Step 6**).
- Spreadsheet must include a column **`ip range id`** (or `ipRangeId` / `ip_range_id`) with numeric `IpRange` primary keys—e.g. second line of each pair in `NSTL_all_ip_check_error.xlsx`, or ids from the checker’s “IP ranges need to expire” list.
- Use **`--dry-run`** to print how many rows would be expired vs missing / already expired; run without `--dry-run` only after approval.
- Sets **`expiredAt`** to the current time; does not delete ranges. Run inside the same container/DB as the NSTL load.

## Cleanup after success

Once results are **confirmed** in the DB, delete working Excel artifacts (`NSTL_*.xlsx`, custom expire lists, copies like `_nstl_work.xls`, and any `~$*.xlsx` lock files) from the project tree so sensitive data is not left around or committed. Keep archives outside the repo if retention is required.
