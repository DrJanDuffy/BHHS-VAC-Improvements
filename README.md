# BHHS VAC Improvements

A self-improving freshness loop for Dr. Jan Duffy's BHHS Virtual Achievement Center (VAC) **Miscellaneous Tech Tips** sheet.

## What this is

The VAC tech-tips sheet is a list of short tips (topic + link + synopsis) pointing agents at BHHS tools and training — RealScout, ACE Social Media, Maxa Design Studio, Skyslope, Breeze, and so on. Links rot, tools get renamed, and new tips get published elsewhere without ever landing here. This repo keeps that sheet fresh with almost no manual upkeep:

- **`data/tech_tips.csv`** is the canonical, version-controlled source of truth.
- **`data/MISCELLANEOUS_TECH_TIPS.xlsx`** is generated from the CSV — hand this to the VAC team; don't hand-edit it, it will be overwritten.
- **A weekly GitHub Action** (`.github/workflows/tech-tips-loop.yml`) checks every tip's link, asks [Parallel Search](https://parallel.ai) whether the tool it describes is still current, looks for new tips the sheet is missing, and opens a **pull request** with anything it finds. Nothing ever lands on `main` without a human merging the PR.
- **A companion Claude Code skill** (`.claude/skills/bhhs-vac-tech-tips-loop/SKILL.md`) does the judgment work the script can't: when a metric misbehaves for two runs running, it diagnoses why and proposes one small, falsifiable tweak to the loop's own thresholds — gated behind its own PR, trialed for 3 runs, and reverted automatically if it doesn't pan out.

## Setup

1. **Add a repo secret** `PARALLEL_API_KEY` (Settings → Secrets and variables → Actions) with a key from [platform.parallel.ai](https://platform.parallel.ai). Without it, the workflow still runs the dead-link check but skips every Parallel Search call.
2. That's it — the workflow runs every Monday, and can also be triggered manually from the Actions tab (`workflow_dispatch`).

## How a run works

```
scripts/check_tips.py
  ├─ dead-link check on every active tip (HTTP HEAD/GET, retried once)
  ├─ Parallel Search: "is this tool/feature still current?" (skipped for already-dead links)
  ├─ Parallel Search: "what BHHS tech tips are we missing?" (one broad discovery pass)
  ├─ updates data/tech_tips.csv (status, last_verified, new candidate_new rows)
  ├─ regenerates data/MISCELLANEOUS_TECH_TIPS.xlsx from the CSV (scripts/build_xlsx.py)
  ├─ updates state/metrics.json, state/flags.json, state/ledger.json
  └─ prints a markdown summary → becomes the PR body
```

The GitHub Actions workflow then opens (or updates) a single PR with whatever changed. **Review it like any other PR:**

| Row color in the xlsx | Status | What it means |
|---|---|---|
| Red | `dead_link` | The link is unreachable — fix or replace it. |
| Yellow | `possibly_superseded` / `stale` | Parallel Search found language suggesting the tool was renamed/retired, or the tip hasn't been re-verified in a long time. Worth a look. |
| Green | `candidate_new` | A tip Parallel Search found that isn't in the sheet yet. Confirm it's real and relevant, then change its `status` to `active`. |

Merging the PR is how you approve the change — nothing writes to `main` on its own.

## The self-improving loop

`scripts/check_tips.py` measures five things every run (precision, coverage, cost, yield, noise — defined in `config/loop_config.json` and the skill file) and tracks them in `state/metrics.json`. If one misbehaves for two runs running, the workflow PR summary says `NEEDS_DIAGNOSIS` and asks for the companion skill to be run conversationally — that's where a human (or Claude, invoked on this) diagnoses the specific rule at fault and proposes **one** small, falsifiable config change, gated behind its own PR. Merging that PR starts a 3-run trial; the script verifies the prediction automatically afterward and records the outcome (accepted or reverted) in `state/ledger.json`, which is append-only — nothing is ever silently un-done.

Full mechanics, the immutable rules the loop can never propose changing, and the failure modes to watch for are documented in `.claude/skills/bhhs-vac-tech-tips-loop/SKILL.md`.

## Repo layout

```
data/
  tech_tips.csv                    canonical data — edit this, not the xlsx
  MISCELLANEOUS_TECH_TIPS.xlsx     generated deliverable (scripts/build_xlsx.py)
config/
  loop_config.json                 tunable thresholds (see the skill file for what may change them)
state/
  metrics.json                     L1 metric time series
  flags.json                       current + historical flags, for aging/repeat tracking
  ledger.json                      append-only self-improvement history
scripts/
  check_tips.py                    the main loop
  build_xlsx.py                    regenerates the xlsx from the CSV
  parallel_client.py               thin Parallel Search API wrapper
.github/workflows/
  tech-tips-loop.yml               weekly + on-demand CI run, opens the PR
.claude/skills/bhhs-vac-tech-tips-loop/
  SKILL.md                         the judgment half of the loop (L2-L4 diagnosis/proposal)
```

## Running it locally

```bash
pip install -r scripts/requirements.txt
export PARALLEL_API_KEY=...        # optional — omit to skip Parallel calls
cd scripts
python check_tips.py               # full run, writes data/ and state/
python check_tips.py --dry-run     # compute and print, write nothing
python check_tips.py --offline     # dead-link check only, no Parallel spend
```
