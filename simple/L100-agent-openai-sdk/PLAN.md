# Plan: Simplified L100 Agent Package

## What Was Done

Created `simple/L100-agent-openai-sdk/` as a simplified version of `L100-agent-openai-agents-sdk/` for business-developers and data-engineers with low agent maturity.

## Deployed App

- **App Name**: `db-workshopp-l100-agent`
- **URL**: https://db-workshopp-l100-agent-7474646098113792.aws.databricksapps.com
- **Service Principal**: `app-15svjw db-workshopp-l100-agent` (ID: 71644186469866)
- **Status**: RUNNING (but needs AI Gateway permission — see below)

## Remaining: AI Gateway Permission

The app's service principal needs `CAN_QUERY` on `workshop-ai-endpoint`. Run:

```bash
databricks api patch /api/2.0/permissions/serving-endpoints/workshop-ai-endpoint \
  --json '{"access_control_list": [{"service_principal_name": "app-15svjw db-workshopp-l100-agent", "all_permissions": [{"permission_level": "CAN_QUERY"}]}]}'
```

Or via Databricks UI: Serving → workshop-ai-endpoint → Permissions → Add SP with Can Query.

## Folder Structure

```
simple/L100-agent-openai-sdk/
├── agent_server/          # UNCHANGED from original
│   ├── __init__.py
│   ├── agent.py           # OpenAI Agents SDK + MCP servers
│   ├── start_server.py    # MLflow AgentServer (FastAPI)
│   ├── evaluate_agent.py  # Embedded evaluation
│   └── utils.py           # Helpers
│
├── scripts/               # 4 scripts (removed grant_lakebase_permissions.py)
│   ├── quickstart.py
│   ├── start_app.py
│   ├── discover_tools.py
│   └── preflight.py
│
├── .claude/skills/        # 7 skills (removed 5 advanced ones)
│   ├── quickstart/
│   ├── run-locally/
│   ├── deploy/
│   ├── discover-tools/
│   ├── add-tools/
│   ├── create-tools/
│   └── modify-agent/
│
├── pyproject.toml         # Python deps & entry points
├── databricks.yml         # DAB config (app name: db-workshopp-l100-agent)
├── app.yaml               # Standalone app config
├── .env.example           # Environment template
├── .gitignore
├── README.md              # Simplified walkthrough
├── AGENTS.md              # Claude Code quick reference
└── CLAUDE.md              # Points to AGENTS.md
```

## What Was Removed vs Original

| Removed | Reason |
|---------|--------|
| `.github/workflows/deploy.yml` | CI/CD too advanced for audience |
| `scripts/grant_lakebase_permissions.py` | Lakebase not in scope |
| `supervisor-api/` skill | Advanced orchestration |
| `supervisor-api-background-mode/` skill | Advanced |
| `long-running-server/` skill | Background task infra |
| `load-testing/` skill | Performance benchmarking |
| `migrate-from-model-serving/` skill | Irrelevant for new users |

## Key Differences

| Aspect | Original | Simplified |
|--------|----------|-----------|
| Skills | 12 | 7 |
| Scripts | 5 | 4 |
| CI/CD | GitHub Actions | None |
| README | Technical deep-dive | 3-step walkthrough |
| Target | Experienced devs | Business-devs, data engineers |
| Evaluation | Embedded + notebook | Points to notebook only |

## Testing the Deployed App

```bash
# Get OAuth token
TOKEN=$(databricks auth token | jq -r '.access_token')

# Test the agent
curl -X POST https://db-workshopp-l100-agent-7474646098113792.aws.databricksapps.com/invocations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input": [{"role": "user", "content": "hi"}]}'
```

## Resources in databricks.yml

- MLflow Experiment: `1906606050275437`
- Genie Space: `01f149bc27281790b7ee970134092bf7` (FreshMart Retail Data)
