"""
AWS Bedrock Configuration
==========================

NeverLose uses Claude Sonnet 4.6 (Supervisor) and Claude Haiku 4.5 (sub-agents)
via AWS Bedrock with CRIS (Cross-Region Inference Service).

CRIS model ID prefix depends on region:
  us-east-1 / us-west-2  → "us." prefix   e.g. us.anthropic.claude-sonnet-4-6-20251001-v1:0
  ap-south-1 (Mumbai)    → "global." prefix (routes to nearest available)

Workshop Studio (PineLabs Hackathon) uses us-east-1 with TEMPORARY credentials.
Temporary credentials include AWS_SESSION_TOKEN — must be passed explicitly to
AsyncAnthropicBedrock (boto3 does not auto-read it from env in all SDK versions).

Credentials expire — if you get auth errors, refresh from Workshop Studio and
update AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN in .env.
"""

import os


class AWSConfig:
    # ── Region ────────────────────────────────────────────────────────────────
    # Workshop Studio restricts to us-east-1. Change to ap-south-1 for prod.
    REGION: str = os.getenv("AWS_REGION", "us-east-1")

    # ── Credentials ───────────────────────────────────────────────────────────
    ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    # SESSION_TOKEN is required for Workshop Studio temporary credentials.
    # Leave empty for long-term IAM credentials (production).
    SESSION_TOKEN: str = os.getenv("AWS_SESSION_TOKEN", "")

    # ── Bedrock Model IDs ─────────────────────────────────────────────────────
    # us-east-1 → "us." CRIS prefix
    # ap-south-1 → "global." CRIS prefix
    # Set BEDROCK_SUPERVISOR_MODEL / BEDROCK_SUB_AGENT_MODEL in .env to override.
    # Verified working in us-east-1 Workshop Studio account (March 2026)
    BEDROCK_SUPERVISOR_MODEL: str = os.getenv(
        "BEDROCK_SUPERVISOR_MODEL",
        "us.anthropic.claude-sonnet-4-6",
    )
    BEDROCK_SUB_AGENT_MODEL: str = os.getenv(
        "BEDROCK_SUB_AGENT_MODEL",
        "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    )

    # ── Inference parameters ──────────────────────────────────────────────────
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7

    @classmethod
    def is_configured(cls) -> bool:
        """True if AWS credentials are present in the environment."""
        return bool(cls.ACCESS_KEY_ID and cls.SECRET_ACCESS_KEY)

    @classmethod
    def bedrock_client(cls):
        """
        Returns an AsyncAnthropicBedrock client.

        Passes aws_session_token explicitly — required for Workshop Studio
        temporary credentials (STS tokens). Safe to pass empty string for
        long-term IAM credentials (SDK ignores it when empty).
        """
        import anthropic
        kwargs = {
            "aws_region": cls.REGION,
            "aws_access_key": cls.ACCESS_KEY_ID,
            "aws_secret_key": cls.SECRET_ACCESS_KEY,
        }
        if cls.SESSION_TOKEN:
            kwargs["aws_session_token"] = cls.SESSION_TOKEN
        return anthropic.AsyncAnthropicBedrock(**kwargs)
