# Workspace Connector Roster — Audit & Lean Set

**Snapshot:** 2026-09-05 · 43 connectors installed at the org level, 41 with
tools enabled in a default chat, ≈1,430 MCP tools loaded per session.

This is the companion to [`integrations-overview.md`](./integrations-overview.md).
That doc is the *catalog* (what could be connected); this one is the *roster*
(what actually is), with a recommended lean set. The goal is to cut the
default tool surface roughly in half without losing anything the BHHS VAC
lead → nurture → transaction pipeline or the workspace skills depend on.

Why it matters: every enabled connector's tool schemas ride along in each
session, and every connector is another permission surface and another
OAuth token to keep alive. ~1,400 tools is well past the point where the
long tail is helping.

## Two levers, not one

Connectors are installed **org-wide**, but tools are toggled **per chat**.
So there are two distinct actions below:

- **Disconnect** — remove from the org. For things nothing uses.
- **Off by default** — leave connected (a skill or occasional workflow
  needs it) but toggle it off in the chat's connector settings for VAC work.
  Turn it on for the session that needs it.

## Fix first (broken today)

These are in `needs_reconnect` or `unknown` state. Either re-auth them or
remove them — a half-installed connector is the worst of both worlds.

| Connector | State | Action |
|---|---|---|
| **Open Brain** | needs_reconnect | **Re-auth now.** The `open-brain-capture-operating` skill triggers at every session start and after every buyer/seller inquiry; it is silently failing until this is fixed. |
| LiveKit Video | needs_reconnect | Disconnect. Nothing in the VAC pipeline or skills references it. |
| Insightfulmcp | needs_reconnect | Disconnect unless someone can say what it is — empty description, no tools loaded. |
| Microsoft 365 | unknown, not enabled | Finish setup or remove. The practice runs on Google Workspace; keep only if a BHHS corporate SharePoint/Outlook dependency exists. |
| Rechat | unknown, not enabled | **Verify with Dr. Jan before touching.** Rechat is a brokerage platform (BHHS uses it in some regions); if it's live, it belongs in the core set. If not, remove. |

## Recommended lean set (keep, on by default)

22 connectors, ≈725 tools. Everything the CRM, sphere, scheduling,
content, and site-portfolio workflows actually call.

| Connector | ≈Tools | Role |
|---|---|---|
| Followup Ace | 189 | FUB — system of record for leads/deals. Largest single surface, but non-negotiable. |
| Cloze | 22 | Sphere/SOI CRM, synced from FUB. |
| Gmail | 29 | Inbox. |
| Google Calendar | 9 | Showings/appointments. |
| Google Drive | 11 | Documents. |
| Notion | 46 | Command center + SOPs. |
| Zapier | 47 | Bridge to CallAction, Homebot, kvCORE, RealScout. |
| Calendly | 36 | Client-facing scheduling links. |
| Airtable | 43 | Creative Requests & Intake Library. |
| Linear | 75 | Engineering issues for this repo. |
| Vercel | 37 | 50+ community/marketing sites (`vercel-freshness-audit`). |
| Cloudflare Developer Platform | 23 | DNS/zones/Workers for the domain portfolio. |
| cloudflare-observability | 7 | Worker logs — keep alongside the platform server. |
| Supabase | 30 | Backend DB for the NestJS VAC service. |
| Parallel Search | 2 | Mandated for every web search (`parallel-search-operating`). |
| Parallel Task MCP | 4 | Deep research / batch enrichment. |
| Open Brain | 4 | Session memory capture (once re-authed). |
| Otter.ai | 3 | Ramble intake source (`ramble-intake-router`). |
| OneUpApp | 55 | Social scheduling across GBP/FB/IG/LinkedIn. |
| Gamma | 18 | All client-facing decks (`gamma-client-materials-operating`). |
| Canva | 33 | Social graphics / marketing collateral. |
| Context7 | 2 | Library docs while building the backend. |

## Off by default (keep connected, enable per session)

Skills reference these, or they're used a few times a month. Leaving them
connected costs nothing; leaving them *enabled* costs ~600 tools per chat.

| Connector | ≈Tools | Why keep | Why off |
|---|---|---|---|
| Alpha Vantage | 130 | `carterworth` and `ruleof40` skills. | Zero overlap with real-estate sessions. |
| Adobe for creativity | 85 | Occasional pro image/video edits. | Canva + Gamma cover 95% of collateral; 85 tools is a lot of weight for the rest. |
| Zoom for Claude | 12 | Client-call recaps. | Only when reviewing a specific meeting. |
| Cloudinary | 30 | If the Vercel sites serve media through it. | Verify usage first; drop to *Disconnect* if none of the sites reference it. |
| Figma | 47 | Design handoff for the VAC frontend. | Not a daily tool. |
| cloudflare-builds | 6 | Debugging a failed Worker deploy. | Rare. |
| Granola | 6 | Meeting notes. | Redundant with Otter; consolidate on Otter and disconnect if unused after 30 days. |

## Disconnect

No skill, workflow, or catalog priority references these. Removing them
drops ≈450 tools from every session and retires several OAuth grants.

| Connector | ≈Tools | Reason |
|---|---|---|
| **Asana** | 31 | Retired 2026-08-28 (see `task-hygiene-sweep`). Still connected and still loading tools. |
| **Attio** | 40 | Third CRM. FUB is the system of record and Cloze is the sphere layer; a third one only creates drift. |
| **Atlassian Rovo** | 41 | Jira/Confluence. Linear + Notion already fill both roles. |
| ElevenLabs | 125 | Voice/agent platform. No voice product in the VAC pipeline. Reconnect if that changes. |
| Tavus Video | 80 | AI video avatars. Same as above. |
| Jam | 35 | Screen-recording bug reports. Nobody files them here. |
| v0 | 8 | Frontend scaffolding; overlaps with Vercel + this repo's own tooling. |
| Facebook Developer Tools | 11 | Meta *app* development, not page/ads management. OneUpApp handles posting. |
| Cerebras.ai | 3 | Docs search for an inference provider nothing uses. |
| cloudflare-api | 3 | Generic API passthrough; the Developer Platform server covers it. |
| cloudflare-docs | 2 | Exact duplicate of the `search_cloudflare_documentation` tool already in the Developer Platform *and* observability servers. |
| LiveKit Video | 9 | Broken (needs_reconnect) and unreferenced. |
| Insightfulmcp | 0 | Broken and unidentified. |

## Net effect

| | Servers | ≈Tools |
|---|---|---|
| Today (enabled in chat) | 41 | 1,430 |
| Lean set, on by default | 22 | 725 |
| Reduction | −19 | **−49%** |

The remaining big rocks are Followup Ace (189) and Linear (75). Both are
justified — FUB is the business — but if a session is only doing CRM
work, toggling Linear/Vercel/Cloudflare off for that chat is a further
easy ~140-tool win.

## Rollout

1. Re-auth **Open Brain** (skills are silently failing).
2. Ask Dr. Jan about **Rechat**; resolve Microsoft 365 either way.
3. Disconnect the 13 in the *Disconnect* table. Asana, Attio, Atlassian
   first — those are the ones most likely to be written to by accident.
4. Toggle the *Off by default* group off in the workspace's default chat
   settings.
5. Re-run this audit in 90 days; the catalog in
   `integrations-overview.md` grows faster than anyone prunes it.
