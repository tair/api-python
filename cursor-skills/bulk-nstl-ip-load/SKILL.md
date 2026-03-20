---
name: bulk-nstl-ip-load
description: Guides bulk IP range import from Excel (NSTL-style) and optional batch expire of IpRange ids from an Excel column. Accepts Excel path on the fly. Requires analysis and user approval before each destructive step. Use when the user mentions bulk IP load, NSTL, Excel IP import, IP range update, batch expire IPs, institution IP, or loading/updating IP ranges from a spreadsheet.
---

# Bulk NSTL IP Load (NSTL workflow)

Use this skill when the user needs to import or update IP ranges in bulk from an Excel file (e.g. NSTL IP updates).

## Analysis and approval (required)

**Do not run any script until the user has approved the step.**

At **every** step:

1. **Analyze** what would change: inspect the Excel (or the output from the previous step), and optionally query or reason about the current state (e.g. which institutions exist, which IP ranges would be added). Determine what the script would create, update, or write.
2. **Report briefly** to the user: summarize what is about to happen (e.g. "Step 1 would create 3 new Party records and link them to consortium 31772: [names]. No existing data would be modified." or "Step 3 would produce `NSTL_all_ip_to_load.xlsx`, the full `NSTL_all_ip_check_error.xlsx`, and after filtering, `NSTL_all_ip_check_error_overlap_only.xlsx` with only non-identical overlap rows for your review.").
3. **Get explicit approval** (e.g. "Proceed?", "Run this step?", "Yes/No"). Wait for the user to confirm.
4. **Only then** run the script for that step.

If the user has not approved, do not execute. If they ask to skip approval for a step, you may proceed only after they confirm. Prefer one step at a time unless the user explicitly asks to run multiple steps or the full pipeline after a single approval.

## Container and database

When the user has a **container and database connection** (e.g. Docker Compose):

- **Use the container for analysis:** Run analysis inside the container so you can query the DB and read the Excel (Django ORM, pandas). For example, run a short Python one-liner or script via `docker-compose run <service> python ...` to compare the Excel with existing Party/IpRange data and produce accurate counts (e.g. "X new Parties", "Y rows to load", "Z conflicts").
- **Run the workflow scripts in the same environment:** Execute each step (NSTLCreateIns, NSTLLoadInsCheck, etc.) inside the container so they use the same DB. Example: `docker-compose run <service> python /var/www/api-python/scripts/NSTLCreateIns.py <path_to_excel>` (adjust service name and in-container path per project).
- **Overlap filter (Step 3):** The app image may be **Python 2 only**. The filter script needs **Python 3 + openpyxl** but has **no application dependencies**—run it on the **host** or via **`docker run` with `python:3.x-slim`** mounting the project (see Step 3 commands). `bulk_ip_load_pipeline.py` will use local `python3` if present, otherwise try the same one-off container when `docker` is available.
- **Excel path:** The file path must be reachable from inside the container. If the Excel is on the host (e.g. `~/Downloads/file.xls`), ensure the project mounts that directory or copy the file into a mounted volume so the container can read it; then pass the in-container path to the script.

This way the pre-step reports can be accurate and the scripts run against the real database.

## Providing the Excel file

**The initial Excel can be supplied on the fly** — no fixed location or naming convention required.

- The user may provide the path when they ask (e.g. "run bulk NSTL IP load with ~/Downloads/NSTL-IP-2024.xlsx" or by pasting/dragging a path).
- Path can be **anywhere** on the filesystem: `~/Downloads/...`, Desktop, a shared drive, or inside the project.
- **Any filename** is fine (e.g. `TEC-NSTL-IP-update.xlsx`, `my-ip-list.xlsx`). Scripts take the path as the first argument.
- Run all commands from the **project root**; use the exact path the user provided (absolute or relative).

When the user mentions an Excel file without a path, ask for the path or confirm the file they mean before running the pipeline or individual scripts.

## When to use

- User has an Excel file with institution IP ranges to load or update.
- User mentions NSTL, bulk IP load, IP range import, or updating institution IPs from a spreadsheet.
- User asks how to run the IP check or load scripts.
- User wants to **batch expire** existing `IpRange` rows using a spreadsheet of **`ip range id`** values (e.g. exported from NSTL overlap / error output).

