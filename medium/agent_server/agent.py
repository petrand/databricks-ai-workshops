
import logging
import os

from agents.mcp import (
    MCPServer,
    MCPServerManager,
    MCPServerStreamableHttp,
    MCPServerStreamableHttpParams,
)
from typing import AsyncGenerator, List

import mlflow
from agents import Agent, Runner, set_default_openai_api, set_default_openai_client
from agents.tracing import set_trace_processors
from databricks_openai import AsyncDatabricksOpenAI
from databricks_openai.agents import McpServer
from fastapi import HTTPException
from mlflow.genai.agent_server import invoke, stream
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)

from agent_server.utils import (
    build_mcp_url,
    create_session,
    deduplicate_input,
    get_session_id,
    get_user_workspace_client,
    init_lakebase_config,
    process_agent_stream_events,
)

logger = logging.getLogger(__name__)

# NOTE: this will work for all databricks models OTHER than GPT-OSS, which uses a slightly different API
set_default_openai_client(AsyncDatabricksOpenAI())
set_default_openai_api("chat_completions")
set_trace_processors([])  # only use mlflow for trace processing
mlflow.openai.autolog()

# GENERATED

NAME = 'my-agent'
SYSTEM_PROMPT = (
    'You are a helpful router assistant for Vicinity Centres. '
    'You have access to tools via MCP servers and must delegate to the right one:\n'
    '- For company policy questions (HR, expenses, code of conduct, travel, leave, '
    'leasing, WHS, IT/security policy, etc.), you have TWO policy tools:\n'
    '  * "Vicinity Knowledge Assistant" — asks the Agent Bricks Knowledge Assistant '
    'and returns a curated, synthesized, cited answer. Prefer this for natural '
    'questions like "what is our policy on...", "am I allowed to...".\n'
    '  * "Vicinity Policy Search" — vector search that returns the raw matching '
    'policy passages from the documents. Use this to find or verify specific source '
    'text, quote exact wording, or when the user asks to see the underlying '
    'documents/chunks.\n'
    '- For questions about foot traffic / how busy a centre is / building '
    'occupancy and visitor counts by date and time, use the "Foot Traffic '
    'Assistant" (Genie) tool.\n'
    'Always pass through the policy IDs and citations the policy tools return.'
)
MODEL = 'databricks-claude-opus-4-6'
MCP_SERVERS = [
    ('Vicinity Policy Search', '/api/2.0/mcp/vector-search/dev/policies/policy_docs_index'),
    ('Foot Traffic Assistant', '/api/2.0/mcp/genie/01f16ee9c4f313fb8841bd033ac15e9b'),
]

# END GENERATED

# Self-hosted MCP server fronting the Agent Bricks Knowledge Assistant. It is
# mounted into this same app (see ka_mcp.py + start_server.py) and reached over
# localhost; no Databricks managed MCP server exists for Knowledge Assistants.
KA_MCP_URL = os.environ.get(
    "KA_MCP_URL",
    f"http://127.0.0.1:{os.environ.get('KA_MCP_PORT', '8765')}/mcp",
)

lakebase_config = init_lakebase_config()

def get_mcp_user_workspace_client():
    # Uncomment the line below to enable on-behalf-of-user authentication
    # return get_user_workspace_client()
    return None

def init_mcp_servers():
    user_workspace_client = get_mcp_user_workspace_client()
    servers: List[MCPServer] = [
        McpServer(
            name=name,
            url=build_mcp_url(url, user_workspace_client),
            workspace_client=user_workspace_client,
        )
        for (name, url) in MCP_SERVERS
    ]
    # Self-hosted Knowledge Assistant MCP server (plain MCP client over localhost,
    # no Databricks OAuth needed since it is served by this same app).
    servers.append(
        MCPServerStreamableHttp(
            name="Vicinity Knowledge Assistant",
            params=MCPServerStreamableHttpParams(url=KA_MCP_URL),
            client_session_timeout_seconds=120,
            cache_tools_list=True,
        )
    )
    return servers

def create_agent(mcp_servers: List[MCPServer]) -> Agent:
    return Agent(
        name=NAME,
        instructions=SYSTEM_PROMPT,
        model=MODEL,
        mcp_servers=mcp_servers,
    )


@invoke()
async def invoke(request: ResponsesAgentRequest) -> ResponsesAgentResponse:
    session_id = get_session_id(request)
    session = None

    if lakebase_config:
        session = create_session(session_id, lakebase_config)
        mlflow.update_current_trace(metadata={"mlflow.trace.session": session_id})

    try:
        mcp_servers = init_mcp_servers()
        async with MCPServerManager(servers=mcp_servers, connect_in_parallel=True) as manager:
            agent = create_agent(manager.active_servers)

            if session:
                messages = await deduplicate_input(request, session)
            else:
                messages = [i.model_dump() for i in request.input]

            result = await Runner.run(agent, messages, session=session)
            return ResponsesAgentResponse(
                output=[item.to_input_item() for item in result.new_items],
                custom_outputs={"session_id": session.session_id} if session else None,
            )
    except Exception as e:
        error_msg = str(e).lower()
        if any(kw in error_msg for kw in ["lakebase", "pg_hba", "postgres", "database instance"]):
            logger.error("Lakebase access error: %s", e)
            raise HTTPException(status_code=503, detail=f"Lakebase unavailable: {e}") from e
        raise


@stream()
async def stream(request: ResponsesAgentRequest) -> AsyncGenerator[ResponsesAgentStreamEvent, None]:
    session_id = get_session_id(request)
    session = None

    if lakebase_config:
        session = create_session(session_id, lakebase_config)
        mlflow.update_current_trace(metadata={"mlflow.trace.session": session_id})

    mcp_servers = init_mcp_servers()
    async with MCPServerManager(servers=mcp_servers, connect_in_parallel=True) as manager:
        agent = create_agent(manager.active_servers)

        if session:
            messages = await deduplicate_input(request, session)
        else:
            messages = [i.model_dump() for i in request.input]

        result = Runner.run_streamed(agent, input=messages, session=session)

        async for event in process_agent_stream_events(result.stream_events()):
            yield event
