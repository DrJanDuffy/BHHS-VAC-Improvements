---
name: bhhs-vac-tech-tips-loop
description: Self-improving freshness loop for Dr. Jan Duffy's BHHS VAC "Miscellaneous Tech Tips" sheet (this repo's data/tech_tips.csv). Checks every tip's link and current relevance via Parallel Search, discovers candidate new tips, and — on repeated metric breaches — proposes a single gated, verified, revertible change to its own thresholds. The mechanical weekly pass runs unattended via .github/workflows/tech-tips-loop.yml; invoke this skill conversationally for an on-demand run, or whenever that workflow's PR summary flags NEEDS_DIAGNOSIS and asks for an L2 diagnosis.
---

# BHHS VAC Tech Tips — Self-Improving Freshness Loop

This skill is the conversational half of a two-part system living in this repo:

1. **`.github/workflows/tech-tips-loop.yml` + `scripts/check_tips.py`** — runs weekly (and on manual dispatch), mechanically: dead-link check, Parallel Search verification, candidate discovery, L1 metrics, and mechanical L5/L6 (trial tracking + revert-or-accept). It never merges anything — every change lands as a pull request for a human to review.
2. **This skill** — the judgment half: L2 diagnosis and L3 hypothesis need reasoning a script can't do. Run this when a human wants an on-demand check, or when a workflow PR's summary says `NEEDS_DIAGNOSIS`.

**This file is self-contained for the judgment steps**, but the actual checking logic lives in `scripts/check_tips.py` — read that file, don't reimplement its logic by hand.

---

## HARD RULES

- **Never push to `main` or merge a PR yourself.** Every data or config change — routine or self-improvement — lands as a PR. A human merges it.
- **Never edit `config/loop_config.json` directly on `main`.** A proposed change goes in its own PR (see L4) with a ledger entry; merging that PR *is* the human approval.
- **Never delete a `state/ledger.json` entry**, and never rewrite one except to append a `trial_run_dates` timestamp or set its terminal `outcome` (done mechanically by `check_tips.py` — leave that machinery alone).
- **Respect the Parallel Search budget** in `config/loop_config.json` (`max_parallel_search_calls_per_run`). A conversational run counts against the same weekly intent — don't burn a second full budget the same week the workflow already ran, unless the human explicitly asks for a fresh check.
- **A candidate tip discovered by search is never promoted to `active` by this skill.** It lands as `status: candidate_new` for a human to confirm; only a human edits that field.

---

## RUNNING A CONVERSATIONAL CHECK

If a human just wants an ad hoc run:

1. `cd scripts && python check_tips.py` (needs `PARALLEL_API_KEY` in the environment; use `--offline` for a dead-link-only pass with no Parallel spend, or `--dry-run` to preview without writing).
2. Read the printed summary. If it changed `data/tech_tips.csv`, `data/MISCELLANEOUS_TECH_TIPS.xlsx`, or any `state/*.json` file, open a PR for it (same shape as the workflow: one branch, one PR, labeled `tech-tips-loop`) — do not commit to `main`.
3. Report the summary to the human plainly. Flag only — this skill does not decide the tip is dead just because a script said so if the human has context the script doesn't (e.g., a link that's intentionally behind a login wall).

---

## THE SELF-IMPROVING LOOP

A suggestion box is not a loop. A loop measures, diagnoses, predicts, trials, **verifies, and reverts**. `check_tips.py` handles L1 (measure), L5 (apply/track a trial), and L6 (verify/revert) mechanically every run. **L2–L4 need judgment and happen here, conversationally.**

### L1 — MEASURE (mechanical, every run — see `check_tips.py`)

| Metric | Definition | Target |
|---|---|---|
| `precision` | Of tips flagged last run, the share still flagged or since resolved. Flags that silently vanished with no fix were false positives. | ≥ 0.70 |
| `coverage` | Active tips actually checked ÷ active tips total. | = 1.00 |
| `cost` | Parallel Search calls used ÷ `max_parallel_search_calls_per_run`. | ≤ 0.85 |
| `yield` | Resolved-since-last-run ÷ flagged-last-run. Did the report cause a fix? | ≥ 0.15 |
| `noise` | Flags at `repeat_count ≥ repeat_escalation_threshold` with no resolution ÷ total flagged. | ≤ 0.25 |

`yield`'s target is lower than the sibling CRM/task loops on purpose: this is a 14-tip sheet with a weekly cadence and no urgency comparable to a stale lead — a fix landing every 6-7 weeks is healthy, not broken.

The series lives in `state/metrics.json`. **A single run is noise; the series is the signal.**

### L2 — DIAGNOSE (you, on a 2+ consecutive breach)

`check_tips.py` already tells you which metric(s) breached 2+ runs running (the `NEEDS_DIAGNOSIS` state and the `⚠️ Breaching...` line in its summary). Your job: read `state/metrics.json` and `state/flags.json` and name the *specific* rule at fault.

