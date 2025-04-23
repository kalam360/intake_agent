"""
Core implementation of the intake agent functionality.

This module provides the implementation details for:
- Prompts and templates
- Validation utilities
- Cost tracking
"""

from prompts import (
    AGENT_INSTRUCTIONS,
    INITIAL_GREETING,
    CLOSING_MESSAGE,
    VALIDATION_PROMPT,
    CLARIFICATION_PROMPT
)

from validation import (
    validate_all,
    generate_clarification_questions,
    summarize_intake_data
)

from cost_tracking import (
    tracker,
    track_llm,
    track_stt,
    track_tts
)

__all__ = [
    # Prompts
    "AGENT_INSTRUCTIONS",
    "INITIAL_GREETING",
    "CLOSING_MESSAGE",
    "VALIDATION_PROMPT",
    "CLARIFICATION_PROMPT",
    # Validation
    "validate_all",
    "generate_clarification_questions",
    "summarize_intake_data",
    # Cost tracking
    "tracker",
    "track_llm",
    "track_stt",
    "track_tts"
]