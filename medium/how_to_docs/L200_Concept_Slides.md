# L200 — Build an AI Agent with Memory
### Concept Walkthrough Deck (Speaker / Slide Draft)

> Companion deck to the L200 Lab Guide. The lab teaches the *mechanics*; this deck explains the *concepts* behind each step — what they are, what to focus on, how they're governed, what production looks like, and concrete industry examples (retail & property/real-estate primary; FSI, manufacturing & healthcare as cross-industry reference).

---

## Slide 1 — Title

**Build an AI Agent with Memory**
From local laptop to governed production app on Databricks

- Level 200 · Hands-on lab + concept walkthrough
- What we'll build: an agent that *searches documents, queries data, and remembers conversations*
- Lens for today: for every building block → **Concept · Focus · Governance · Production · Industry example**

*Speaker note:* The lab gives you the recipe. The goal of these slides is so you walk away able to explain **why** each piece exists to a customer architect, not just **how** to wire it.

---

## Slide 2 — The Agent in One Picture

**A production agent is an assembly of governed services, not a single model call.**

`[ARCHITECTURE DIAGRAM — insert L200_agent_architecture.png]`

```
Data & Tools   →   AI Gateway   →   Agent + Memory   →   Local Dev   →   Cloud Deploy   →   Evaluate
(Vector Search,    (FMAPI,           (Agents SDK,         (FastAPI,        (Apps, Asset      (MLflow
 Genie, UC)         governance)       Lakebase)            Next.js, uv)     Bundles)          Tracing/Eval)
```

| Layer | What it provides | Service |
|-------|------------------|---------|
| Tools | Search docs, query data | Vector Search, Genie, UC |
| Gateway | Governed, metered LLM access | Foundation Model API + AI Gateway |
| Brain | Reasoning + tool selection loop | OpenAI Agents SDK |
| Memory | Continuity across turns & sessions | Lakebase (Postgres) |
| Runtime | Auth, networking, hosting | Databricks Apps |
| Trust | Observability + quality scoring | MLflow Tracing & Evaluation |

*Speaker note:* Emphasise that **governance is not a layer at the end** — Unity Catalog and AI Gateway wrap every box. That's the Databricks differentiator vs. stitching this together yourself.

---

## Slide 3 — Concept 1: AI Agents & the Agent Loop

**Concept.** An agent is an LLM given *tools* and an *objective*, run in a loop: reason → pick a tool → observe result → reason again → answer. The OpenAI Agents SDK runs this loop; Databricks hosts it.

**Key focus.**
- The model doesn't *answer* immediately — it *decides* whether it needs a tool first.
- System prompt + tool descriptions are the real "programming" of the agent.
- Bounded autonomy: max turns, timeouts, and a clear stop condition.

**Governance.**
- Pin the model (`databricks-claude-sonnet-4-6`) so behaviour is reproducible.
- Tool access = data access — every tool the agent holds is a permission you've granted.
- Run as a **service principal** in prod, not a human identity (least privilege, auditable).

**In production we usually see.**
- Narrow, single-purpose agents beat one "do-everything" agent — easier to evaluate and govern.
- A human-in-the-loop gate for any *write* action (refunds, bookings, record updates).
- Guardrails on prompt + output before the agent is allowed to act.

**Industry examples.**
- *Retail:* post-purchase support agent — looks up an order, checks the returns policy, drafts a resolution; escalates refunds over a threshold to a human.
- *Property:* leasing assistant — answers prospect questions about a unit, pulls live availability, books a viewing.
- *Also seen in:* FSI (a servicing agent that explains a transaction and routes disputes); Manufacturing (a maintenance copilot that diagnoses a fault and raises a work order).

---

## Slide 3b — The Agent Loop (Universal Concept)

> Foundation: Claude Agent SDK — *"How the agent loop works."* The L200 lab runs this same loop via the **OpenAI Agents SDK** with a **Claude model**. The pattern is framework-agnostic — Anthropic's Claude Agent SDK is an alternative way to run the identical loop.

