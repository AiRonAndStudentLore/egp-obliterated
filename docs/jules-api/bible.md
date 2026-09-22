# Jules API & CLI Bible

> **Generated:** 2026-09-22 · **Source:** `developers.google.com/jules/api` (last updated 2025-11-10) + `jules.google/docs` (full docs surface, including CLI reference and changelog through 2026-03-09)
>
> **⚠ v2 OBSOLESCENCE WARNING:** The Jules REST API is in **alpha** (`v1alpha`). Per the docs note: *"specifications, API keys, and definitions may change."* Google has shipped model-tier upgrades (Gemini 2.5 → 3 Pro → 3.1 Pro) and new features (CI Fixer, Repoless, Continuous AI) without versioning the API. A `v1`/`v2` may ship before this bible gets re-crawled. Treat endpoint shapes here as **best-effort current behavior** — always re-verify against `developers.google.com/jules/api` before launching production agents.

---

## 1. TL;DR — 5-minute first call

Jules is Google's async coding agent. It runs in a fresh cloud VM, clones your GitHub repo, makes changes, and opens a PR. Two surfaces:

- **REST API** at `https://jules.googleapis.com/v1alpha` — programmatic, async, GitHub-PR-driven
- **Jules Tools CLI** (`npm install -g @google/jules`) — terminal + TUI dashboard

```bash
# Get API key: web app → Settings → API (max 3 keys)
export JULES_API_KEY="..."

# 1. List your connected repos (sources)
curl "https://jules.googleapis.com/v1alpha/sources" \
  -H "X-Goog-Api-Key: $JULES_API_KEY"

# 2. Create a session (a unit of work)
curl "https://jules.googleapis.com/v1alpha/sessions" \
  -X POST -H "Content-Type: application/json" -H "X-Goog-Api-Key: $JULES_API_KEY" \
  -d '{
    "prompt": "Add unit tests for the auth module",
    "sourceContext": {
      "source": "sources/github-myorg-myrepo",
      "githubRepoContext": { "startingBranch": "main" }
    },
    "automationMode": "AUTO_CREATE_PR",
    "title": "Auth tests"
  }'

# 3. Poll session state
curl "https://jules.googleapis.com/v1alpha/sessions/{sessionId}" \
  -H "X-Goog-Api-Key: $JULES_API_KEY"

# 4. Pull activities (plan, progress, completion)
curl "https://jules.googleapis.com/v1alpha/sessions/{sessionId}/activities?pageSize=30" \
  -H "X-Goog-Api-Key: $JULES_API_KEY"
```

---

## 2. Authentication & API keys

