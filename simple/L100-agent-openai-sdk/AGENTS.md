# Agent Development with Claude Code

## First Time? Start Here

```bash
uv run quickstart
```

This handles authentication, environment setup, and MLflow experiment creation.

## Common Tasks

| What you want to do | Skill to use | Command |
|---------------------|-------------|---------|
| Set up for the first time | `/quickstart` | `uv run quickstart` |
| Run the agent locally | `/run-locally` | `uv run start-app` |
| See what tools are available | `/discover-tools` | `uv run discover-tools` |
| Add a new tool | `/add-tools` | Edit `agent.py` + `databricks.yml` |
| Create a new Databricks resource | `/create-tools` | Via SDK or CLI |
| Change the model or system prompt | `/modify-agent` | Edit `agent.py` |
| Deploy to Databricks | `/deploy` | `databricks bundle deploy && databricks bundle run agent_openai_agents_sdk` |

## Key Files

| File | Purpose |
|------|---------|
| `agent_server/agent.py` | Agent logic — model, system prompt, MCP servers |
| `agent_server/start_server.py` | FastAPI server + MLflow tracing |
| `databricks.yml` | Deployment configuration and resource permissions |
| `.env` | Local environment variables |

## Quick Commands

```bash
uv run quickstart          # First-time setup
uv run start-app           # Start agent + chat UI
uv run start-server        # Start agent server only (port 8000)
uv run discover-tools      # Find available workspace resources
uv run preflight           # Pre-deploy health check
uv run agent-evaluate      # Run evaluation suite locally
```

## Deploying

```bash
# Pre-flight check
uv run preflight

# Deploy and start
databricks bundle deploy
databricks bundle run agent_openai_agents_sdk

# View logs
databricks apps logs <app-name> --follow
```

**Important:** Always include `--profile <profile>` in CLI commands if you have multiple profiles. Check `.env` for `DATABRICKS_CONFIG_PROFILE`.

## Evaluating Your Agent

Run `02_agent_evaluation.ipynb` in the parent folder (Databricks notebook) for the full evaluation suite with MLflow scorers.

For quick local evaluation: `uv run agent-evaluate`

## Adding Tools

1. Add MCP server in `agent_server/agent.py` → `MCP_SERVERS` list
2. Grant permissions in `databricks.yml` → `resources` section
3. Deploy with `databricks bundle deploy`

See the `/add-tools` skill for YAML examples and the `/create-tools` skill if the resource doesn't exist yet.