**The loop every agent runs.** On its own an LLM only emits text. The *loop* is what lets it take action and react until the task is done:

1. **Receive** — the prompt + system prompt + tool definitions + conversation so far.
2. **Reason** — the model either answers, or requests one or more tool calls.
3. **Execute** — run the tools, feed the results back to the model.
4. **Repeat** — each cycle is one *turn*; keep looping until there are no tool calls.
5. **Return** — the final answer, with token usage and cost.

**Why it matters / how you bound it.**
- An open-ended prompt could loop forever → cap **max turns** and a **budget**.
- **Permissions** decide which tools may actually run — *tool access = data access*.
- **Hooks** can intercept, audit, or block a tool call before it executes.
- Context **accumulates** across turns → automatic **compaction** summarizes older history.
- **Subagents** run isolated sub-loops with fresh context to keep the main loop lean.

*Speaker note:* This is the engine under Concept 1. Every later building block (AI Search, Genie, MCP, memory) is just a **tool** the model can choose to call inside this loop — and every governance lever above (turns, permissions, hooks) is how you keep an autonomous loop safe in production.

---

## Slide 3c — The Agent Loop in This Workshop

`[DIAGRAM — insert L200_agent_loop.png]`

**How to read it.**
- The agent runs a *loop* — it does not answer in one shot.
- Each turn: **Reason**, then decide whether a tool is needed.
- If yes, it calls a tool **via MCP**: **Vector Search (VSE)**, **Genie**, or **Knowledge Assistant (KA)**.
- The tool result feeds back (**observe**) and the loop **repeats** — one cycle = one turn.
- When no tool is needed, it returns the **final answer**.

**Cross-cutting every turn.**
- **Lakebase** persists conversation memory.
- **Unity Catalog** governs every tool (permissions + lineage).
- **MLflow** traces every step.

*Speaker note:* This is the same universal loop from the previous slide, wired to the lab's actual tools. The model chooses VSE vs Genie vs KA based on the question — semantic/keyword document search, NL-to-SQL over tables, or a managed RAG assistant. (Diagram source: `L200_agent_loop.mmd`.)

---

## Slide 4 — Concept 2: AI Search & Document Retrieval

**Concept.** Retrieval-Augmented Generation: instead of relying on the model's memory, you *retrieve* the right context from your own data and feed it in. **AI Search isn't just vectors** — it spans **semantic** (embedding) search that matches by meaning, **exact keyword / full-text** search for precise terms, and **hybrid** that blends both. The agent picks the mode the query needs.

**Key focus.**
- Match the retrieval mode to the query: **semantic** for natural-language meaning, **exact / keyword** for IDs, SKUs, codes & names, **hybrid** for the best of both.
- Re-rank results for precision; chunking quality and index **freshness** still drive answer quality.
- Always ground the answer in retrieved text and cite it → reduces hallucination.

**Governance.**
- The index lives in Unity Catalog (`catalog.schema.policy_docs_index`) — same ACLs as any table.
- Row/column controls on source documents flow through to what can be retrieved.
- Lineage: you can trace an answer back to the exact document version that produced it.

