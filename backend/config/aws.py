"""
AWS Bedrock Configuration
==========================

NeverLose uses Claude Sonnet 4.6 (Supervisor) and Claude Haiku 4.5 (sub-agents)
via AWS Bedrock with Global CRIS (Cross-Region Inference Service).

CRIS prefix "global." routes to the nearest available region automatically.
This prevents capacity-related failures at demo time vs. a fixed us-east-1 endpoint.

To switch to direct regional inference (slightly faster, no CRIS overhead):
  BEDROCK_SUPERVISOR_MODEL = us.anthropic.claude-sonnet-4-6-20251001-v1:0
  BEDROCK_SUB_AGENT_MODEL  = us.anthropic.claude-haiku-4-5-20251001-v1:0

Region: ap-south-1 (Mumbai) — lowest latency for the Indian demo context.
Override with AWS_REGION env var if demoing from a different region.

Credentials: loaded automatically by the Anthropic SDK from env vars
  AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (or ~/.aws/credentials at the venue).
"""

import os


class AWSConfig:
    # ── Region ────────────────────────────────────────────────────────────────
    # ap-south-1 = Mumbai; use us-east-1 if Bedrock CRIS not available in ap-south-1
    REGION: str = os.getenv("AWS_REGION", "ap-south-1")

    # ── Credentials (read by anthropic SDK / boto3 from env automatically) ────
    ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")

    # ── Bedrock Model IDs — Global CRIS ───────────────────────────────────────
    # Global CRIS (recommended for demos — resilient across regions):
    BEDROCK_SUPERVISOR_MODEL: str = os.getenv(
        "BEDROCK_SUPERVISOR_MODEL",
        "global.anthropic.claude-sonnet-4-6-v1",
    )
    BEDROCK_SUB_AGENT_MODEL: str = os.getenv(
        "BEDROCK_SUB_AGENT_MODEL",
        "global.anthropic.claude-haiku-4-5-20251001-v1:0",
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
        Import anthropic here to avoid hard dependency if Bedrock isn't available.
        """
        import anthropic
        return anthropic.AsyncAnthropicBedrock(aws_region=cls.REGION)
