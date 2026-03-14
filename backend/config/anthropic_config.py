"""
Anthropic Direct API Configuration
=====================================

Used as fallback when AWS Bedrock credentials are unavailable or Bedrock
returns errors. Same model capabilities, slightly different latency profile.

Fallback chain in supervisor.py:
  1. AWS Bedrock (CRIS) — preferred, lower latency at venue
  2. Anthropic Direct API — fallback when Bedrock unavailable
  3. Mock responses — last resort, never fails the demo

Model IDs differ between Bedrock and Anthropic direct:
  Bedrock : global.anthropic.claude-sonnet-4-6-v1
  Direct  : claude-sonnet-4-6-20251001

Set ANTHROPIC_API_KEY in .env for the fallback to work.
"""

import os


class AnthropicConfig:
    # ── API Key ───────────────────────────────────────────────────────────────
    API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # ── Model IDs (Anthropic direct — different from Bedrock IDs) ────────────
    SUPERVISOR_MODEL: str = "claude-sonnet-4-6-20251001"
    SUB_AGENT_MODEL: str = "claude-haiku-4-5-20251001"

    # ── Inference parameters (keep in sync with AWSConfig) ───────────────────
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7

    @classmethod
    def is_configured(cls) -> bool:
        """True if ANTHROPIC_API_KEY is set."""
        return bool(cls.API_KEY)

    @classmethod
    def direct_client(cls):
        """
        Returns an AsyncAnthropic client.
        Import anthropic here to avoid hard dependency at module load time.
        """
        import anthropic
        return anthropic.AsyncAnthropic(api_key=cls.API_KEY)
