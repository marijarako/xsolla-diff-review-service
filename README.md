# AI Diff Review Service

A service that receives a unified diff, analyzes it asynchronously, and
returns structured review findings.

## Running locally

\`\`\`bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
\`\`\`

## Development status

- [x] Phase 0: project setup
- [x] Phase 1: /health and /spec routes
- [ ] Phase 2: authentication
- [ ] Phase 3: diff parsing
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