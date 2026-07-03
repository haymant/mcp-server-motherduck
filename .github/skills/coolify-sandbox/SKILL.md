---
name: "coolify-sandbox"
description: "Coolify provider operations for creating, starting, stopping, pausing, reading/writing files, and managing preview URLs in sandbox environments. Core skill used by agents and orchestration layer."
context: "Coolify PaaS (self-hosted) sandbox management"
argument-hint: "Use for all sandbox lifecycle, file I/O, dev server, and code-server operations when sandbox type is 'coolify'"
compatibility: "Coolify v4.x"
user-invocable: false
metadata:
  agent: Orchestrator
  feature: sandbox-connector-coolify
  parent: sandbox-connector-abstraction
---

# Coolify Sandbox Skill

This skill provides the key knowledge and patterns for interacting with **Coolify** as a sandbox provider.

### Core Purpose
Enable agents and the sandbox abstraction layer to:
- Create / connect to isolated development containers
- Start / stop / pause sandboxes
- Execute commands
- Read / write files
- Expose multiple ports with clean preview URLs
- Support code-server (cloud IDE)

---

## 1. Application Lifecycle APIs

### Create Application
- **Primary Endpoint**: `POST /applications/dockerfile` (recommended for custom image)
- Alternative: `POST /applications/public` (for git-based)

**Key Payload Fields**:
```json
{
  "name": "sandbox-session-abc123",
  "image": "your-registry/coolify-sandbox:latest",
  "project_uuid": "proj_xxx",
  "destination_uuid": "dest_xxx",
  "ports_exposes": "3000,1223,1222",
  "domains": "https://sandbox-abc123.yourdomain.com,https://sandbox-abc123-health.yourdomain.com:1222,https://sandbox-abc123-ide.yourdomain.com:1222",
  "env": [
    {"key": "NODE_ENV", "value": "development"},
    {"key": "PORT", "value": "3000"}
  ]
}
```

### Lifecycle Operations

| Action              | Method + Endpoint                              | Notes |
|---------------------|------------------------------------------------|-------|
| **Start**           | `POST /applications/{uuid}/start`              | Starts the container |
| **Stop**            | `POST /applications/{uuid}/stop`               | Graceful stop |
| **Restart**         | `POST /applications/{uuid}/restart`            | Restart container |
| **Pause / Hibernate** | `POST /applications/{uuid}/stop`             | Use stop + snapshot for hibernation |
| **Destroy**         | `DELETE /applications/{uuid}`                  | Permanent deletion |
| **Get State**       | `GET /applications/{uuid}`                     | Returns status, deployments, etc. |
| **Update Config**   | `PATCH /applications/{uuid}`                   | Env, ports, domains, etc. |

---

## 2. Multiple Ports & Preview URLs (Traefik)

Coolify + Traefik natively supports **multiple preview URLs**.

### Best Practice for Multiple Ports

1. Set `ports_exposes`: `"3000,1223,1222"` so the container exposes the needed ports.
2. Use the `IMAGE_PAYLOAD` (heredoc) style when creating applications to explicitly include `domains` as a comma-separated string. This matches the connector examples elsewhere in this document and avoids ambiguity about accepted formats. Example:

```bash
IMAGE_PAYLOAD=$(cat <<JSON
{
  "name": "sandbox-session-$(uuidgen | tr -d '-')",
  "destination_uuid": "${TEST_COOLIFY_DESTINATION_UUID}",
  "server_uuid": "${SERVER_UUID:-${TEST_COOLIFY_SERVER_UUID:-}}",
  "project_uuid": "${TEST_COOLIFY_PROJECT_UUID}",
  "docker_registry_image_name": "your-registry/coolify-sandbox",
  "domains": "https://sandbox-abc123.yourdomain.com,https://sandbox-abc123-health.yourdomain.com:1222,https://sandbox-abc123-ide.yourdomain.com:1222",
  "ports_exposes": "3000,1223,1222",
  "environment_name": "production",
  "health_check_enabled": true,
  "health_check_path": "/health",
  "health_check_port": 1222
}
JSON
)
```

Notes:
- Prefer distinct subdomains (for example `sandbox-abc123-health` and `sandbox-abc123-ide`) rather than relying on a single hostname plus port suffixes, because some Coolify installs normalize domains and can collapse routers.
Important Coolify idiosyncrasy:

- When you supply multiple `domains` on app create, the non-primary (non-head) domains usually must include the explicit ports that match `ports_exposes` (for example `:1222` and `:1223`) so Coolify/Traefik will allocate routers for those ports. However, after provisioning, users should access the preview endpoints without including the port in the browser address bar — Coolify/Traefik will route the hostname on standard HTTPS (443). Example:

  - Payload domains: `https://s10...ac1.h.lizhao.net,https://s10...ac2.h.lizhao.net:1222,https://s10...ac3.h.lizhao.net:1223`
  - Health check URL (access): `https://s10...ac2.h.lizhao.net/health`  (no `:1222` in the browser)
  - IDE (code-server) URL (access): `https://s10...ac3.h.lizhao.net`  (no `:1223` in the browser)

  Note: this is an installation-specific behavior — some Coolify installs map the ported hostnames to the container port internally and do not expose raw TCP on those non-standard ports externally. Always validate reachability from a client (Playwright/curl) after provisioning.
