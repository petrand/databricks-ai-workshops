import asyncio
import logging
from pathlib import Path

from databricks_openai.agents.session import AsyncDatabricksSession
from dotenv import load_dotenv
from mlflow.genai.agent_server import AgentServer, setup_mlflow_git_based_version_tracking

from agent_server.utils import init_lakebase_config

logger = logging.getLogger(__name__)

# Load env vars from .env before importing the agent for proper auth
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)


async def _ensure_lakebase_tables() -> None:
    config = init_lakebase_config()
    if not config:
        return
    try:
        session = AsyncDatabricksSession(
            session_id="__startup__",
            instance_name=config.instance_name,
            autoscaling_endpoint=config.autoscaling_endpoint,
            project=config.autoscaling_project,
            branch=config.autoscaling_branch,
            schema=config.memory_schema,
        )
        await session._ensure_tables()
        logger.info("Lakebase tables ready (schema: %s)", config.memory_schema)
    except Exception as e:
        logger.warning("Could not create Lakebase tables at startup: %s", e)


# Need to import the agent to register the functions with the server
import agent_server.agent  # noqa: E402

agent_server = AgentServer("ResponsesAgent", enable_chat_proxy=True)
# Define the app as a module level variable to enable multiple workers
app = agent_server.app  # noqa: F841
setup_mlflow_git_based_version_tracking()

# --- Self-hosted Knowledge Assistant MCP server (runs in a background thread) ---
# Databricks has no managed MCP server for Agent Bricks Knowledge Assistants, so
# we host one here (see agent_server/ka_mcp.py). It listens on a localhost port
# and the router consumes it over MCP (see agent.py). Running it in a daemon
# thread keeps it independent of this app's ASGI lifespan.
from agent_server import ka_mcp  # noqa: E402

ka_mcp.start_in_background()

# Run table creation at startup
try:
    asyncio.run(_ensure_lakebase_tables())
except Exception as e:
    logger.warning("Lakebase table setup deferred: %s", e)


def main():
    agent_server.run(app_import_string="agent_server.start_server:app")
