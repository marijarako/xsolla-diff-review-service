"""
Centralized configuration, loaded from environment variables.

Reading configuration from environment variables (instead of hardcoding
values directly in the code) is standard practice: it lets us use a
different token on our local machine vs. on the deployed server, without
ever changing the code itself. This matters even more later, when we
store LLM API keys the same way.
"""

import os

# The bearer token clients must send to access any /v1/* route.
# We do NOT hardcode a default value here on purpose: if this is missing,
# the service must fail closed (reject every /v1 request) rather than
# silently accepting anything.
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")