- If your Coolify instance rejects `domains` on create, create the app first and then `PATCH /v1/applications/{uuid}` with a `domains` field (comma-separated string or array depending on the install) — the connector in this repo patches domains when needed.
- Coolify will configure Traefik routers and TLS automatically for domains it manages; using the `IMAGE_PAYLOAD` pattern keeps examples consistent across the skill.

### In Connector (`getRuntimePreviewEnv()`)

Return environment variables inside the sandbox:

```ts
{
  "SANDBOX_URL_3000": "https://sandbox-abc123.yourdomain.com",
  "SANDBOX_URL_1222": "https://sandbox-abc123-health.yourdomain.com:1223",
  "SANDBOX_URL_1223": "https://sandbox-abc123-ide.yourdomain.com:1222"
}
```

**Code-server (Port 1223)** is a first-class citizen — expose it with its own preview URL.

### Implementation notes & caveats (current repo)

- Default code-server port used by the implementation: `CODE_SERVER_PORT = 1222`.
- Lightweight health probe port used by images: `HEALTH_PORT` (default `1223`).
- The connector attempts to set `ports_exposes` and the app `env` `PORT` to the sandbox runtime port so that processes can bind to the platform-provided port.

Important caveat: some Coolify deployments only route the primary hostname (no per-port public routing) or require extra platform configuration to publish non-standard ports externally. In those environments exposing `ports_exposes` does not guarantee an externally routable TCP port for every container port.

Recommended connector behavior when multiple public ports are unreliable:

- Prefer binding your primary HTTP server to the platform-provided `PORT` (posted into the app envs). This ensures Traefik / the primary router will reach your app without relying on extra published ports.
- Provide a lightweight health endpoint inside the image that listens on the `HEALTH_PORT` (default `1222`) so Coolify's probe can validate container readiness. When Coolify supports per-port preview URLs, prefer exposing distinct ports (for example: `3000` app, `1222` health, `1223` code-server). Only consider an internal proxy if the Coolify installation does not publish non-standard ports and you must forward the single externally routed `PORT` to internal services.
- If you rely on distinct preview URLs for code-server or other services, verify that the Coolify instance actually maps `:port` on the public hostname to the container port (see diagnostics below).

When the connector sets runtime envs, ensure the following are present in the application JSON / env list:

- `PORT` — the platform routing port the container should bind to
- Optional `SANDBOX_URL_<port>` keys for user-friendly runtime references

If you control the Coolify installation, prefer enabling Coolify's multiple public port support or a TCP proxy feature so per-port preview URLs work predictably.

## Coolify API: Quickstart & Test

Use the following environment variables (examples are taken from `apps/web/.env`) to operate the Coolify API from a terminal before running the examples below:

```bash
export TEST_COOLIFY_API_KEY="<your-api-key>"
export TEST_COOLIFY_BASE_URL="https://h.lizhao.net/api"
export TEST_COOLIFY_PROJECT_UUID="g5reo4idp5u23fif8nm1ylm2"
export TEST_COOLIFY_SERVER_UUID="ip6w8eqr5r6k6ncujoolhg14"
export TEST_COOLIFY_DESTINATION_UUID="w1091karsnu4qv7zumue9hkk"
export TEST_COOLIFY_DOCKER_IMAGE="haymant/oai"
```

Notes: these values are already present in `apps/web/.env` in this repo for tests; replace `<your-api-key>` with the real key from that file or your environment.

Prerequisites: `curl` and `jq` installed locally.

Prerequisite: server UUID (what the connector does)

The connector code will automatically discover a usable Coolify server by calling `GET /v1/servers` and selecting the first server object that has a `uuid` and whose `settings.is_usable` is not `false`. When you call the Coolify API manually you must supply `server_uuid` (the platform may return a validation error if it's missing).

Example — list servers and extract a usable `server_uuid`:

```bash
curl -s -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" "${TEST_COOLIFY_BASE_URL}/v1/servers" | jq .

# Quick extract first usable uuid
SERVER_UUID=$(curl -s -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" \
  "${TEST_COOLIFY_BASE_URL}/v1/servers" | jq -r '.[] | select(.uuid and (.settings.is_usable != false)) | .uuid' | head -n1)
echo "Using server uuid: $SERVER_UUID"
```

If you prefer the connector to choose the server for you, call the connector-level APIs in this repo (it calls `getCoolifyServerUuid()` internally). When calling the Coolify HTTP API directly, include `server_uuid` in the create payload to avoid validation errors.

1) Create an application

Connector-style image flow (preferred; matches connector in this repo):