## Excel format

Expected columns: **serial id**, **cn name**, **en name**, **start ip**, **end ip**.

## Workflow (script order)

Use the **same Excel path** the user provided for steps 1–3. Step **6** uses the generated `NSTL_all_ip_to_load.xlsx` (written to the current working directory, typically project root).

**Typical order:** Batch **expire** (Step 5) usually runs **after** review and **before** bulk **load** (Step 6), so conflicting old `IpRange` rows are retired before new ones are inserted. Expire can also happen earlier/later per process (e.g. ops-only); treat Step 5 as “when the user is ready to expire ids,” not “only after load.”

Before each step: analyze what would change, report briefly, get approval, then run.

| Step | Before running: report |
|------|------------------------|
| 1 NSTLCreateIns | Which new Party records would be created (serial id, name), and that they will be linked to consortium 31772. No change if all already exist. |
| 2 NSTLLoadInsCheck | That you will produce/overwrite `NSTL_ins_check.xlsx` and `NSTL_ins_check_error.xlsx`; summarize row counts or name conflicts if you can infer from the Excel. |
| 3 NSTLLoadIPCheck + overlap filter | That you will produce/overwrite `NSTL_all_ip_to_load.xlsx` and `NSTL_all_ip_check_error.xlsx`, then run the **overlap filter** (Python 3 + **openpyxl** only—no Django; often a **one-off `python:3.x-slim` Docker** mount if the app container is Py2-only) to write `NSTL_all_ip_check_error_overlap_only.xlsx`. This step does not modify the DB. |
| 4 Review | **Ask the user to review only `NSTL_all_ip_check_error_overlap_only.xlsx`** (non-identical overlap / containment). Treat exact matches (`ip range exists` in the full file) as noise—summarize how many were stripped. Point to the full `NSTL_all_ip_check_error.xlsx` only if they need validation errors (`too large`, `private`, `invalid`) or raw detail. Decide which existing ranges need **expiring** before load. |
| 5 Batch expire (optional) | How many **active** `IpRange` rows would get `expiredAt` from the user’s expire list (and how many ids are unknown or already expired). **Usually before Step 6.** Prefer **`--dry-run`** first; separate approval before apply. |
| 6 NSTLLoadIPRange | How many rows from `NSTL_all_ip_to_load.xlsx` would be loaded (new Party if missing, new IpRange per row); this step **writes to the DB**. Run after overlaps are resolved (including any Step 5 expires). |
| 7 Cleanup (reminder) | **No script.** After the user **confirms** DB results (sample checks / sign-off), **remind them to delete** intermediate and working Excel files so they are not kept in the repo, leaked, or reopened by mistake. See **Cleanup** below. |

1. **New institutions only**  
   If the Excel includes new institutions (serial id / names not yet in DB), run:
   ```bash
   python scripts/NSTLCreateIns.py <path_to_excel>
   ```

2. **Institution name check**  
   Ensure one institution name per serialId:
   ```bash
   python scripts/NSTLLoadInsCheck.py <path_to_excel>
   ```
   Fix any conflicts reported in `NSTL_ins_check_error.xlsx` before continuing.

