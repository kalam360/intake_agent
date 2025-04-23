"""
Cost tracking module for the real estate intake agent.

This module provides functionality to track and report API usage and costs
for various services used by the agent (OpenAI, Deepgram, etc.).
"""
from typing import Dict, List, Optional, Any
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("cost-tracking")

# Current pricing (as of April 2025)
# These should be updated if pricing changes
PRICING = {
    "openai": {
        "gpt-4o-mini": {
            "input": 0.00015,  # per token
            "output": 0.00060,  # per token
        },
        "tts-1": 0.000015,  # per character
    },
    "deepgram": {
        "nova-2": 0.00025,  # per second
    },
    "cartesia": {
        "tts": 0.000010,  # per character
    },
}


@dataclass
class APIUsage:
    """Tracks usage for a specific API call."""
    api_name: str
    model_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    input_tokens: int = 0
    output_tokens: int = 0
    audio_seconds: float = 0.0
    characters: int = 0
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CostTracker:
    """Tracks API usage and costs across a session."""
    
    def __init__(self):
        self.usages: List[APIUsage] = []
        self.session_start = datetime.now()
        self.session_id = f"session_{int(time.time())}"
    
    def track_llm_usage(self, model_name: str, input_tokens: int, output_tokens: int, metadata: Optional[Dict[str, Any]] = None):
        """
        Track usage of an LLM API call.
        
        Args:
            model_name: Name of the model used (e.g., "gpt-4o-mini")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Additional information about the API call
        """
        if "openai" in model_name or model_name in PRICING.get("openai", {}):
            api_name = "openai"
            pricing = PRICING.get("openai", {}).get(model_name, {})
            cost = (input_tokens * pricing.get("input", 0)) + (output_tokens * pricing.get("output", 0))
        else:
            api_name = "unknown"
            cost = 0.0
        
        usage = APIUsage(
            api_name=api_name,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            metadata=metadata or {}
        )
        
        self.usages.append(usage)
        logger.info(f"Tracked LLM usage: {model_name}, cost: ${cost:.6f}")
    
    def track_stt_usage(self, model_name: str, audio_seconds: float, metadata: Optional[Dict[str, Any]] = None):
        """
        Track usage of a speech-to-text API call.
        
        Args:
            model_name: Name of the model used (e.g., "nova-2")
            audio_seconds: Duration of audio processed in seconds
            metadata: Additional information about the API call
        """
        if "deepgram" in model_name or model_name in PRICING.get("deepgram", {}):
            api_name = "deepgram"
            cost = audio_seconds * PRICING.get("deepgram", {}).get(model_name, 0.00025)
        else:
            api_name = "unknown"
            cost = 0.0
        
        usage = APIUsage(
            api_name=api_name,
            model_name=model_name,
            audio_seconds=audio_seconds,
            cost=cost,
            metadata=metadata or {}
        )
        
        self.usages.append(usage)
        logger.info(f"Tracked STT usage: {model_name}, {audio_seconds:.2f}s, cost: ${cost:.6f}")
    
    def track_tts_usage(self, model_name: str, characters: int, metadata: Optional[Dict[str, Any]] = None):
        """
        Track usage of a text-to-speech API call.
        
        Args:
            model_name: Name of the model used (e.g., "tts-1")
            characters: Number of characters synthesized
            metadata: Additional information about the API call
        """
        if "openai" in model_name and "tts" in model_name:
            api_name = "openai"
            cost = characters * PRICING.get("openai", {}).get("tts-1", 0.000015)
        elif "cartesia" in model_name:
            api_name = "cartesia"
            cost = characters * PRICING.get("cartesia", {}).get("tts", 0.000010)
        else:
            api_name = "unknown"
            cost = 0.0
        
        usage = APIUsage(
            api_name=api_name,
            model_name=model_name,
            characters=characters,
            cost=cost,
            metadata=metadata or {}
        )
        
        self.usages.append(usage)
        logger.info(f"Tracked TTS usage: {model_name}, {characters} chars, cost: ${cost:.6f}")
    
    def get_total_cost(self) -> float:
        """Get the total cost of all tracked API calls."""
        return sum(usage.cost for usage in self.usages)
    
    def get_cost_by_api(self) -> Dict[str, float]:
        """Get costs broken down by API provider."""
        costs = {}
        for usage in self.usages:
            costs[usage.api_name] = costs.get(usage.api_name, 0.0) + usage.cost
        return costs
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get a summary of all API usage."""
        total_input_tokens = sum(usage.input_tokens for usage in self.usages)
        total_output_tokens = sum(usage.output_tokens for usage in self.usages)
        total_audio_seconds = sum(usage.audio_seconds for usage in self.usages)
        total_characters = sum(usage.characters for usage in self.usages)
        
        return {
            "session_id": self.session_id,
            "session_duration_seconds": (datetime.now() - self.session_start).total_seconds(),
            "total_cost": self.get_total_cost(),
            "costs_by_api": self.get_cost_by_api(),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_audio_seconds": total_audio_seconds,
            "total_characters": total_characters,
            "call_count": len(self.usages),
        }
    
    def log_usage_summary(self):
        """Log a summary of all API usage."""
        summary = self.get_usage_summary()
        
        logger.info("=== API Usage Summary ===")
        logger.info(f"Session ID: {summary['session_id']}")
        logger.info(f"Session Duration: {summary['session_duration_seconds']:.2f} seconds")
        logger.info(f"Total Cost: ${summary['total_cost']:.4f}")
        
        logger.info("Costs by API:")
        for api, cost in summary['costs_by_api'].items():
            logger.info(f"  - {api}: ${cost:.4f}")
        
        logger.info(f"Total Input Tokens: {summary['total_input_tokens']}")
        logger.info(f"Total Output Tokens: {summary['total_output_tokens']}")
        logger.info(f"Total Audio Seconds: {summary['total_audio_seconds']:.2f}")
        logger.info(f"Total Characters: {summary['total_characters']}")
        logger.info(f"Total API Calls: {summary['call_count']}")
        logger.info("========================")


# Global tracker instance
tracker = CostTracker()


# Decorator for tracking LLM usage
def track_llm(model_name: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            
            # This is a simplified implementation - in a real system,
            # you would extract actual token counts from the API response
            # Here we're using rough estimates
            input_text = kwargs.get("input", "")
            output_text = str(result)
            
            # Rough token estimation (1 token ≈ 4 chars)
            input_tokens = len(input_text) // 4
            output_tokens = len(output_text) // 4
            
            tracker.track_llm_usage(
                model_name=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                metadata={
                    "duration": time.time() - start_time,
                    "function": func.__name__,
                }
            )
            
            return result
        return wrapper
    return decorator


# Decorator for tracking STT usage
def track_stt(model_name: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            
            # Estimate audio duration from the audio data
            # This is a simplified implementation
            audio_data = kwargs.get("audio", None)
            if audio_data:
                # In a real implementation, extract actual audio duration
                audio_seconds = 5.0  # Placeholder
            else:
                audio_seconds = 0.0
            
            tracker.track_stt_usage(
                model_name=model_name,
                audio_seconds=audio_seconds,
                metadata={
                    "duration": time.time() - start_time,
                    "function": func.__name__,
                }
            )
            
            return result
        return wrapper
    return decorator


# Decorator for tracking TTS usage
def track_tts(model_name: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            
            # Extract text length
            text = kwargs.get("text", "")
            characters = len(text)
            
            tracker.track_tts_usage(
                model_name=model_name,
                characters=characters,
                metadata={
                    "duration": time.time() - start_time,
                    "function": func.__name__,
                }
            )
            
            return result
        return wrapper
    return decorator