```bash
# Safely split image into name/tag. If no tag is present, IMAGE_TAG will be empty.
IMAGE="${TEST_COOLIFY_DOCKER_IMAGE}"
if [[ "$IMAGE" == *:* ]]; then
  IMAGE_NAME="${IMAGE%:*}"
  IMAGE_TAG="${IMAGE##*:}"
else
  IMAGE_NAME="$IMAGE"
  IMAGE_TAG=""
fi

# Build payload without tag first, then add tag only if present to avoid invalid reference formats
IMAGE_PAYLOAD=$(cat <<JSON
{
  "name": "sandbox-session-$(uuidgen | tr -d '-')",
  "destination_uuid": "${TEST_COOLIFY_DESTINATION_UUID}",
  "server_uuid": "${SERVER_UUID:-${TEST_COOLIFY_SERVER_UUID:-}}",
  "project_uuid": "${TEST_COOLIFY_PROJECT_UUID}",
  "server_uuid": "${TEST_COOLIFY_SERVER_UUID}",
  "docker_registry_image_name": "${IMAGE_NAME}",
  "domains": "https://s10a7wk9g8s5745czr2vdtac1.h.lizhao.net,https://s10a7wk9g8s5745czr2vdtac2.h.lizhao.net:1222,https://s10a7wk9g8s5745czr2vdtac3.h.lizhao.net:1222",
  "ports_exposes": "3000,1223,1222",
  "environment_name": "production",
  "health_check_enabled": true,
  "health_check_path": "/health",
  "health_check_port": 1222
}
JSON
)

if [ -n "$IMAGE_TAG" ]; then
  IMAGE_PAYLOAD=$(jq --arg tag "$IMAGE_TAG" '. + {docker_registry_image_tag: $tag}' <<< "$IMAGE_PAYLOAD")
fi

APP_JSON=$(curl -s -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$IMAGE_PAYLOAD" \
  "${TEST_COOLIFY_BASE_URL}/v1/applications/dockerimage")

APP_UUID=$(echo "$APP_JSON" | jq -r '.uuid // .id')
echo "Created app: $APP_UUID"
```


2) Start the application and wait for a healthy deployment:

```bash
curl -s -X POST -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" "${TEST_COOLIFY_BASE_URL}/v1/applications/${APP_UUID}/start"

# Poll for readiness (look for deployments and preview URLs)
for i in $(seq 1 30); do
  APP=$(curl -s -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" "${TEST_COOLIFY_BASE_URL}/v1/applications/${APP_UUID}")
  SANDBOX_URL_1222=$(echo "$APP" | jq -r '.env[]? | select(.key=="SANDBOX_URL_1222") | .value' 2>/dev/null || true)
  if [ -n "$SANDBOX_URL_1222" ]; then
    echo "Found SANDBOX_URL_1222: $SANDBOX_URL_1222"; break
  fi
  sleep 2
done

# If SANDBOX_URL_1222 was published, probe health
if [ -n "$SANDBOX_URL_1222" ]; then
  curl -I --max-time 5 "$SANDBOX_URL_1222/health" || echo "health probe failed"
else
  echo "No per-port preview URL published; check application JSON for routing info:"
  echo "$APP" | jq '.'
fi
```

3) Fetch deployments and logs (example):

```bash
DEPLOYMENTS=$(curl -s -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" "${TEST_COOLIFY_BASE_URL}/v1/applications/${APP_UUID}/deployments")
DEPLOY_UUID=$(echo "$DEPLOYMENTS" | jq -r '.[0].uuid // .[0].id')
echo "Latest deployment: $DEPLOY_UUID"

# Try to fetch logs for the deployment (endpoint may vary by Coolify install)
curl -s -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" "${TEST_COOLIFY_BASE_URL}/v1/applications/${APP_UUID}/deployments/${DEPLOY_UUID}/logs" | jq -r '.[]?.message' || echo "No logs or endpoint not available"
```

4) Stop and destroy when done:

```bash
curl -s -X POST -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" "${TEST_COOLIFY_BASE_URL}/v1/applications/${APP_UUID}/stop"
curl -s -X DELETE -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" "${TEST_COOLIFY_BASE_URL}/v1/applications/${APP_UUID}"
```

These steps give a minimal, testable flow that a developer or CI job can follow to validate the Coolify connector behavior (ports_exposes, `PORT` env, and health probe response on `SANDBOX_URL_1222`).

5) List all applications (for cleanup or debugging):

```bash
APPS=$(curl -s -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" \
  "${TEST_COOLIFY_BASE_URL}/v1/applications" | jq -r '.[] | "\(.uuid // .id)\t\(.name)"' | cut -f1)  
```

5) Pull and push updates (example):

```bash
# Pull current config
APP=$(curl -s -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" "${TEST_COOLIFY_BASE_URL}/v1/applications/${APP_UUID}")
echo "Current config: $APP"
# Update env vars (example: add FOO=bar)
UPDATED_APP=$(echo "$APP" | jq '.env += [{"key": "FOO", "value": "bar"}]')
curl -s -X PATCH -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$UPDATED_APP" \
  "${TEST_COOLIFY_BASE_URL}/v1/applications/${APP_UUID}"
echo "Updated config: $(curl -s -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" "${TEST_COOLIFY_BASE_URL}/v1/applications/${APP_UUID}")"
```

6) Restart the application:

```bash
curl -s -X POST -H "Authorization: Bearer ${TEST_COOLIFY_API_KEY}" "${TEST_COOLIFY_BASE_URL}/v1/applications/${APP_UUID}/restart"
```