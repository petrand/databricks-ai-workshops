# Build Production Scale Governed AI Agents in Databricks

> A practical guide to building production-ready AI agents — not toy demos. From zero to deployed, with evaluation, governance, and monitoring baked in from day one.

---

## Choose Your Level

| Level | What You'll Build | Duration | Get Started |
|-------|-------------------|----------|-------------|
| **[Simple (L100)](./simple/)** | AI agent using managed Databricks services — Genie, Vector Search, Playground, managed agents. No custom code required. | ~3 hours | [Lab Guide](./simple/LAB_GUIDE.md) |
| **[Medium (L200)](./medium/)** | Custom agent with OpenAI Agents SDK, MCP tools, Lakebase memory, and full-stack chat UI deployed as a Databricks App. | ~4 hours | [Workspace Guide](./medium/lab_instructions/SETUP_GUIDE_WORKSPACE_ONLY.md) |
| **[Advanced (L300)](./advanced/)** | Production-grade LangGraph agent with MCP, persistent memory, streaming UI, and comprehensive evaluation suite. | 2 days | [Local Guide](./advanced/WORKSHOP_INSTRUCTIONS.md) / [Workspace Guide](./advanced/WORKSHOP_INSTRUCTIONS_WORKSPACE.md) |

---

## Data Setup (Required First)

**You must create your dataset before starting any workshop level.** All levels depend on structured data tables, chunked documents, a Vector Search index, and a Genie Space being provisioned first.

| Method | Best for | Instructions |
|--------|----------|--------------|
| **Workspace notebook** | Workshop attendees, workspace-only users | Run `data/workspace_setup_script/01_quickstart_setup.py` as a notebook (select catalog + schema > Run All) |
| **Local CLI scripts** | Local development, CI/CD automation | See [`data/README.md`](./data/README.md) |

The setup creates: data tables, chunked policy documents, a Vector Search index, a Genie Space, and an MLflow experiment (~10-15 minutes).

> **Note:** The Simple (L100) and Medium (L200) workspace guides include data setup as their first step. For Advanced (L300) local development, run the scripts in `data/local_cli_setup_script/` separately.

---

## What You'll Learn

Every level follows the same agent lifecycle:

1. **Build** — Connect LLMs to your data using tools (Genie, Vector Search, UC Functions, MCP)
2. **Evaluate** — MLflow tracing, automated LLM judges, prompt iteration
3. **Govern** — AI Gateway, Unity Catalog permissions, guardrails
4. **Deploy** — Databricks Apps with service principals and observability
5. **Improve** — Human-in-the-loop feedback, labelling sessions, continuous iteration

---

## Quick Start

```bash
git clone https://github.com/AnanyaDBJ/databricks-ai-workshops.git
cd databricks-ai-workshops
```

Then open the **Get Started** link for your chosen level above.

---

## Repository Structure

```
simple/          L100 — Managed services, no custom code
medium/          L200 — Custom agent with memory (OpenAI Agents SDK + Lakebase)
advanced/        L300 — Full custom stack (LangGraph + MCP + React UI)
data/            Shared setup scripts and synthetic data generation
```

See [`data/README.md`](./data/README.md) for details on the data setup that powers all levels.

---

## Why This Exists

There are plenty of "hello world" agent demos. What's missing is the hard part — evaluation, governance, monitoring, and the operational rigor that separates a prototype from a product.

These workshops teach you to build agents that are **tested, governed, observable, and continuously improving.**
