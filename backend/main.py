"""
Vercel ASGI entry point for the MotherDuck MCP server.

This module exposes the MotherDuck MCP server over Streamable HTTP,
wrapped with Bearer-token authentication, ready to be deployed on Vercel's
Python runtime.

The client's `Authorization: Bearer <token>` header carries the MotherDuck
access token — there is no separate API key.  The server extracts it from
each request and passes it to DuckDB's MotherDuck connector.

Environment variables:

  MCP_DB_PATH                  – Database path (default ":memory:").
  MCP_READ_WRITE               – Set to "1" to enable write access.
  MCP_MAX_ROWS                 – Max rows per query (default "1024").
  MCP_MAX_CHARS                – Max chars per query result (default "50000").
  MCP_QUERY_TIMEOUT            – Query timeout in seconds (default "-1").
  MCP_INIT_SQL                 – SQL to run on startup.
  MCP_ALLOW_SWITCH_DATABASES   – Set to "1" to enable switch_database_connection.
  MCP_SAAS_MODE                – Set to "1" for MotherDuck SaaS mode.
  MCP_EPHEMERAL_CONNECTIONS    – Set to "0" to disable ephemeral connections.
  MCP_MOTHERDUCK_CONNECTION_PARAMETERS – Additional MotherDuck connection params.
  AWS_ACCESS_KEY_ID            – AWS access key for S3 connections.
  AWS_SECRET_ACCESS_KEY        – AWS secret key for S3 connections.
  AWS_SESSION_TOKEN            – AWS session token.
  AWS_DEFAULT_REGION           – AWS region.
"""

import contextvars
import os

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from mcp_server_motherduck.server import create_mcp_server

# CORS headers applied to every response so browser-based MCP clients
# (Inspector, etc.) can read error responses too.
CORS_HEADERS = {
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET, POST, DELETE, OPTIONS",
    "access-control-allow-headers": "*",
    "access-control-max-age": "86400",
}

# Per-request (per-async-context) MotherDuck token extracted from the
# Authorization header.  The DatabaseClient reads this when connecting.
_request_motherduck_token: contextvars.ContextVar[str] = contextvars.ContextVar(
    "_request_motherduck_token"
)


def get_request_motherduck_token() -> str:
    """Return the MotherDuck token supplied by the current request, or ''."""
    return _request_motherduck_token.get("")


def _add_cors_headers(response: Response) -> Response:
    """Return a new Response with CORS headers added."""
    for key, value in CORS_HEADERS.items():
        response.headers.setdefault(key, value)
    return response


# ---------------------------------------------------------------------------
# Bearer token auth middleware
# ---------------------------------------------------------------------------
class BearerAuthMiddleware:
    """Extract the MotherDuck token from the Authorization: Bearer header
    and add CORS headers to every response.

    The Bearer token *is* the MotherDuck token — there is no separate API key.
    The middleware stores it in a context variable (and as a fallback in
    ``os.environ["MOTHERDUCK_TOKEN"]``) so the downstream DatabaseClient can
    pick it up when connecting.

    Requests without a Bearer token receive a 403 response.  OPTIONS (CORS
    preflight) returns 204.  **Every** HTTP response — including errors from
    the inner app such as 405 — is intercepted and decorated with CORS headers
    so browser-based MCP clients (Inspector, etc.) can always read them.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Handle CORS preflight — return 204 with CORS headers immediately.
        if scope.get("method", "").upper() == "OPTIONS":
            response = Response(status_code=204)
            _add_cors_headers(response)
            await response(scope, receive, send)
            return

        # Extract and validate Bearer token (required for all non-OPTIONS).
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode()

        if not auth_header.startswith("Bearer "):
            from starlette.responses import PlainTextResponse

            response = PlainTextResponse(
                "Forbidden: missing MotherDuck token in Authorization header",
                status_code=403,
            )
            _add_cors_headers(response)
            await response(scope, receive, send)
            return

        md_token = auth_header[7:]

        # Store in context var (async-safe) and env var (fallback for
        # DuckDB/DatabaseClient).
        _request_motherduck_token.set(md_token)
        os.environ["MOTHERDUCK_TOKEN"] = md_token

        # Intercept the inner app's response to inject CORS headers on
        # every response (including 405, 500, etc.).
        async def send_with_cors(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers_list = list(message.get("headers", []))
                for key, value in CORS_HEADERS.items():
                    key_bytes = key.encode("latin-1")
                    # Don't duplicate if the inner app already set it
                    if not any(k.lower() == key_bytes for k, _ in headers_list):
                        headers_list.append((key_bytes, value.encode("latin-1")))
                message["headers"] = headers_list
            await send(message)

        await self.app(scope, receive, send_with_cors)


# ---------------------------------------------------------------------------
# Helper: parse boolean-ish env var
# ---------------------------------------------------------------------------
def _env_bool(key: str, default: str = "0") -> bool:
    return os.environ.get(key, default).strip().lower() in ("1", "true", "yes")


def _env_int(key: str, default: str) -> int:
    try:
        return int(os.environ.get(key, default).strip())
    except (ValueError, TypeError):
        return int(default)


# ---------------------------------------------------------------------------
# Create the MotherDuck MCP server
# ---------------------------------------------------------------------------
mcp = create_mcp_server(
    db_path=os.environ.get("MCP_DB_PATH", ":memory:"),
    motherduck_token=None,  # Token comes per-request via BearerAuthMiddleware
    # Vercel's serverless runtime may not set HOME; fall back to /tmp
    home_dir=os.environ.get("HOME") or "/tmp",
    saas_mode=_env_bool("MCP_SAAS_MODE"),
    read_only=not _env_bool("MCP_READ_WRITE"),
    ephemeral_connections=_env_bool("MCP_EPHEMERAL_CONNECTIONS", "1"),
    max_rows=_env_int("MCP_MAX_ROWS", "1024"),
    max_chars=_env_int("MCP_MAX_CHARS", "50000"),
    query_timeout=_env_int("MCP_QUERY_TIMEOUT", "-1"),
    init_sql=os.environ.get("MCP_INIT_SQL"),
    allow_switch_databases=_env_bool("MCP_ALLOW_SWITCH_DATABASES"),
    motherduck_connection_parameters=os.environ.get(
        "MCP_MOTHERDUCK_CONNECTION_PARAMETERS",
        "session_hint=mcp&dbinstance_inactivity_ttl=0s",
    ),
)

# ---------------------------------------------------------------------------
# Expose over Streamable HTTP as an ASGI app.
#
# The MCP protocol endpoint lives at `/mcp`. Vercel's Python runtime
# auto-detects the module-level `app` callable and serves it.
#
# `stateless_http=True` is required for serverless: each request is
# self-contained so the server does not need an in-memory session across
# cold starts.
# ---------------------------------------------------------------------------
app = mcp.http_app(
    path="/mcp",
    stateless_http=True,
)

# Add permissive CORS so browser-based MCP clients (Inspector, etc.) can
# reach the endpoint.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["mcp-session-id"],
)

# Wrap with Bearer token auth (checked against MCP_API_KEY env var).
app = BearerAuthMiddleware(app)  # type: ignore[assignment]


def main() -> None:
    """Run the server locally over stdio (for Claude Desktop, `uv run`, etc.)."""
    print("Starting MotherDuck MCP server (stdio)...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
