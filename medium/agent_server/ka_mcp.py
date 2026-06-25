"""Self-hosted MCP server that fronts the Agent Bricks Knowledge Assistant.

Databricks does not provide a managed MCP server for Knowledge Assistants, so we
host one here as part of this app: a small FastMCP server with a single tool that
proxies the KA's serving endpoint. It runs in a background thread on a localhost
port (so it does not depend on the host app's lifespan), and the router consumes
it over MCP at ``http://127.0.0.1:<port>/mcp`` (see ``agent.py``).
"""

import logging
import os
import threading

from databricks.sdk import WorkspaceClient
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# The Agent Bricks Knowledge Assistant serving endpoint to proxy.
KA_SERVING_ENDPOINT = os.environ.get("KA_SERVING_ENDPOINT", "ka-a9d02891-endpoint")
# Localhost port the in-app MCP server listens on (internal to the app only).
KA_MCP_PORT = int(os.environ.get("KA_MCP_PORT", "8765"))

mcp = FastMCP("vicinity-knowledge-assistant", host="127.0.0.1", port=KA_MCP_PORT)


@mcp.tool()
def ask_policy_assistant(question: str) -> str:
    """Ask the Vicinity Centres policy Knowledge Assistant a question.

    The Knowledge Assistant (Agent Bricks) answers strictly from the Vicinity
    Centres company policy documents and returns a grounded, cited answer. Use
    this for questions about company policies (HR, expenses, leasing, WHS,
    security, compliance, sustainability, IT/security, etc.).

    Args:
        question: The natural-language policy question to ask.

    Returns:
        The assistant's grounded answer text.
    """
    w = WorkspaceClient()
    resp = w.api_client.do(
        "POST",
        f"/serving-endpoints/{KA_SERVING_ENDPOINT}/invocations",
        body={"input": [{"role": "user", "content": question}]},
    )
    output = resp.get("output", []) if isinstance(resp, dict) else []
    text = "".join(
        seg.get("text", "")
        for item in output
        for seg in (item.get("content") or [])
        if isinstance(item.get("content"), list)
    )
    return text or "No answer returned by the Knowledge Assistant."


_started = False
_lock = threading.Lock()


def start_in_background() -> None:
    """Start the FastMCP streamable-HTTP server in a daemon thread (idempotent)."""
    global _started
    with _lock:
        if _started:
            return
        _started = True

    def _run() -> None:
        try:
            # Blocking; serves the MCP over streamable HTTP at /mcp.
            mcp.run(transport="streamable-http")
        except Exception as e:  # pragma: no cover - defensive
            logger.error("Knowledge Assistant MCP server crashed: %s", e)

    threading.Thread(target=_run, name="ka-mcp-server", daemon=True).start()
    logger.info(
        "Knowledge Assistant MCP server starting on http://127.0.0.1:%s/mcp",
        KA_MCP_PORT,
    )