"Yield is low" is not a diagnosis. "Yield is 0.0 because `stale_after_days: 180` never fires in a sheet this small before a human notices and fixes the link anyway — `stale` flags are just dead weight that never resolves through this loop's own mechanism" is.

No nameable rule → **stop**. Leave `diagnosis: UNRESOLVED` in your reply and let the breach carry forward. A change with no named cause is a guess.

### L3 — HYPOTHESIZE (one change, one prediction)

State, in your reply to the human:

- **The change** — the exact key/value to edit in `config/loop_config.json`. Not a description.
- **Predicted effect** — which metric moves, which direction, to what value.
- **Predicted non-effect** — which metrics must *not* move.
- **Verification window** — 3 runs (`trial_window_runs` in config).

Eligible changes are small: one threshold in `config/loop_config.json` (`stale_after_days`, `repeat_escalation_threshold`, `dead_link_timeout_seconds`, `max_parallel_search_calls_per_run` — lowering only, `discovery_queries_per_run`, `report_cap_items`). **Never** a new data source, a new write capability, a change to the PR-only posture, or a change to this file's HARD RULES.

### L4 — GATE (a PR, always — merging it is the approval)

Open a small PR that:
1. Changes exactly one value in `config/loop_config.json`.
2. Appends one entry to `state/ledger.json` with `outcome: "TRIAL"`, the exact prior value in `prior_text`, the prediction, and `must_not_move`, and `trial_run_dates: []`.

Title it `[PROPOSAL] adjust {key} — {routine}`. **Do not merge it.** Tell the human what it predicts and ask them to review. If it sits unmerged for `proposal_expiry_runs` (4) weekly runs, comment `EXPIRED — closing; re-diagnose from scratch if the metric still breaches` and close it — do not re-file the same text.

### L5 — TRIAL (mechanical once merged)

Once merged, `check_tips.py` finds the `TRIAL` ledger entry each run, appends the run date, and after `trial_window_runs` (3) runs, verifies automatically. You don't need to do anything here except notice the workflow PR summaries saying `TRIAL (run N of 3)` and mention it if the human asks.

### L6 — VERIFY (mechanical) → ACCEPT or REVERT

Also mechanical. `check_tips.py` compares the actual metric after 3 trial runs against the prediction and sets the ledger entry's `outcome` to `ACCEPTED` or `REVERTED`. **A `REVERTED` entry means the config value is still whatever was in the merged PR** — the script tracks the outcome but does not itself open a revert PR (no write-to-config capability beyond what a human-merged PR grants). If you see a `REVERTED` outcome in the ledger, **open a follow-up PR restoring the exact `prior_text` value** and say so plainly — a reverted trial is a successful iteration, not a failure.

### IMMUTABLE — never propose changing these, however the metrics argue for it

1. The PR-only posture — nothing in this system may commit or merge directly to `main`.
2. The human-merge-is-the-gate mechanism for config changes.
3. The `candidate_new` review gate — search-discovered tips are never auto-promoted to `active`.
4. `max_parallel_search_calls_per_run` may only be *lowered* by a proposal, never raised above its original value (16) without an explicit human ask outside this loop.
5. The 3-run trial window and the requirement to verify before accepting.
6. This list.

A system that can loosen its own safety rails will, given enough metric pressure, loosen them. This list is not subject to the loop.

### CONVERGENCE

All five metrics in target for `convergence_clean_runs_required` (4) consecutive runs → `MAINTENANCE`. L1 still runs every week; L2–L4 stay dormant until something breaches twice again. Say `Loop converged — maintenance mode` once when this happens; don't manufacture a change to have something to report.

---

## FAILURE MODES — "WRONG LOOKS LIKE THIS"

❌ Merging a PR yourself, ever — routine or proposal
❌ Editing `config/loop_config.json` on `main` without a PR
❌ Promoting a `candidate_new` row to `active` yourself
❌ Diagnosing off one run's metrics instead of a 2-run breach
❌ Proposing a change with no falsifiable prediction
❌ Treating an unmerged proposal PR as approved because nobody objected
❌ Reporting a `REVERTED` trial as a failure instead of a confirmed negative
❌ Raising `max_parallel_search_calls_per_run` above 16 via a proposal
❌ Rewriting or deleting a `state/ledger.json` entry instead of appending

✅ Weekly mechanical pass does L1/L5/L6 · you do L2/L3 on a real breach · every config change is its own small PR · merging is the gate · 3-run trial always verified · revert restores the exact prior value · converge and stay quiet when it's working

---

## CHANGELOG

- **2026-08-29 — v1.0.** Initial version, paired with `scripts/check_tips.py` and `.github/workflows/tech-tips-loop.yml`. Seeded from the BHHS VAC "Miscellaneous Tech Tips" spreadsheet (14 tips).