3. **IP check (validation + overlap)**  
   Compare rows with existing IP ranges; outputs "to load" and "errors":
   ```bash
   python scripts/NSTLLoadIPCheck.py <path_to_excel>
   ```
   Outputs:
   - `NSTL_all_ip_to_load.xlsx` — rows safe to load.
   - `NSTL_all_ip_check_error.xlsx` — all issues (too large, private, invalid, exists, contained, overlap same/different institution).

   **Immediately after** `NSTLLoadIPCheck` succeeds, run the overlap-only review file (same approval as Step 3—no separate approval round unless the user asks to stop). The filter is **pure file processing** (openpyxl); it does **not** import Django or touch the DB.

   **Host with Python 3:**
   ```bash
   python3 -m pip install openpyxl   # if needed
   python3 scripts/filter_nstl_ip_check_error_overlap_only.py
   ```

   **No Python 3 on the host / app container is Python 2 only:** run a **one-off** official image from the **project root** (writes `NSTL_all_ip_check_error_overlap_only.xlsx` into the mounted tree):
   ```bash
   docker run --rm -v "$PWD:/work" -w /work python:3.11-slim-bookworm \
     bash -lc "pip install --no-cache-dir -q openpyxl && python scripts/filter_nstl_ip_check_error_overlap_only.py"
   ```
   This writes **`NSTL_all_ip_check_error_overlap_only.xlsx`**, which **drops**:
   - **`ip range exists`** (exact same start/end as DB—identical range, nothing to decide)
   - **`ip range contained`** when the two emitted rows share the **same `serial id`** (new range sits inside a **larger range for the same institution**—redundant, like an exact duplicate for practical review)
   - Other non-overlap errors (`too large`, `private`, `invalid`)—those remain **only** in the full error workbook

   **Keeps** `ip range contained` when the spreadsheet `serial id` and the DB row `serial id` **differ** (new range inside **another** institution’s range—needs a decision).

   so the user is prompted to review **real overlap / containment** rows only.

4. **Review errors**  
   Focus the user on **`NSTL_all_ip_check_error_overlap_only.xlsx`**. Resolve conflicts per process; build or confirm the list of **`ip range id`** values to expire before load; see [reference.md](reference.md) if available.

5. **Batch expire (optional, usually before load)**  
   When review calls for retiring existing ranges, run **`batch_expire_ip_ranges_from_excel.py`** on a small spreadsheet of **`ip range id`** values (see section below). Prefer **`--dry-run`**, then apply after approval.

6. **Load IP ranges**  
   Load the cleaned "to load" file:
   ```bash
   python scripts/NSTLLoadIPRange.py NSTL_all_ip_to_load.xlsx
   ```

7. **Cleanup (reminder — after the user confirms results)**  
   **No script.** Remind the user to **remove working Excel artifacts**, for example:

   - Generated NSTL outputs: `NSTL_ins_check.xlsx`, `NSTL_ins_check_error.xlsx`, `NSTL_all_ip_to_load.xlsx`, `NSTL_all_ip_check_error.xlsx`, `NSTL_all_ip_check_error_overlap_only.xlsx`, `NSTL_all_ip_load_runtime_error.xlsx` (if any).
   - Any **copies** of source spreadsheets placed in the repo for Docker (e.g. `_nstl_work.xls`), **expire lists**, or exports with **`ip range id`**.
   - Watch for Excel lock files **`~$*.xlsx`** (delete if present; should be **gitignored**).

   Goal: no lingering institution/IP data in the project tree or accidental commits. The user may keep archives **outside** the repo per retention policy.

**Pipeline (single command with path on the fly):**  
Use the pipeline script and pass the user's Excel path as the first argument (any path, any filename). Add `--load` to also run **Step 6** (`NSTLLoadIPRange`) after checks. **`bulk_ip_load_pipeline.py` does not run batch expire** — run Step 5 manually between review and load when needed.

```bash
python scripts/bulk_ip_load_pipeline.py /path/to/user/file.xlsx [--load]
```
Example with a file in Downloads: `python scripts/bulk_ip_load_pipeline.py ~/Downloads/TEC-NSTL-IP-update.xlsx`

## Batch expire IP ranges (Excel)

**Workflow position:** Typically **Step 5**, **after** review (Step 4) and **before** load (Step 6), when overlapping DB ranges must be expired so the new file can load cleanly. It can be used at other times per process.

Use this when overlap resolution (or another process) requires **retiring existing DB ranges**. The script sets **`expiredAt = now`** on each listed range; it does **not** delete rows.

**Excel format**

- One column detectable as **`ip range id`**: same header as `NSTL_all_ip_check_error.xlsx` / overlap-only export (`ip range id`), or **`ipRangeId`** / **`ip_range_id`** (spacing/case-insensitive after normalization).
- Extra columns are fine; they are ignored. Duplicate ids are de-duplicated.
- Typical source: copy the **`ip range id`** column (and optional note columns) from error/review workbooks, or paste ids the checker printed as “IP ranges need to expire”.

