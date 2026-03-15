"""ManimFlow configuration — all model and generation settings in one place.

Change settings here to affect the entire pipeline.
Environment variables override these defaults.
"""

import os


# ─── MODEL CONFIGURATION ───

# The LLM model to use for all pipeline stages
MODEL = os.environ.get("MODEL", "claude-opus-4-6")

# LLM provider: "anthropic" or "bedrock"
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic")

# Bedrock model ID (only used when LLM_PROVIDER=bedrock)
BEDROCK_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
)


# ─── CONTEXT AND TOKEN LIMITS ───

# Maximum output tokens per LLM call
MAX_TOKENS_DEFAULT = 16384

# Higher limits for stages that produce large outputs
MAX_TOKENS_DESIGN = 32768  # Design system rewrites full story with visual specs
MAX_TOKENS_SCREENPLAY = 32768  # Screenplay produces large structured JSON
MAX_TOKENS_CODEGEN = 32768  # Code generation
MAX_TOKENS_FIX = 32768  # Code fix calls

# Enable 1M token context window (requires beta header for supported models)
ENABLE_1M_CONTEXT = True

# Models that support 1M context
CONTEXT_1M_MODELS = {
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4-20250514",
}


# ─── THINKING CONFIGURATION ───

# Enable extended/interleaved thinking for all agents
ENABLE_THINKING = True

# Thinking token budget (for models that need explicit budget, not adaptive)
THINKING_BUDGET = 10000

# Models that use adaptive thinking (no budget needed, thinking scales automatically)
ADAPTIVE_THINKING_MODELS = {"claude-opus-4-6"}


# ─── CACHING ───

# Enable prompt caching (reduces cost for repeated system prompts)
ENABLE_CACHING = True

# Cache TTL: "5m" (default) or "1h" (requires extended-cache-ttl beta)
CACHE_TTL = "5m"


# ─── PIPELINE CONFIGURATION ───

# Writers Room
WRITERS_PARALLEL = 3  # Number of parallel story writers
WRITERS_REVISIONS = 1  # Number of review-revise rounds

# Screenplay
SCREENPLAY_MAX_FIX_ROUNDS = 3  # Max validation-fix rounds
SCREENPLAY_MAX_TOOL_ROUNDS = 6  # Max knowledge search rounds

# Codegen / Render
MAX_FIX_ATTEMPTS = 5  # Max render fix attempts
MAX_QUALITY_LOOPS = 2  # Max quality improvement rounds

# Render quality: l=480p, m=720p, h=1080p, k=4K
DEFAULT_QUALITY = "l"
