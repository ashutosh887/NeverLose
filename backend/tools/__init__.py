"""
NeverLose Tools — Pine Labs API wrappers.

All tools check USE_MOCK env var first.
  USE_MOCK=true  → load from backend/mock/*.json (safe for demo)
  USE_MOCK=false → call Pine Labs APIs (legacy or new, with correct auth)
"""