**Commands** (run in the **same Docker / DB environment** as other NSTL scripts; path must be visible in-container). For **`.xlsx`** inputs the image needs **`openpyxl`** (added to `requirements.txt`; rebuild the image, or install once per run as below):

```bash
# Preview (no DB writes)
docker compose run --rm -w /var/www/api-python -e PYTHONPATH=/var/www/api-python \
  paywall-api-python2 sh -c "pip install -q 'openpyxl<3' && python scripts/batch_expire_ip_ranges_from_excel.py /var/www/api-python/expire_list.xlsx --dry-run"

# Apply after explicit user approval
docker compose run --rm -w /var/www/api-python -e PYTHONPATH=/var/www/api-python \
  paywall-api-python2 sh -c "pip install -q 'openpyxl<3' && python scripts/batch_expire_ip_ranges_from_excel.py /var/www/api-python/expire_list.xlsx"
```

**`.xls`** files do not need `openpyxl` (pandas uses xlrd).

Host-only (if Django settings and DB are configured locally):

```bash
python scripts/batch_expire_ip_ranges_from_excel.py path/to/expire_list.xlsx --dry-run
```

**Agent behavior:** Always offer **`--dry-run` first**, report counts (found / missing ids / already expired / to expire), then obtain **separate explicit approval** before running without `--dry-run`. This step **modifies production data**.

Optional: **`--column "Custom Header"`** if the id column name is non-standard.

## Error types (NSTLLoadIPCheck)

| Error | Meaning |
|-------|--------|
| ip range too large | Range size exceeds allowed limit. |
| ip range private | Range contains private IPs. |
| ip range invalid | Malformed or invalid IPs (e.g. 255.x). |
| ip range exists | Exact same range already in DB (ignore for load). **Excluded from `NSTL_all_ip_check_error_overlap_only.xlsx`**—do not ask the user to triage these. |
| ip range contained | New range is inside an existing range. **Same institution** (matching `serial id` on the paired rows): excluded from the overlap-only review file (skip like exact match). **Different institution**: kept for review. |
| ip range contain existing in same institution | New range fully contains existing range(s) for same institution (existing may need expire). |
| ip range contain existing in different institution | New range fully contains range(s) of another institution (conflict). |
| ip range overlap (same/different institution) | Partial overlap; decide expire or reject. |

## Technical notes

- IP comparison uses DB-backed overlap and existence checks (`startLong`/`endLong`) for efficiency.
- Scripts use shared helpers in `common.common`: `get_overlapping_ranges`, `exact_match_exists`.
- The overlap filter (`filter_nstl_ip_check_error_overlap_only.py`) is **Python 3** and only needs **openpyxl**; it does not use Django or the DB (pure file I/O). Default paths are project-root `NSTL_all_ip_check_error.xlsx` → `NSTL_all_ip_check_error_overlap_only.xlsx`. Use **`docker run python:3.x-slim`** from the project root when neither the host nor the app container has `python3`.
- `bulk_ip_load_pipeline.py` uses **`NSTL_PY3_FILTER_IMAGE`** (default `python:3.11-slim-bookworm`) for that Docker step; pass **`--no-docker-filter`** to skip if you cannot run Docker.

## Agent behavior after Step 3

1. Run the filter script; print the summary line (rows removed as exact match, overlap rows written).
2. When reporting for Step 4, lead with **overlap-only** counts and error-type breakdown from the overlap file—not the full 294-row-style dump unless the user asks.
3. Use **exact match** and **same-institution contained** only as a **factual aside** (e.g. "258 identical ranges and 22 same-inst contained rows removed from review; N rows still need overlap decisions"). Rescan the overlap-only file after filter changes if quoting counts.

## Agent behavior after Step 6 (load) or when the user confirms success

1. **Remind (Step 7):** Prompt the user to **delete** intermediate/generated Excel files and any temporary copies in the project directory (list the usual `NSTL_*.xlsx` names and `_nstl_work.xls` pattern). Do not delete files without the user’s confirmation.
2. If they use git, suggest **`git status`** to ensure no stray `*.xlsx` or incomplete ignores.

## Additional resources

- For process details and PDF instructions summary, see [reference.md](reference.md) when present.