**In production we usually see.**
- **Hybrid (semantic + keyword) as the default** for enterprise search; exact match for identifiers.
- Metadata filtering (region, language, effective-date, entitlement) layered on top of search.
- Scheduled or trigger-based re-sync (staleness is the #1 complaint); re-rankers to lift precision.

**Industry examples.**
- *Retail:* exact SKU / order lookup **and** semantic search across return policies, warranty terms, and product manuals — one consistent answer across 30 markets.
- *Property:* exact unit / lease ID lookup **and** semantic search across lease agreements, compliance docs, and tenant handbooks — "pet policy and notice period for this block?"
- *Also seen in:* FSI (product disclosures & policy wording); Healthcare (clinical protocol / formulary lookup); Manufacturing (equipment manuals & SOPs on the shop floor).

---

## Slide 5 — Concept 3: Genie & Natural-Language-to-SQL

**Concept.** Genie lets the agent ask a question in plain English against governed tables; Genie translates to SQL, runs it, and returns the result. This is how the agent reasons over **structured** data.

**Key focus.**
- Curate the Genie Space: which tables, good column descriptions, sample queries, certified metrics.
- It's a *semantic* layer over real tables — answers are only as good as the curation.
- Pair quantitative answers (Genie) with qualitative ones (RAG) for a complete assistant.

**Governance.**
- Genie respects Unity Catalog permissions — the agent can only query what the SP is granted.
- Queries are auditable; row-level security and column masking still apply.
- Define "trusted" metrics centrally so the agent doesn't invent its own definition of "active customer."

**In production we usually see.**
- Tight scoping to a curated mart, not the raw lakehouse — accuracy and cost both improve.
- Certified/golden queries for the top 20 business questions.
- Guardrails against unbounded scans (cost) and against exposing PII columns.

**Industry examples.**
- *Retail:* "Top-selling SKUs in EMEA last week vs. the same week last year?" answered live against the sales mart.
- *Property:* "Which buildings have occupancy below 85% and a lease expiring this quarter?" for an asset manager.
- *Also seen in:* FSI (portfolio exposure & risk Q&A); Manufacturing (OEE and yield by line/plant); Healthcare (operational metrics like bed utilisation).

---

## Slide 6 — Concept 4: MCP (Model Context Protocol)

**Concept.** MCP is an **open standard** for connecting agents to tools and data sources. Instead of bespoke integrations, the agent speaks one protocol; Databricks exposes Vector Search and Genie as MCP servers.

**Key focus.**
- Decouples the agent from the tool — swap a data source without rewriting the agent.
- One consistent interface (`/api/2.0/mcp/vector-search/...`, `/api/2.0/mcp/genie/...`).
- `uv run discover-tools` to enumerate what's connectable in the workspace.

**Governance.**
- MCP calls still go through Unity Catalog + the SP's grants — the protocol doesn't bypass security.
- Databricks-managed MCP servers inherit platform auth; self-hosted/external ones need their own review.
- One place to reason about "what can this agent reach" = the declared MCP server list.

**In production we usually see.**
- A small, reviewed catalogue of approved MCP tools rather than ad-hoc connections.
- Mix of Databricks-managed (Genie, Vector Search) and internal (CRM, OMS, ticketing) servers.
- Tool descriptions treated as product surface — they're what the model reads to choose correctly.

**Industry examples.**
- *Retail:* same agent connects Vector Search (policies) + Genie (sales) + an MCP server fronting the order-management system.
- *Property:* agent reaches Genie (portfolio data) + an MCP wrapper around the property-management / CRM system to raise a maintenance ticket.
- *Also seen in:* FSI (MCP to core banking / case systems); Manufacturing (MCP to MES / CMMS); Healthcare (MCP to EHR/scheduling, behind strict controls).

---

## Slide 6b — Managed MCP Servers on Databricks

Pre-built servers Databricks runs for you. Unity Catalog permissions are always enforced; discover them in **workspace → AI Gateway → MCPs**.

| Feature | Managed MCP URL template | What it exposes |
|---|---|---|
| **AI Search** (formerly Vector Search) | `/api/2.0/mcp/ai-search/{catalog}/{schema}/{index_name}` | Semantic + keyword search over a Vector Search index (document retrieval / RAG) |
| **Genie** (all spaces, Beta) | `/api/2.0/mcp/genie` | Natural-language queries across Genie Spaces + UC data (read-only) |
| **Genie Space** (single) | `/api/2.0/mcp/genie/{genie_space_id}` | NL-to-SQL against one curated Genie Space |
| **Unity Catalog Functions** | `/api/2.0/mcp/functions/{catalog}/{schema}/{function_name}` | Invoke registered UC functions (SQL / Python UDFs) as tools |
| **Databricks SQL** | `/api/2.0/mcp/sql` | Execute AI-generated SQL (read-write; for pipeline / data authoring) |

All prefixed with `https://<workspace-hostname>`. The legacy `/api/2.0/mcp/vector-search/...` prefix still works (AI Search is the renamed Vector Search). For on-behalf-of-user auth, each server needs its OAuth scope: `ai-search`, `genie`, `unity-catalog`, `sql`.

---

## Slide 6c — MCP Server Types & Governance

| MCP server type | What it is |
|---|---|
| **Managed** (Databricks-hosted) | Pre-built servers Databricks runs for you — AI Search, Genie, Unity Catalog functions, Databricks SQL. No setup; discover them in AI Gateway → MCPs. |
| **External** | Third-party MCP servers reached through a Databricks-managed proxy, with managed OAuth so credentials are never exposed. |
| **Custom** | Self-hosted MCP servers you deploy as a Databricks App — for your own tools / APIs not covered by the managed set. |
| **Governance** (all three types) | All integrate with the **Unity AI Gateway**: access control, credential management, centralized visibility. UC permissions mean an agent reaches only the tools and data its identity is granted. |

> Source: Databricks docs — [MCP on Databricks](https://docs.databricks.com/aws/en/generative-ai/mcp/) · [Managed MCP servers](https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp).

---

## Slide 7 — Concept 5: AI Gateway & Foundation Model API

**Concept.** Foundation Model API serves the LLMs; AI Gateway is the governed front door — every model call passes through it for auth, rate limiting, cost tracking, and logging.

**Key focus.**
- Centralised access: one endpoint, many models, swap models without app changes.
- Rate limits + payload logging + usage attribution out of the box.
- Decouples "which model" from "how the app calls a model."

**Governance.**
- Per-team/endpoint rate limits and budgets prevent runaway spend.
- Request/response logging gives an audit trail of what was sent to the model.
- Guardrails (PII, safety) and provider fallback configured once, centrally.

**In production we usually see.**
- Cost attribution by team/use-case via the gateway, tied into chargeback.
- A/B or canary across model versions before a full cutover.
- Rate limits as the first line of defence against abuse and cost spikes.

**Industry examples.**
- *Retail:* peak-season (Black Friday) traffic capped per channel so one chatbot can't starve others; spend tracked per brand.
- *Property:* a single governed model endpoint shared across leasing, facilities, and finance assistants, each with its own budget.
- *Also seen in:* FSI (strict PII/safety guardrails + full audit logging); Healthcare (PHI redaction at the gateway); Manufacturing (model fallback for edge/plant continuity).

---

## Slide 8 — Concept 6: Agent Memory with Lakebase

**Concept.** Lakebase is managed Postgres on Databricks. It gives the agent **persistent memory** — conversation history survives across turns *and* across sessions, so the agent has continuity instead of amnesia.

**Key focus.**
- Two stores in the lab: agent memory schema (the loop's context) + chat history (the UI).
- Memory is state you must design: what to keep, for how long, and what to forget.
- OLTP-style, low-latency reads/writes — different workload from the analytical lakehouse.

**Governance.**
- Memory often contains PII → retention policy, deletion/right-to-be-forgotten, access controls.
- Schema-level grants; in prod the **service principal** needs explicit table *and sequence* grants.
- Keep memory inside the governed perimeter (it's in Databricks, not a random external DB).

**In production we usually see.**
- Scoping memory per user/session and applying TTL/summarisation to control growth and risk.
- Separation of short-term (conversation) vs. long-term (durable preferences) memory.
- Treating memory as auditable data, not a black box.

**Industry examples.**
- *Retail:* the agent remembers a shopper's sizes, prior returns reason, and channel preference across visits — without re-asking.
- *Property:* a tenant assistant recalls an open maintenance request and unit context across calls, so the resident never repeats themselves.
- *Also seen in:* FSI (recall a customer's open dispute & disclosures already shown); Healthcare (care-context continuity under strict consent/retention); Manufacturing (technician's recent diagnostics on an asset).

---

## Slide 8b — How the Agent Memory Works in This Lab

> Implementation: `agent_server/utils.py` (`create_session`, `deduplicate_input`) and `Runner.run(agent, messages, session=session)`.

| How memory works | In this workshop — OpenAI Agents SDK + Lakebase |
|---|---|
| **Where it lives** | `AsyncDatabricksSession` (the Databricks OpenAI-Agents session) backed by **Lakebase Postgres**, in schema `agent_openai_memory`. |
| **Keyed by** | A **`session_id` per conversation thread**: a custom `session_id`, else the `conversation_id`, else a freshly generated UUID. |
| **Each turn** | The session loads the **FULL conversation history** for that `session_id` and prepends it to the model input, then writes the new turn back. `get_items()` is called with **no limit**. |
| **Is it compressed?** | **No.** No summarization or truncation — the whole thread is replayed every turn. The OpenAI Agents SDK session **does not auto-compact** (unlike the Claude Agent SDK / Claude Code, which summarizes when context fills). |
| **So in production** | Context grows with the conversation → watch cost, latency, and context-window limits. Manage it yourself: cap history (`get_items(limit=…)`), summarize older turns, or apply TTL / rotate sessions. |

**Two memory layers, don't confuse them.**
- **Agent memory** (`agent_openai_memory`) — the *conversation thread* the model replays each turn (this slide).
- **Chat history** (frontend `ai_chatbot` schema) — what the Next.js UI shows in the sidebar; a separate store.

*Speaker note:* The `deduplicate_input` helper isn't compression — it just avoids re-sending history the client already passed: if the session already holds the thread, only the newest message is sent and the session supplies the rest. The full replay (no summarization) is the key takeaway, and it's exactly why the deck's "design TTL & summarization up front" guidance matters.

---

## Slide 8c — Memory Protocol: Starting a Fresh Chat

`[DIAGRAM — insert L200_memory_fresh.png]`

Communication sequence — **User → Databricks App (OpenAI Agents SDK) → Foundation Model → Lakebase**:

1. User sends the first message (no `session_id` yet).
2. `get_session_id()` finds none → generates a new UUID.
3. App opens the session and calls `get_items(session_id)` on Lakebase.
4. Lakebase returns **empty** — brand-new thread.
5. `deduplicate_input`: no history, so send the full input = `[ first message ]`.
6. App → Foundation Model: system prompt + tools + `[ first message ]`.
7. Model returns the assistant reply.
8. App writes `add_items([ user msg, assistant msg ])` → Lakebase **INSERT** keyed by `session_id`.
9. App returns the reply **+ `session_id`** (`custom_outputs`); the client keeps it to continue later.

---

## Slide 8d — Memory Protocol: Resuming an Existing Chat

`[DIAGRAM — insert L200_memory_existing.png]`

Communication sequence — same participants, with an existing `session_id`:

1. User sends a new message **+ existing `session_id`**.
2. `get_session_id()` uses the provided id.
3. App calls `get_items(session_id)` (inside `deduplicate_input`) → Lakebase returns **N stored items** (thread already has history).
4. App sends **only the newest message** (history is already persisted).
5. `Runner.run` loads the **full history** via `get_items` (**no limit**) → Lakebase returns all N items.
6. The full conversation is **prepended — NO compression / NO summarization**.
7. App → Foundation Model: system prompt + tools + `[ full history ]` + `[ new message ]`.
8. Model returns the assistant reply; App appends `add_items([ new user msg, assistant msg ])`.
9. App returns the reply.

*Speaker note:* The contrast between these two diagrams is the whole memory story — fresh chat starts empty and persists; resuming replays the **entire** thread every turn (which is why context and cost grow, and why you cap/summarise in production).

---

## Slide 8e — Memory in Production: Best Practices as You Scale

- **Cap context** — window history or limit turns / tokens; don't replay everything.
- **Summarize** older turns into a running summary; keep recent turns verbatim.
- **Short-term vs long-term** — separate the conversation thread from durable user facts; fetch long-term memory on demand.
- **Isolate** by user / session / tenant — no cross-user leakage.
- **Retention by design** — TTL, deletion, right-to-be-forgotten; treat memory as PII.
- **Cost control** — prompt-cache the stable prefix; track tokens, latency, and spend per conversation.
- **OLTP hygiene** — index on `session_id`, pool connections, archive / partition as tables grow.
- **Observe & evaluate** — trace memory reads / writes (MLflow); test recall and no cross-session leakage; least-privilege access.

*Speaker note:* These matter most precisely because this lab replays the full thread with no compression — so as conversations and user counts grow, capping context, summarising, isolating tenants, and watching cost/latency are what keep a memory agent viable in production.

---

## Slide 9 — Concept 7: Unity Catalog Governance (the cross-cutting layer)

**Concept.** Unity Catalog is the single governance plane over data, models, documents, functions, and now agent tools. It's not a step in the lab — it's *underneath every step*.

**Key focus.**
- One permission model across tables, vector indexes, Genie, and UC functions.
- Lineage and audit across the whole agent stack, end to end.
- The agent can only ever touch what its identity is granted — by design.

**Governance.**
- Least-privilege grants to the app's service principal (the lab's Step 10 GRANTs).
- Lineage answers "what data did this answer come from?" — essential for trust & audit.
- Tags/classifications (PII, confidential) drive masking and access consistently.

**In production we usually see.**
- A dedicated SP per app with narrowly scoped grants — never broad/admin access.
- Catalog/schema isolation per environment (dev/test/prod).
- Governance reviews before a tool is added to an agent, because tool = access.

**Industry examples.**
- *Retail:* support agent reads returns data but is masked from full payment details; access differs by region for GDPR.
- *Property:* leasing agents see availability and pricing; tenant PII and financials restricted to authorised roles.
- *Also seen in:* FSI (segregation of duties, regulated audit trails); Healthcare (HIPAA-grade PHI controls); Manufacturing (IP protection on process data).

---

## Slide 10 — Concept 8: Local Dev → Production (Asset Bundles, Apps, Service Principals)

**Concept.** Develop and test the full stack on your laptop, then deploy the *same* code to Databricks Apps with one command using Asset Bundles (infrastructure-as-code).

**Key focus.**
- Fast inner loop locally (`uv run start-app`) → high-fidelity outer loop in cloud.
- `databricks.yml` declares the app, env vars, and resource bindings as code.
- `value_from` binds env vars to governed resources (experiment, postgres) — no secrets hard-coded.

**Governance.**
- Identity flips on deploy: **you** locally → **service principal** in prod (the cause of Step 10 grants).
- Bundles = reproducible, reviewable, version-controlled deployments (auditable change).
- Separate dev/prod targets keep blast radius contained.

**In production we usually see.**
- CI/CD pipelines (GitHub Actions) running `bundle deploy` on merge — no manual clicking.
- Environment promotion dev → staging → prod with the same bundle.
- The local-vs-SP permission gap as the #1 "works on my machine" surprise — solved with explicit grants.

**Industry examples.**
- *Retail:* one bundle deploys the same assistant to each regional workspace with region-specific bindings.
- *Property:* a managed-services partner ships agent updates to many client workspaces via versioned bundles.
- *Also seen in:* FSI (change control & approvals baked into CI/CD); Manufacturing (per-plant deployment from one bundle); Healthcare (controlled promotion with validation gates).

---

## Slide 11 — Concept 9: MLflow Tracing & Evaluation

**Concept.** MLflow Tracing records every step the agent takes (prompts, tool calls, retrievals, latency, tokens). MLflow Evaluation scores quality against datasets and scorers so you can improve systematically.

**Key focus.**
- Tracing = the agent's flight recorder: *why* did it answer that, which tools fired?
- Evaluation turns "it feels better" into measured accuracy / relevance / safety.
- Build a regression set so a prompt or model change can't silently degrade quality.

**Governance.**
- Traces are an audit trail of agent behaviour — what was retrieved, what was sent to the model.
- Scorers can encode policy checks (safety, PII leakage, groundedness) as gates.
- Evaluation experiments are tracked in UC for reproducibility and review.

**In production we usually see.**
- Offline eval in CI before deploy + online monitoring of live traffic after.
- Quality dashboards and alerting on regressions, latency, and cost per conversation.
- Human review queues feeding labelled data back into the eval set (flywheel).

**Industry examples.**
- *Retail:* evaluate that the returns agent cites the *correct, current* policy before each peak season.
- *Property:* monitor that the leasing agent never quotes stale availability or pricing — flag and alert on drift.
- *Also seen in:* FSI (prove groundedness & no fabricated advice for audit); Healthcare (safety/PHI-leakage scorers as hard gates); Manufacturing (accuracy of diagnostic guidance).

---

## Slide 12 — Putting It Together: The Production Mental Model

**A trustworthy agent = capability × governance × observability.**

- **Capability:** Agents SDK + MCP tools (Vector Search, Genie) + Memory (Lakebase)
- **Governance:** Unity Catalog + AI Gateway + service-principal least privilege
- **Observability:** MLflow Tracing + Evaluation, in CI and in production

Anti-patterns to avoid:
- One mega-agent with broad access → scope it down, one job per agent.
- RAG index that drifts from source → automate sync.
- Memory with no retention policy → design TTL & deletion up front.
- Deploy by clicking → bundles + CI/CD.
- "Looks fine" → no eval set → measure it.

*Speaker note:* Land the message that Databricks lets a customer assemble all of this **inside one governed platform** instead of stitching five vendors together — that's the strategic story.

---

## Slide 13 — From Lab to Your Industry (Discussion)

**Retail starting points**
- Customer-service / returns assistant · merchandising & sales Q&A · in-store associate copilot · supplier & policy search · post-purchase / order-status concierge.

**Property / Real-estate starting points**
- Leasing & prospect assistant · tenant/resident support · portfolio & asset analytics · facilities/maintenance triage · lease-document Q&A · investor/valuation reporting copilot.

**Pick one use case → map it to the 9 concepts → identify the data, tools, memory, and guardrails it needs.**

| For your chosen use case, answer: | Concept it maps to |
|---|---|
| What documents must it ground on? | RAG / Vector Search |
| What structured questions will it answer? | Genie |
| What systems must it reach? | MCP |
| What must it remember? | Lakebase memory |
| What can it never see or do? | Unity Catalog + guardrails |
| How will we prove it's good? | MLflow Eval |

---

## Slide 14 — Appendix: Same Pattern, More Industries

**The architecture is industry-agnostic — only the data, tools, and guardrails change.**

| Concept | FSI | Manufacturing | Healthcare |
|---|---|---|---|
| Agent loop | Servicing & dispute routing | Maintenance diagnostic copilot | Patient-services / scheduling assistant |
| RAG | Disclosures, policy wording | Equipment manuals, SOPs | Clinical protocols, formulary |
| Genie | Portfolio exposure & risk | OEE, yield by line/plant | Bed utilisation, ops metrics |
| MCP | Core banking / case systems | MES / CMMS | EHR / scheduling (strict controls) |
| AI Gateway | PII/safety guardrails + audit | Model fallback for plant continuity | PHI redaction at the gateway |
| Memory | Open disputes, prior disclosures | Recent asset diagnostics | Care context (consent-bound) |
| Unity Catalog | Segregation of duties, audit | Process-IP protection | HIPAA-grade PHI controls |
| Deploy | Change control in CI/CD | Per-plant from one bundle | Validation gates on promotion |
| MLflow Eval | Groundedness for audit | Diagnostic accuracy | Safety / PHI-leakage gates |

---

## Slide 15 — Next Steps

1. Customise the agent (prompt, tools, model) and redeploy.
2. Run `uv run agent-evaluate` and build custom scorers.
3. Connect your own data — a Genie Space and Vector Search index on real tables/docs.
4. Explore L300: multi-agent orchestration, embeddings-based memory, human-in-the-loop gates, CI/CD.
5. Engage your Databricks account team for an architecture review / tailored workshop.
