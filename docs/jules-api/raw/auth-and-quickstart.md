# Jules API — Auth & Quickstart
Source: https://developers.google.com/jules/api
Last updated: 2025-11-10

## Introduction
The Jules API lets you programmatically access Jules's capabilities to automate and enhance your software development lifecycle. Use the API to create custom workflows, automate tasks like bug fixing and code reviews, and embed Jules's intelligence directly into the tools you use every day, such as Slack, Linear, and GitHub.

**Note:** The Jules API is in an **alpha release** — experimental. Specifications, API keys, and definitions may change. At least one stable + one experimental version will be maintained in the future.

## Authentication

### Generate API Key
- Web app → [Settings](https://jules.google.com/settings#api) → create new API key
- **Max 3 API keys per account**

### Use API Key
- Header: `X-Goog-Api-Key: YOUR_API_KEY`
- **Keep secure.** Publicly exposed keys are [automatically disabled](https://cloud.google.com/resource-manager/docs/organization-policy/restricting-service-accounts#disable-exposed-keys).

## API Concepts (Core Resources)

| Resource | Purpose |
|---|---|
| **Source** | Input source for the agent (e.g., GitHub repo). Must install Jules GitHub app first via [jules.google/docs](https://jules.google/docs). |
| **Session** | Continuous unit of work within a specific context (like a chat session). Started with a prompt + source. |
| **Activity** | Single unit of work within a Session. Sessions contain multiple activities (plan generation, messages, progress updates). |

## Quickstart: Your First API Call

### Step 1: List sources
\`\`\`bash
curl 'https://jules.googleapis.com/v1alpha/sources' \\
    -H 'X-Goog-Api-Key: YOUR_API_KEY'
\`\`\`
Response:
\`\`\`json
{
  "sources": [
    {
      "name": "sources/github/bobalover/boba",
      "id": "github/bobalover/boba",
      "githubRepo": { "owner": "bobalover", "repo": "boba" }
    }
  ],
  "nextPageToken": "github/bobalover/boba-web"
}
\`\`\`

### Step 2: Create a session
\`\`\`bash
curl 'https://jules.googleapis.com/v1alpha/sessions' \\
    -X POST \\
    -H "Content-Type: application/json" \\
    -H 'X-Goog-Api-Key: YOUR_API_KEY' \\
    -d '{
      "prompt": "Create a boba app!",
      "sourceContext": {
        "source": "sources/github/bobalover/boba",
        "githubRepoContext": { "startingBranch": "main" }
      },
      "automationMode": "AUTO_CREATE_PR",
      "title": "Boba App"
    }'
\`\`\`
- `automationMode` is optional. Default: no PR auto-created.
- `AUTO_CREATE_PR` → PR opens automatically.
- `requirePlanApproval: true` → session waits for explicit plan approval.
- Default: plans auto-approved.

Response:
\`\`\`json
{
  "name": "sessions/31415926535897932384",
  "id": "31415926535897932384",
  "title": "Boba App",
  "sourceContext": {
    "source": "sources/github/bobalover/boba",
    "githubRepoContext": { "startingBranch": "main" }
  },
  "prompt": "Create a boba app!"
}
\`\`\`

### Step 3: List sessions
\`\`\`bash
curl 'https://jules.googleapis.com/v1alpha/sessions?pageSize=5' \\
    -H 'X-Goog-Api-Key: YOUR_API_KEY'
\`\`\`

### Step 4: Approve plan (if required)
\`\`\`bash
curl 'https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:approvePlan' \\
    -X POST \\
    -H "Content-Type: application/json" \\
    -H 'X-Goog-Api-Key: YOUR_API_KEY'
\`\`\`

### Step 5: Activities + sendMessage
\`\`\`bash
# List activities
curl 'https://jules.googleapis.com/v1alpha/sessions/SESSION_ID/activities?pageSize=30' \\
    -H 'X-Goog-Api-Key: YOUR_API_KEY'

# Send message to agent
curl 'https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:sendMessage' \\
    -X POST \\
    -H "Content-Type: application/json" \\
    -H 'X-Goog-Api-Key: YOUR_API_KEY' \\
    -d '{ "prompt": "Can you make the app corgi themed?" }'
\`\`\`

## Activity types (from example response)
- `planGenerated` — agent's plan with steps
- `planApproved` — user approved plan (`planId`)
- `progressUpdated` — work in progress, can include bash output, git patches, media
- `sessionCompleted` — done, includes final changeSet with `suggestedCommitMessage`
- `artifacts[]` — `bashOutput`, `changeSet` (gitPatch with unidiffPatch + baseCommitId), `media` (base64 image)

## Output PR structure
\`\`\`json
{
  "outputs": [{
    "pullRequest": {
      "url": "https://github.com/bobalover/boba/pull/35",
      "title": "Create a boba app",
      "description": "..."
    }
  }]
}
\`\`\`
