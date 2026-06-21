# Fresh Hermes Agent + Hermes WebUI setup

This note documents the clean setup created on 2026-06-20:

- fresh `hermes-agent` clone at `/home/azureuser/workspace/hermes-agent`
- Hermes WebUI repo at `/home/azureuser/workspace/hermes-webui`
- old Oxaide-local runtime state removed from the now-retired legacy Oxaide runtime paths:
  - `/home/azureuser/oxaide/.hermes-oxaide`
  - `/home/azureuser/oxaide/.hermes-oxaide-runtime`

## Official recommended local hookup

Per the upstream Hermes WebUI docs, the recommended way to use WebUI with Hermes Agent is:

1. prefer the repo bootstrap / launcher path first
2. if using Docker, prefer the single-container compose path unless you specifically need split services

Requirements verified on this machine:

- `docker` present
- classic `docker-compose` present at `/usr/local/bin/docker-compose`
- `docker compose` plugin not present

Repo-local `.env` created:

- `UID=1000`
- `GID=1000`
- `HERMES_WORKSPACE=/home/azureuser/workspace`
- `HERMES_WEBUI_AGENT_DIR=/home/azureuser/workspace/hermes-agent`
- `HERMES_WEBUI_PYTHON=/home/azureuser/.hermes/hermes-agent/venv/bin/python`

Recommended local launch from `/home/azureuser/workspace/hermes-webui`:

- `python3 bootstrap.py`

or:

- `./start.sh`

with the intended agent checkout wired through:

- `HERMES_WEBUI_AGENT_DIR=/home/azureuser/workspace/hermes-agent`

and the working interpreter override on this machine:

- `HERMES_WEBUI_PYTHON=/home/azureuser/.hermes/hermes-agent/venv/bin/python`

Verified official upstream launcher outcome on this machine:

- `python3 bootstrap.py --no-browser`
- WebUI ready at `http://localhost:8787`
- health OK at `http://127.0.0.1:8787/health`
- bootstrap log at `/home/azureuser/.hermes/webui/bootstrap-8787.log`

## Validated real backend home + Azure Foundry path

On 2026-06-21, the real Hermes backend home was re-aligned so the actual product pair is:

- WebUI repo: `/home/azureuser/workspace/hermes-webui`
- Agent repo: `/home/azureuser/workspace/hermes-agent`
- Hermes home: `/home/azureuser/.hermes`

Working backend model config now resolves to:

- `provider: azure-foundry`
- `default: gpt-5.4-mini`
- `base_url: https://leewe-mm4i1l65-eastus2.cognitiveservices.azure.com/openai/v1`

Relevant backend env path:

- `/home/azureuser/.hermes/.env`

Presence verified for:

- `AZURE_FOUNDRY_API_KEY`
- `AZURE_FOUNDRY_BASE_URL`

Fresh validation run used:

- `HERMES_HOME=/home/azureuser/.hermes`
- `HERMES_WEBUI_STATE_DIR=/tmp/hermes-webui-final-check`
- `HERMES_WEBUI_PORT=8792`
- `HERMES_WEBUI_AGENT_DIR=/home/azureuser/workspace/hermes-agent`
- `HERMES_WEBUI_PYTHON=/home/azureuser/.hermes/hermes-agent/venv/bin/python`

Validated outcomes on that run:

- WebUI ready at `http://localhost:8792`
- health OK at `http://127.0.0.1:8792/health`
- onboarding status returned:
   - `completed: true`
   - `provider_configured: true`
   - `provider_ready: true`
   - `chat_ready: true`
   - `setup_state: ready`
   - `current_provider: azure-foundry`
   - `current_model: gpt-5.4-mini`

Supported Hermes Agent runtime resolution also verified:

- `provider: azure-foundry`
- `api_mode: codex_responses`
- `auth_mode: api_key`

Important note:

- a raw direct `AIAgent(...).chat(...)` probe previously hit `/chat/completions` with an empty model and returned Azure `400 Missed model deployment`
- the supported runtime resolver for the same backend home now resolves `codex_responses` correctly for the GPT-5 deployment family
- treat the readiness proof and runtime-provider resolution as the authoritative validation path for this setup

Recommended Docker path, if Docker is specifically desired:

- `docker-compose up -d`

Verified working containerized local launch on this machine required:

- building the WebUI image from local source instead of relying on `ghcr.io/nesquena/hermes-webui:latest`
- using alternate host ports because `8642` and `8787` were already occupied

Verified local endpoints after the source build path:

- WebUI healthy at `http://127.0.0.1:28787/health`
- WebUI root at `http://127.0.0.1:28787`

Expected local endpoints:

- WebUI: `http://127.0.0.1:8787`
- Hermes gateway/API: `http://127.0.0.1:8642`

The earlier containerized proof path used:

- named Docker volume `hermes-home`
- named Docker volume `hermes-agent-src`
- shared host workspace mount `/home/azureuser/workspace:/workspace`

Notes:

- The official upstream-first path for this machine should prefer `bootstrap.py` / `start.sh` with `HERMES_WEBUI_AGENT_DIR=/home/azureuser/workspace/hermes-agent`.
- On this machine, the launcher also needs `HERMES_WEBUI_PYTHON=/home/azureuser/.hermes/hermes-agent/venv/bin/python` because the workspace `hermes-agent` checkout does not currently have its own ready local virtualenv.
- The clean clone at `/home/azureuser/workspace/hermes-agent` is the intended source-of-truth checkout for Hermes Agent here.
- The two-container Docker path remains useful for split-service proof and debugging, but it is not the upstream recommended default path.
- Remaining cleanup opportunity: provision a checkout-local `.venv` under `/home/azureuser/workspace/hermes-agent` so `HERMES_WEBUI_PYTHON` can point at the workspace checkout directly instead of the installed Hermes home interpreter.

## Cloudflare container deployment path

For Cloudflare-native deployment, the existing Oxaide production tooling remains the practical path:

- deploy script: `tools/build/deploy-cloudflare-containers-production.mjs`
- validator: `tools/build/validate-cloudflare-containers.mjs`
- runbook: `docs/launch/cloudflare-containers-production-deploy.md`

Important reality:

- this Cloudflare lane deploys the Oxaide worker-routed `/agents` and `/internal/runtime/*` container setup
- it is not the same thing as the stock `hermes-webui` two-container local Docker setup
- current repo progress now points the Oxaide Cloudflare container image path at `../workspace/hermes-webui/Dockerfile` so production can move toward the validated upstream WebUI repo rather than the older `apps/open-webui-oxaide` image wrapper

Required runtime secrets are already referenced by the Oxaide tooling:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `AZURE_OPENAI_API_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `HERMES_API_KEY`
- `HERMES_WEBUI_PASSWORD`

Recommended deploy/validate flow from `/home/azureuser/oxaide`:

- validate secrets/runtime: `bash scripts/with-node22.sh python3 scripts/bitwarden_exec.py --node-env production --require-env HERMES_API_KEY --require-env HERMES_WEBUI_PASSWORD -- node tools/build/validate-cloudflare-containers.mjs`
- deploy with Worker secret sync: `bash scripts/with-node22.sh python3 scripts/bitwarden_exec.py --node-env production --require-env CLOUDFLARE_API_TOKEN --require-env CLOUDFLARE_ACCOUNT_ID --require-env AZURE_OPENAI_API_KEY --require-env STRIPE_SECRET_KEY --require-env STRIPE_WEBHOOK_SECRET --require-env HERMES_API_KEY --require-env HERMES_WEBUI_PASSWORD -- node tools/build/deploy-cloudflare-containers-production.mjs`

## Hooking WebUI to the clean backend

Two practical interpretations exist:

1. **Local clean setup**
   - Run `hermes-webui` via `docker-compose.two-container.yml`
   - This gives a clean Hermes backend and WebUI pair immediately.

2. **Cloudflare-native Oxaide route**
   - Use the existing Oxaide Cloudflare container lane for public `/agents`
   - Keep `/home/azureuser/workspace/hermes-webui` as the clean local/forked control repo for direct Docker/bootstrap use and now also as the intended container build source for the Oxaide worker-routed lane.

## SaaS posture recommendation

Updated product direction:

- `oxaide/` should be marketing site only
- `workspace/hermes-webui/` should be the actual product workspace application
- the long-term product runtime should not depend on the Oxaide app/account shell

Reason:

- upstream Hermes WebUI has optional local password/passkey auth, but it does not ship a full SaaS account/billing/subscription system
- Oxaide contains useful reference patterns for auth/billing, but the updated direction is to avoid long-term dependency on its app shell for workspace access

Practical product decision:

- **Yes**, for a real paid SaaS you should use a real auth layer for the product
- **Yes**, you should use Stripe checkout / portal / subscription state for the product
- **Yes**, you likely need usage tracking / entitlement gating outside raw upstream Hermes WebUI if you want plans, limits, overages, seat control, or admin reporting
- **No**, the long-term product should not depend on the Oxaide app/account shell even if Oxaide remains the marketing site

What upstream Hermes WebUI can handle on its own:

- local password login
- local passkeys / WebAuthn
- workspace sessions, files, chat, profiles, cron, and agent UX

What the product control plane must own in a monetized SaaS:

- user identity
- team/account model
- checkout and billing portal
- subscription status
- plan/feature gating
- usage metering shown to customers
- launch/handoff into the workspace app

In short:

- do **not** try to force upstream Hermes WebUI itself to become the first system of record for SaaS auth + billing
- do **not** rely on the Oxaide app/account shell for long-term product runtime access
- keep Oxaide as marketing and let the product app/control plane own the real SaaS flow

## Caveat about secrets in tracked files

During setup, secret-like values were found in tracked files under `/home/azureuser/oxaide`. Treat those files as sensitive and rotate anything that should not have been committed.