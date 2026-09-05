# Integration Connectors Overview

This document catalogs the third-party connectors available to the BHHS
Virtual Assistant/Concierge (VAC) platform, and groups them by how they map
onto the real-estate workflows this project supports (lead intake, CRM
sync, scheduling, marketing, and back-office operations for a BHHS Nevada
REALTOR practice).

Each connector is listed with its auth model — **Managed** (Anthropic-hosted
OAuth), **OAuth** (bring-your-own OAuth app), **API Key**, **MCP**
(exposed as a Model Context Protocol server), or **Native** (already
connected to this workspace as a first-party tool suite; usable from Claude
with no extra provisioning, but the VAC backend still needs the vendor's own
API credentials to call it directly) — since that determines the setup work
(an admin consent flow vs. a stored secret) before the VAC backend can call
it.

> Auth models aren't mutually exclusive — several connectors (Notion,
> Vercel, Resend, Jira, Sanity, etc.) support more than one, so pick
> whichever fits how a given environment provisions credentials.

## How to use this doc

0. For what is *currently* connected to the workspace — and which of those
   to keep, mute, or disconnect — see [`connector-roster.md`](./connector-roster.md).
1. Skim **Priority for BHHS VAC** for the connectors worth wiring up first.
2. Use the category tables to find alternatives or fill a gap (e.g. a second
   e-signature or SMS provider).
3. When a connector is added to the NestJS backend, record it in
   `docs/integrations-overview.md` (this file) under its category with a
   one-line note on what it's used for, so this stays the source of truth
   instead of drifting from the code.

---

## Priority for BHHS VAC

Ranked by how directly they support the lead → nurture → transaction
pipeline this platform automates. Everything here is present in the
account's connector catalog today.

| Connector | Why it matters here |
|---|---|
| **Slack** | Ops/agent alerting — new lead, hot-lead score, deal milestone notifications. |
| **Google** (Gmail, Calendar, Drive) | Primary inbox, showing/appointment scheduling, document storage for a solo-to-small-team practice. |
| **GitHub** | This repo's own CI/CD and issue tracking. |
| **Notion** | SOPs and the internal command-center doc referenced elsewhere in this workspace. |
| **Zapier** | Bridges the connectors below to systems without a native connector yet (Follow Up Boss, kvCORE, RealScout, Homebot, CallAction). |
| **Calendly** | Client-facing scheduling links for showings and consults. |
| **HubSpot / Salesforce** | CRM sync target if/when the practice consolidates off point solutions. |
| **Airtable** | Creative/content intake tracking (see the Airtable creative-intake skill). |
| **Linear** | Engineering issue tracking for this codebase. |

---

## Featured (top-of-catalog)

| Connector | Auth | Category |
|---|---|---|
| Slack | Managed / OAuth | Messaging |
| GitHub | Managed / OAuth | Dev / Source control |
| Notion | OAuth, MCP, API Key | Docs & knowledge |
| Linear | Managed / OAuth | Project management |
| Microsoft *(beta)* | Managed / OAuth | Productivity suite |
| Snowflake | Managed / OAuth | Data warehouse |
| Salesforce *(beta)* | Managed / OAuth | CRM |

## CRM & Sales

| Connector | Auth |
|---|---|
| Salesforce *(beta)* | OAuth |
| HubSpot | OAuth |
| Attio | Native |
| monday.com | OAuth, API Key |

## Messaging & Communication

| Connector | Auth |
|---|---|
| Slack | Managed, OAuth |
| Discord | OAuth |
| Telegram Bot | API Key |
| Linq *(beta)* | OAuth |
| Photon | OAuth |
| Zoom | OAuth |
| Google (Gmail) | OAuth |
| Mailgun | API Key |
| SendGrid | API Key |
| Resend | OAuth, MCP, API Key |

## Scheduling

| Connector | Auth |
|---|---|
| Calendly | OAuth, API Key |
| Google Calendar | OAuth |

## Docs, Content & Knowledge