- **Generate:** [jules.google.com/settings#api](https://jules.google.com/settings#api) → max 3 keys per account
- **Header:** `X-Goog-Api-Key: <key>` (note: original docs use lowercase `x-goog-api-key`; both work)
- **Security:** Publicly-exposed keys are **auto-disabled** by Google Cloud
- **Rotation:** Delete old keys via Settings; create new ones
- **No OAuth** for API access — only API keys (OAuth is for CLI `jules login` only)

---

## 3. Core concepts

| Resource | What it is | Lifecycle |
|---|---|---|
| **Source** | A connected GitHub repo. Created via the Jules web UI (install Jules GitHub app, pick repos). The API is read-only on sources. | Persistent (until you disconnect) |
| **Session** | A unit of work: one prompt + one source → one PR. Has a `state` machine (see §7). | Created → runs → COMPLETED/FAILED |
| **Activity** | An event within a session (plan generated, message, progress update, completion). | Append-only log |

A session is the unit you create. The Jules VM is provisioned fresh per session, clones the repo, runs your prompt, generates a plan (which you can auto-approve or require explicit approval), executes, and produces a PR.

---

## 4. Plans, concurrency & limits (THE LOAD-BEARING TABLE)

| Plan | Daily Tasks (rolling 24h) | **Concurrent Tasks** | Model Access |
|---|---|---|---|
| **Free** (`Jules`) | 15 | **3** | Gemini 2.5 Pro |
| **Pro** (`Jules in Pro`) | 100 | **15** | Gemini 3 Pro → **Gemini 3.1 Pro** (recently upgraded) |
| **Ultra** (`Jules in Ultra`) | 300 | **60** | Priority access to latest (3 Pro → 3.1 Pro) |

**For Plan D:** User's "15 simultaneous" target = **Pro tier exactly**.

- **Paid plans** require a **Google AI subscription** (Pro or Ultra), currently available **only for individual `@gmail.com` accounts**. Workspace/business upgrade paths pending — interest form at the docs.
- **Family plan pooling:** task limits are NOT shared/pooled; each family member is independent.
- **Hit-the-limit behavior:** new task button disabled, tooltip explains why; existing tasks still manageable.
- **Age requirement:** 18+ (some Google One family members under 18 may lack Jules access).
- **No explicit REST API rate limit** is documented. The bottleneck is concurrent-task slots.

---

## 5. REST endpoint reference

Base: `https://jules.googleapis.com`

### 5.1 Sessions

#### `POST /v1alpha/sessions` — create
**Body:**
| Field | Type | Required | Notes |
|---|---|---|---|
| `prompt` | string | ✅ | Task description |
| `title` | string | – | Optional; auto-generated if omitted |
| `sourceContext` | object | ✅ | `{source: "sources/...", githubRepoContext: {startingBranch: "..."}}`. Omit for repoless sessions. |
| `requirePlanApproval` | bool | – | Default: `false` (auto-approve plans). Set `true` for explicit approval. |
| `automationMode` | enum | – | `AUTOMATION_MODE_UNSPECIFIED` (default) or `AUTO_CREATE_PR` |

**Returns:** full Session object with `name`, `id`, `state: "QUEUED"`, `url`, timestamps.

#### `GET /v1alpha/sessions` — list
Query: `pageSize` (1-100, default 30), `pageToken` (cursor from previous response).

#### `GET /v1alpha/sessions/{sessionId}` — get
Pattern: `^sessions/[^/]+$`. Returns full Session including `outputs[]` if COMPLETED.

#### `POST /v1alpha/sessions/{sessionId}:approvePlan` — approve
Empty body. Required only if `requirePlanApproval: true` was set at create.

#### `POST /v1alpha/sessions/{sessionId}:sendMessage` — message
Body: `{prompt: "..."}`. Empty response. Agent responds in next activity.

### 5.2 Activities

#### `GET /v1alpha/sessions/{sessionId}/activities` — list
Query: `pageSize` (1-100, default 50), `pageToken`, **timestamp filter** (e.g., `?createTime=2026-01-17T00:03:53Z`).

#### `GET /v1alpha/sessions/{sessionId}/activities/{activityId}` — get
Pattern: `^sessions/[^/]+/activities/[^/]+$`. Returns full Activity object.

### 5.3 Sources

#### `GET /v1alpha/sources` — list
Query: `pageSize` (1-100, default 30), `pageToken`, **`filter`** (AIP-160, e.g., `name=sources/github-myorg-myrepo`).

#### `GET /v1alpha/sources/{sourceId}` — get
Pattern: `^sources/.*$`. Returns full Source including `githubRepo.{owner, repo, isPrivate, defaultBranch, branches[]}`.

---

## 6. Session state machine

| State | Meaning |
|---|---|
| `STATE_UNSPECIFIED` | Sentinel |
| `QUEUED` | Waiting to be processed |
| `PLANNING` | Jules is generating the plan |
| `AWAITING_PLAN_APPROVAL` | Plan ready — user must call `:approvePlan` |
| `AWAITING_USER_FEEDBACK` | Agent needs human input |
| `IN_PROGRESS` | Actively working |
| `PAUSED` | Paused |
| `FAILED` | Failed |
| `COMPLETED` | Done |

**Note:** `requirePlanApproval` defaults to `false`. If you don't need approval (batch mode), skip this step. **Auto-approve timer:** if you don't act within the timer's window, the plan auto-approves anyway. So you can poll `state` and not manually approve in most cases.

---

## 7. Activity event types

Every Activity has `originator` (`user`, `agent`, or `system`) and one of these event types:

| Event | Field | Meaning |
|---|---|---|
| `planGenerated` | `plan: {id, steps[]}` | Jules generated a plan |
| `planApproved` | `planId` | User approved |
| `userMessaged` | `userMessage` | User posted in chat |
| `agentMessaged` | `agentMessage` | Jules posted in chat |
| `progressUpdated` | `title, description` | Work in progress |
| `sessionCompleted` | – | Done |
| `sessionFailed` | `reason` | Failed with reason |

**Artifacts** (attached to activities):
- `changeSet` → `{source, gitPatch: {baseCommitId, unidiffPatch, suggestedCommitMessage}}`
- `bashOutput` → `{command, output (stdout+stderr), exitCode}`
- `media` → `{mimeType, data (base64)}`

**PullRequest output** (in Session.outputs):
```json
{ "pullRequest": { "url": "https://github.com/.../pull/N", "title": "...", "description": "..." } }
```

---

## 8. CLI — Jules Tools (`@google/jules`)

### Install
```bash
npm install -g @google/jules
```

### Auth
```bash
jules login    # opens browser, OAuth flow
jules logout
```

### Commands

| Command | Purpose |
|---|---|
| `jules` (no args) | Launch interactive TUI dashboard |
| `jules help` | General help |
| `jules version` | Show installed CLI version |
| `jules --theme light` | TUI theme override (dark/light) |
| `jules remote list --repo` | List connected repositories |
| `jules remote list --session` | List all remote sessions |
| `jules remote new --repo <owner/name> --session "<prompt>"` | Create session |
| `jules remote new --parallel <N>` | Start N parallel sessions for same task |
| `jules remote pull --session <id>` | Pull results from completed session |
| `jules completion bash` | Generate shell autocompletion |

**Inference:** `jules remote new` infers the repo from the current working directory's git remote — you can omit `--repo`.

**Parallel mode:** `--parallel <N>` is the closest thing to "15 concurrent" at the CLI level (CLI just batches N sessions; the real concurrency is still bounded by your plan's concurrent-task slot).

---

## 9. Recent features (changelog highlights)

| Date | Feature |
|---|---|
| 2026-03-09 | Gemini 3.1 Pro available to Pro plan (replaces 3 Pro) |
| recent | **CI Fixer:** Jules auto-detects & fixes failed GitHub Actions on its own PRs (loop: fix → commit → resubmit) |
| recent | **Commit Authoring:** 3 modes — Jules (default), Co-authored, User-only |
| recent | **MCP servers:** Linear, Stitch, Neon, Tinybird, Context7, Supabase |
| 2025-12-10 | Gemini 3 Flash base model for all tiers |
| 2025-12-10 | **Planning Critic:** secondary agent reviews all plans → 9.5% lower failure rate |
| 2025-11-19 | **Performance Optimizations** in Suggested Tasks |
| 2025-11-10 | **Repoless sessions** via REST API — ephemeral VM, no repo needed (Node, Python, Rust, Bun preloaded) |
| 2025-10-03 | Suggested + Scheduled Tasks (Continuous AI) |
| 2025-10-02 | Render integration (auto-fix failed deploys) |
| 2025-09-30 | OAuth2 error handling (CLI) |
| 2025-09-29 | Parallel Task Execution flag (CLI) |
| 2025-09-23 | Initial GA |

**CI Fixer is huge for Plan D:** Jules PRs self-iterate on CI failures without us re-prompting. Means our gate failures posted as PR comments can be addressed by Jules itself in a fix loop.

**Repoless mode** is also huge: we could spawn `POST /v1alpha/sessions` with **no** `sourceContext`, just a prompt, and get an ephemeral VM. Useful for one-off rule generation tasks that don't need our repo.

---

## 10. Errors & failure handling

- **Auto-retry** in-session for: network hiccups, transient install errors, slow dep resolution
- **After multiple retries** → task marked `FAILED`
- **Common failure causes:**
  - Incomplete/missing environment setup scripts
  - Vague or overly broad prompts
  - Nonstandard build systems
  - Long-running processes in setup (e.g., `npm run dev` — **not supported**)
- **Errors surface in:** activity feed (failed step logged) + UI notification badge
- **Manual retry:** "rerun" button in task summary; fix setup script/prompt before restart
- **API errors:** REST returns standard Google API error codes (400, 401, 403, 404, 429, 500). No documented Jules-specific error catalog → assume Google's generic JSON error envelope.

---

## 11. Security & privacy

- **Cloud VM:** isolated, internet-enabled. Treat like public/shared compute.
- **No secrets in repos.** Don't commit API keys/tokens.
- **Private repos NOT used for training.** Explicit in docs.
- **Jules reads non-code files** — review carefully.
- **MCP server scope:** read-only by default, audited tool permissions, hand-vetted initial list (Linear, Stitch, Neon, Tinybird, Context7, Supabase).

---

## 12. What Plan D needs from this bible

| Plan D question | Answer from bible |
|---|---|
| Concurrency target | 15 = **Pro tier** (Pro plan required) |
| Daily capacity | 100 sessions/day = enough for all 1,072 rules + headroom |
| Model selection | **Gemini 3.1 Pro** confirmed available on Pro tier |
| How to spawn a session | `POST /v1alpha/sessions` with `{prompt, sourceContext, automationMode: "AUTO_CREATE_PR"}` |
| PR auto-creation | `AUTO_CREATE_PR` flag at create |
| PR feedback loop | CI Fixer auto-iterates on GitHub Actions failures; or manually post `sendMessage` after reading `changeSet.gitPatch.unidiffPatch` |
| Concurrency under control | Set `requirePlanApproval: false` (auto-approve) so we don't bottleneck on human approval; rely on parallel slot capacity |
| Cost per session | No API cost — Jules is subscription-based; tier covers it |
| Repo requirement | `sourceContext.source = "sources/github-<owner>-<repo>"` — need to connect our EGP repo via web UI first |

**Critical pre-flight for Plan D:**
1. **Connect EGP OBLITERATED repo to Jules web UI** (Settings → Connect GitHub → pick repo) — this creates the source resource
2. **Confirm Pro tier** — 15 concurrent slots needed
3. **Confirm model:** Pro tier gets 3.1 Pro (confirmed via changelog 2026-03-09)

---

## 13. Raw extracts (audit trail)

All source pages saved under `docs/jules-api/raw/`:

- `rest-tree.md` (91KB) — full `/jules/api/reference/rest` subtree crawl
- `jules-docs.md` (4,757 lines) — full `jules.google/docs` crawl (CLI reference, usage-limits, errors, environment, running-tasks, api/reference/types, changelog)
- `auth-and-quickstart.md` — extracted auth + quickstart page from `developers.google.com/jules/api`
- `awesome-list.md` — `github.com/google-labs-code/jules-awesome-list` (mostly GitHub chrome, useful prompts repo)

**Re-crawl recipe:**
```bash
# REST API surface
crwl crawl https://developers.google.com/jules/api/reference/rest \
  --deep-crawl bfs --max-pages 20 -o md-fit -O rest-tree.md

# Jules docs surface (CLI, limits, errors, types)
crwl crawl https://jules.google/docs \
  --deep-crawl bfs --max-pages 25 -o md-fit -O jules-docs.md
```

---

## 14. Open questions for v2 prep

When `v1`/`v2` ships:
- Endpoint paths likely stay similar (`/v1alpha/sessions` → `/v1/sessions`?)
- `automationMode` may gain new values (e.g., `AUTO_MERGE`)
- New event types expected (probably `planCritique`, `ciFixed`)
- Pricing tiers likely expanded; concurrency caps may rise
- Watch for: `automationMode: AUTO_MERGE` and changes to `outputs[]` shape (today: PR only; v2 may include patches, branches, worktree URLs)
