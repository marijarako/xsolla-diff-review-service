# AI Diff Review Service

A service that receives a unified diff, analyzes it asynchronously, and
returns structured review findings.

## Running locally

\`\`\`bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
\`\`\`

## Configuration

The service reads its configuration from environment variables.

| Variable     | Required | Description                                               |
|--------------|----------|-----------------------------------------------------------|
| `AUTH_TOKEN` | Yes      | Bearer token required on every `/v1/*` route.             |

See `.env.example` for a template. Before running locally, export it:

\`\`\`bash
export AUTH_TOKEN=your-secret-token-here
uvicorn app.main:app --host 0.0.0.0 --port 8000
\`\`\`

## Authentication

Every route under `/v1/*` (any HTTP method) requires an
`Authorization: Bearer <token>` header matching `AUTH_TOKEN`. Missing or
invalid tokens return `401` with the error envelope:

\`\`\`json
{ "error": { "code": "unauthorized", "message": "..." } }
\`\`\`

`/health` and `/spec` remain public and require no authentication.

## Diff Parsing

The service parses unified diff text (as produced by `git diff`) into a
structured list of files, each with its added ("+") lines and their line
numbers in the new file.

Notes on parsing behavior:
- Only line numbers in the **new** file are tracked (removed lines do not
  advance the line counter, since they don't exist in the new file).
- Files that were deleted (`+++ /dev/null`) are skipped - there is nothing
  meaningful to review in a deleted file.
- A diff with no valid hunk headers (`@@ ... @@`) is rejected as
  unparseable.

## Development status

- [x] Phase 0: project setup
- [x] Phase 1: /health and /spec routes
- [x] Phase 2: authentication
- [x] Phase 3: diff parsing
- [ ] Phase 4: mock provider rules
- [ ] Phase 5: async job system
- [ ] Phase 6: GET routes for job status
- [ ] Phase 7: chunking
- [ ] Phase 8: caching + idempotency
- [ ] Phase 9: SSE streaming
- [ ] Phase 10: rate limiting
- [ ] Phase 11: concurrency
- [ ] Phase 12: LLM provider
- [ ] Phase 13: deployment
- [ ] Phase 14: testing
- [ ] Phase 15: SUBMISSION.md