| Connector | Auth |
|---|---|
| Notion | OAuth, MCP, API Key |
| Google Drive | OAuth |
| Airtable | MCP |
| Coda | MCP |
| Sanity | OAuth, MCP, API Key |
| Contentful | API Key |
| Webflow | OAuth, MCP, API Key |
| Confluence *(via Atlassian Rovo)* | OAuth |

## Project & Task Management

| Connector | Auth |
|---|---|
| Linear | Managed, OAuth |
| Jira | OAuth, MCP |
| Asana | MCP |
| ClickUp | OAuth, API Key |
| Todoist | MCP |
| TickTick | MCP |
| monday.com | OAuth, API Key |
| Coda | MCP |

## Identity & Access

| Connector | Auth |
|---|---|
| WorkOS | OAuth |
| Okta | OAuth |
| Auth0 | OAuth |
| Clerk | API Key |

## Design & Media

| Connector | Auth |
|---|---|
| Figma | OAuth |
| Canva | OAuth |
| Adobe (for creativity) | Native |
| Cloudinary | MCP, API Key |
| Zeplin | OAuth |
| ElevenLabs | API Key |
| Gamma | Native |

## Dev, Infra & Data

| Connector | Auth |
|---|---|
| GitHub | Managed, OAuth |
| GitLab | OAuth, API Key |
| Gitee | OAuth |
| Vercel | OAuth, MCP, API Key |
| Netlify | MCP |
| Cloudflare | MCP |
| Render | API Key |
| Railway | API Key |
| Supabase | MCP |
| PlanetScale | MCP |
| Neon | API Key |
| Snowflake | Managed, OAuth |
| Databricks | OAuth |
| ClickHouse | MCP |
| Tinybird | API Key |
| Convex | OAuth |
| ngrok | API Key |
| CircleCI | API Key |
| Postman | MCP |

## Analytics & Monitoring

| Connector | Auth |
|---|---|
| Mixpanel | MCP |
| PostHog | MCP |
| Segment | API Key |
| Datadog | API Key |
| Sentry | MCP |
| PagerDuty | MCP |
| Similarweb | MCP |
| G2 | MCP |
| Local Falcon | MCP |

## Commerce, Payments & Finance

| Connector | Auth |
|---|---|
| Stripe | MCP |
| Shopify | OAuth |
| Xero | MCP |
| Brex | MCP |
| Razorpay | MCP |
| Agentcard | MCP |
| Embat | MCP |
| Docusign | OAuth |

## HR & People Ops

| Connector | Auth |
|---|---|
| Workday | OAuth |
| BambooHR | OAuth, API Key |

## Search & Automation Glue

| Connector | Auth |
|---|---|
| Zapier | Native |
| n8n | API Key |
| Make | MCP |
| Algolia | API Key |
| Firecrawl | API Key |

## AI / Model Providers

| Connector | Auth |
|---|---|
| Anthropic | API Key |
| OpenAI | API Key |
| OpenRouter | API Key |
| Google Gemini | API Key |
| DeepSeek | API Key |
| Cohere | API Key |
| Perplexity | API Key |
| Replicate | API Key |
| Hugging Face | MCP |
| Pinecone | API Key |

## Social & Growth

| Connector | Auth |
|---|---|
| LinkedIn | OAuth |
| Reddit | OAuth |
| Twitch | OAuth |
| Spotify | OAuth |
| beehiiv | OAuth, MCP, API Key |
| Zomato | MCP |
| Zernio | MCP |

## Everything else in the catalog

Box, Egnyte, Dropbox — file storage; Miro — whiteboarding; O'Reilly —
learning content; Ticket Tailor — event ticketing; Wix — site builder;
Candid — nonprofit/funder research; Crowdin, Typeform, Kernel, AgentMail,
Manufact, Mem0, WHOOP — round out the remainder of the catalog and can be
added to a category above as they become relevant.

---

*Generated from the connector catalog snapshot on 2026-09-05. Re-run this
inventory periodically — new connectors are added to the catalog faster
than this doc will be updated by hand.*
