#!/usr/bin/env python3
"""BHHS VAC Tech Tips — self-improving freshness loop.

Every run:
  1. Loads data/tech_tips.csv and state/{metrics,flags,ledger}.json.
  2. Checks every active tip's link (dead-link probe) and asks Parallel
     Search whether the tool/feature it describes is still current
     (L1 — MEASURE happens mechanically here; L2-L4 diagnosis/hypothesis/
     proposal are judgment calls left to a human or the companion Claude
     skill, see .claude/skills/bhhs-vac-tech-tips-loop/SKILL.md).
  3. Runs one broad discovery query for tech tips not yet in the sheet.
  4. Updates data/tech_tips.csv in place (status + last_verified + new
     candidate rows), regenerates data/MISCELLANEOUS_TECH_TIPS.xlsx, and
     updates state/*.json.
  5. Writes a markdown run summary to stdout / --summary-out, which the
     GitHub Actions workflow uses as the pull request body. This script
     NEVER pushes or opens a PR itself — that is the workflow's job, and
     only after this script exits 0.

Nothing here merges to main directly: this script only ever changes the
working tree. The GitHub Actions workflow is responsible for branching,
committing, and opening a PR for a human to review and merge.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import difflib
import json
import sys
from pathlib import Path

import requests

import build_xlsx
import parallel_client

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "tech_tips.csv"
CONFIG_PATH = REPO_ROOT / "config" / "loop_config.json"
METRICS_PATH = REPO_ROOT / "state" / "metrics.json"
FLAGS_PATH = REPO_ROOT / "state" / "flags.json"
LEDGER_PATH = REPO_ROOT / "state" / "ledger.json"

SUPERSEDED_PHRASES = [
    "no longer available",
    "no longer offered",
    "discontinued",
    "has been retired",
    "is retired",
    "sunset",
    "replaced by",
    "renamed to",
    "rebranded as",
    "deprecated",
    "this feature has been removed",
]

CSV_FIELDS = [
    "id", "topic", "link", "synopsis", "category", "source_type",
    "added_date", "last_verified", "status", "first_flagged",
    "repeat_count", "notes",
]


def today() -> str:
    return dt.date.today().isoformat()


def iso_week() -> str:
    y, w, _ = dt.date.today().isocalendar()
    return f"{y}-W{w:02d}"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def load_tips(path: Path = CSV_PATH) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_tips(rows: list[dict], path: Path = CSV_PATH) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)


def check_link(url: str, timeout: int, retries: int) -> tuple[str, int | None, str]:
    """Returns (state, http_code, final_url). state in {OK, REDIRECT, DEAD}."""
    if not url:
        return "DEAD", None, url
    last_exc = None
    for attempt in range(retries + 1):
        try:
            resp = requests.head(url, timeout=timeout, allow_redirects=True)
            if resp.status_code in (405, 403):  # some hosts reject HEAD
                resp = requests.get(url, timeout=timeout, allow_redirects=True, stream=True)
            if 200 <= resp.status_code < 400:
                state = "REDIRECT" if resp.url != url else "OK"
                return state, resp.status_code, resp.url
            return "DEAD", resp.status_code, resp.url
        except requests.RequestException as exc:  # noqa: PERF203
            last_exc = exc
    return "DEAD", None, url + f" (error: {last_exc})"


def verify_with_parallel(tip: dict, calls_budget: list[int]) -> tuple[str, list[str]]:
    """Returns (signal, evidence_excerpts). signal in
    {OK, POSSIBLY_SUPERSEDED, SKIPPED_BUDGET, SKIPPED_ERROR}.
    """
    if calls_budget[0] <= 0:
        return "SKIPPED_BUDGET", []
    objective = (
        "Verify whether this Berkshire Hathaway HomeServices (BHHS) real estate "
        f"agent tech tip is still current: \"{tip['topic']}\". Say whether the "
        "tool, feature, or vendor described still exists under this name, or "
        "whether BHHS or the vendor has renamed, replaced, retired, or "
        "discontinued it. Note any newer official BHHS tech tip covering the "
        "same topic."
    )
    queries = [tip["topic"], f"BHHS {tip['topic']}"]
    try:
        resp = parallel_client.search(objective, queries, max_results=4)
    except parallel_client.ParallelAPIError:
        return "SKIPPED_ERROR", []
    calls_budget[0] -= resp.calls_used

    evidence = []
    signal = "OK"
    for r in resp.results:
        for excerpt in r.excerpts:
            lower = excerpt.lower()
            if any(phrase in lower for phrase in SUPERSEDED_PHRASES):
                signal = "POSSIBLY_SUPERSEDED"
                evidence.append(f"{r.url}: {excerpt[:200]}")
    return signal, evidence[:3]


def discover_candidates(existing_topics: list[str], config: dict, calls_budget: list[int]) -> list[dict]:
    if calls_budget[0] <= 0:
        return []
    objective = (
        "Find current Berkshire Hathaway HomeServices (BHHS) agent tech tips, "
        "training videos, or tools (e.g. ACE, Maxa Design Studio, RealScout, "
        "Breeze, Skyslope, agent showcase pages) published or updated recently "
        "that a BHHS Nevada/Arizona VAC tech-tips sheet may be missing."
    )
    queries = [
        "BHHS ACE Social Media new agent tech tip",
        "Berkshire Hathaway HomeServices new agent tool 2026",
    ][: config.get("discovery_queries_per_run", 2)]
    try:
        resp = parallel_client.search(objective, queries, max_results=6)
    except parallel_client.ParallelAPIError:
        return []
    calls_budget[0] -= resp.calls_used

    candidates = []
    for r in resp.results:
        title = r.title or r.url
        is_dupe = any(
            difflib.SequenceMatcher(None, title.lower(), t.lower()).ratio() > 0.6
            for t in existing_topics
        )
        if is_dupe or not r.url:
            continue
        candidates.append({"title": title, "url": r.url, "excerpt": (r.excerpts[0] if r.excerpts else "")[:250]})
    return candidates[:5]


def run(dry_run: bool, offline: bool, summary_out: Path | None) -> int:
    config = load_json(CONFIG_PATH)
    metrics_state = load_json(METRICS_PATH)
    flags_state = load_json(FLAGS_PATH)
    ledger_state = load_json(LEDGER_PATH)
    rows = load_tips()

    prior_flags = flags_state.get("flags", {})
    # Always starts at the full budget; --offline just never calls the
    # functions that would spend it, so calls_used correctly comes out 0.
    calls_budget = [config["max_parallel_search_calls_per_run"]]

    active_rows = [r for r in rows if r["status"] not in ("archived",)]
    findings: list[dict] = []
    new_flags: dict = {}
    resolved_since_last_run: list[str] = []
    fully_checked_count = 0

    for row in active_rows:
        link_state, http_code, final_url = check_link(
            row["link"], config["dead_link_timeout_seconds"], config["dead_link_retries"]
        )
        skipped_verification = False

        if link_state == "DEAD":
            tier, status, signal = "P1", "dead_link", "DEAD_LINK"
            fully_checked_count += 1
        else:
            if link_state == "REDIRECT" and final_url != row["link"]:
                row["notes"] = (row["notes"] + f" | redirects to {final_url}").strip(" |")
            if offline:
                signal = "OK"
            else:
                signal, evidence = verify_with_parallel(row, calls_budget)
                if evidence:
                    row["notes"] = (row["notes"] + " | " + " ; ".join(evidence)).strip(" |")
            if signal == "POSSIBLY_SUPERSEDED":
                tier, status = "P2", "possibly_superseded"
                fully_checked_count += 1
            elif signal in ("SKIPPED_BUDGET", "SKIPPED_ERROR"):
                # Could not verify currency this run — never let a skipped
                # check masquerade as "resolved" or silently drop a real
                # flag. Carry the prior flag state forward unchanged and
                # exclude this tip from the coverage numerator.
                skipped_verification = True
                prior_flag = prior_flags.get(row["id"])
                if prior_flag:
                    tier, status = prior_flag["tier"], prior_flag["status"]
                else:
                    tier, status = None, row["status"] if row["status"] != "active" else "active"
            else:
                fully_checked_count += 1
                last_verified = row.get("last_verified") or ""
                stale = False
                if last_verified:
                    age_days = (dt.date.today() - dt.date.fromisoformat(last_verified)).days
                    stale = age_days > config["stale_after_days"]
                if stale:
                    tier, status = "P2", "stale"
                else:
                    tier, status = None, "active"
                    row["last_verified"] = today()

        prior = prior_flags.get(row["id"])
        if tier and skipped_verification:
            # Unchanged carry-forward: keep the existing flag's age/repeat
            # exactly as they were — but still surface it in the report,
            # tagged as unverified, so a flaky API call this run doesn't
            # make a real, still-open issue silently disappear from view.
            new_flags[row["id"]] = prior
            row["status"] = status
            findings.append({
                "id": row["id"], "topic": row["topic"], "tier": tier,
                "signal": f"{status} (unverified this run)",
                "repeat": prior.get("repeat_count", 0) + 1, "http_code": http_code,
            })
        elif tier:
            first_flagged = prior["first_flagged"] if prior else today()
            repeat = (prior.get("repeat_count", 0) + 1) if prior else 0
            new_flags[row["id"]] = {
                "tier": tier,
                "status": status,
                "first_flagged": first_flagged,
                "repeat_count": repeat,
                "last_seen": today(),
            }
            row["status"] = status
            row["first_flagged"] = first_flagged
            row["repeat_count"] = str(repeat)
            escalated_tier = tier
            if repeat + 1 >= config["repeat_escalation_threshold"] and tier == "P2":
                escalated_tier = "P1"
            findings.append({
                "id": row["id"], "topic": row["topic"], "tier": escalated_tier,
                "signal": status, "repeat": repeat + 1, "http_code": http_code,
            })
        else:
            if prior:
                resolved_since_last_run.append(row["id"])
            row["status"] = status if status else "active"
            row["first_flagged"] = ""
            row["repeat_count"] = "0"

    candidates = [] if offline else discover_candidates(
        [r["topic"] for r in rows], config, calls_budget
    )
    next_id_num = max((int(r["id"].split("-")[1]) for r in rows), default=0) + 1
    for c in candidates:
        rows.append({
            "id": f"tip-{next_id_num:03d}", "topic": c["title"], "link": c["url"],
            "synopsis": c["excerpt"], "category": "Uncategorized",
            "source_type": "article", "added_date": today(), "last_verified": "",
            "status": "candidate_new", "first_flagged": today(), "repeat_count": "0",
            "notes": "Discovered by Parallel Search — needs human review before promoting to active.",
        })
        next_id_num += 1

    # --- L1 MEASURE ---
    total_checked = len(active_rows)
    flagged_last_run = list(prior_flags.keys())
    precision_hits = sum(
        1 for fid in flagged_last_run
        if fid in new_flags or fid in resolved_since_last_run
    )
    precision = round(precision_hits / len(flagged_last_run), 2) if flagged_last_run else 1.0
    coverage = round(fully_checked_count / max(len(active_rows), 1), 2)
    calls_used = config["max_parallel_search_calls_per_run"] - calls_budget[0]
    cost = round(calls_used / max(config["max_parallel_search_calls_per_run"], 1), 2)
    yield_metric = round(
        len(resolved_since_last_run) / len(flagged_last_run), 2
    ) if flagged_last_run else 1.0
    repeat_thresh = config["repeat_escalation_threshold"]
    noisy = sum(1 for f in new_flags.values() if f["repeat_count"] + 1 >= repeat_thresh)
    noise = round(noisy / len(new_flags), 2) if new_flags else 0.0

    metrics_entry = {
        "date": today(), "iso_week": iso_week(),
        "precision": precision, "coverage": coverage, "cost": cost,
        "yield": yield_metric, "noise": noise,
        "calls_used": calls_used, "flagged_count": len(new_flags),
        "resolved_count": len(resolved_since_last_run),
        "candidates_found": len(candidates),
        "suppressed": False,
    }

    targets = {"precision": (">=", 0.70), "coverage": ("==", 1.00), "cost": ("<=", 0.85),
               "yield": (">=", 0.15), "noise": ("<=", 0.25)}
    breaches = []
    for name, (op, target) in targets.items():
        val = metrics_entry[name]
        ok = {"==": val == target, ">=": val >= target, "<=": val <= target}[op]
        if not ok:
            breaches.append(name)
    metrics_entry["breaches"] = breaches

    prior_runs = [r for r in metrics_state["runs"] if not r.get("suppressed")]
    consecutive_breach_names = []
    for name in breaches:
        if prior_runs and name in prior_runs[-1].get("breaches", []):
            consecutive_breach_names.append(name)

    if not dry_run:
        metrics_state["runs"].append(metrics_entry)
        save_json(METRICS_PATH, metrics_state)
        flags_state["flags"] = new_flags
        save_json(FLAGS_PATH, flags_state)
        save_tips(rows)
        build_xlsx.build()

    # --- L6 VERIFY (mechanical: only checks a TRIAL entry already in the ledger) ---
    verify_note = None
    for entry in reversed(ledger_state.get("entries", [])):
        if entry.get("outcome") == "TRIAL":
            trial_runs = entry.get("trial_run_dates", [])
            if not dry_run:
                trial_runs.append(today())
                entry["trial_run_dates"] = trial_runs
            if len(trial_runs) >= config["trial_window_runs"]:
                predicted_metric = entry["predicted"]["metric"]
                predicted_to = entry["predicted"]["to"]
                actual_val = metrics_entry.get(predicted_metric)
                must_not_move = entry.get("must_not_move", [])
                broke_guard = any(m in breaches for m in must_not_move)
                hit_target = actual_val is not None and (
                    actual_val >= predicted_to if predicted_to >= entry["predicted"]["from"]
                    else actual_val <= predicted_to
                )
                if broke_guard:
                    entry["outcome"] = "REVERTED"
                    verify_note = f"Trial REVERTED — a must-not-move metric ({', '.join(must_not_move)}) breached."
                elif hit_target:
                    entry["outcome"] = "ACCEPTED"
                    verify_note = f"Trial ACCEPTED — {predicted_metric} reached {actual_val} (target {predicted_to})."
                else:
                    entry["outcome"] = "REVERTED"
                    verify_note = f"Trial REVERTED — {predicted_metric} did not reach {predicted_to} (actual {actual_val})."
            break

    if not dry_run:
        save_json(LEDGER_PATH, ledger_state)

    loop_state = "LEARNING"
    if any(e.get("outcome") == "TRIAL" for e in ledger_state.get("entries", [])):
        loop_state = "TRIAL"
    elif len(prior_runs) >= config["convergence_clean_runs_required"] and not breaches:
        loop_state = "MAINTENANCE"
    elif consecutive_breach_names:
        loop_state = "NEEDS_DIAGNOSIS"

    findings.sort(key=lambda f: (f["tier"], -f["repeat"]))
    capped = findings[: config["report_cap_items"]]
    withheld = max(0, len(findings) - len(capped))

    summary_lines = [
        f"# BHHS VAC Tech Tips — {iso_week()} freshness check ({today()})",
        "",
        f"Checked **{total_checked}** active tips · **{len(new_flags)}** flagged · "
        f"**{len(resolved_since_last_run)}** resolved since last run · "
        f"**{len(candidates)}** new candidate tip(s) discovered.",
        "",
    ]
    if capped:
        summary_lines.append("## Flagged")
        for f in capped:
            repeat_note = f" (REPEAT×{f['repeat']})" if f["repeat"] > 1 else ""
            summary_lines.append(f"- **{f['tier']}** `{f['signal']}` — {f['topic']}{repeat_note}")
        if withheld:
            summary_lines.append(f"- _...{withheld} more withheld over the {config['report_cap_items']}-item cap._")
    else:
        summary_lines.append("## Flagged\nNothing found — all active tips checked out clean.")

    if candidates:
        summary_lines.append("\n## New candidate tips (need human review)")
        for c in candidates:
            summary_lines.append(f"- [{c['title']}]({c['url']})")

    if resolved_since_last_run:
        summary_lines.append(f"\n## Resolved since last run\n{', '.join(resolved_since_last_run)}")

    if verify_note:
        summary_lines.append(f"\n## Self-improvement trial\n{verify_note}")

    summary_lines.append(
        f"\n## Loop\n`precision {precision} · coverage {coverage} · cost {cost} · "
        f"yield {yield_metric} · noise {noise}` — **{loop_state}**"
    )
    if consecutive_breach_names:
        summary_lines.append(
            f"\n⚠️ Breaching 2+ consecutive runs: {', '.join(consecutive_breach_names)}. "
            "Needs an L2 diagnosis — run the `bhhs-vac-tech-tips-loop` skill conversationally "
            "to name the specific rule at fault and (if warranted) open a proposal PR against "
            "`config/loop_config.json`."
        )

    summary_md = "\n".join(summary_lines)
    print(summary_md)
    if summary_out:
        summary_out.write_text(summary_md + "\n", encoding="utf-8")

    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Compute and print everything, write nothing.")
    ap.add_argument("--offline", action="store_true", help="Skip all Parallel Search calls (dead-link check only).")
    ap.add_argument("--summary-out", type=Path, default=None)
    args = ap.parse_args()
    return run(dry_run=args.dry_run, offline=args.offline, summary_out=args.summary_out)


if __name__ == "__main__":
    sys.exit(main())
