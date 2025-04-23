# Migration Plan: LiveKit Agents v0.x to v1.x

This document outlines the plan for migrating `voice_agent/agent.py` from LiveKit Agents v0.x to v1.x.

## Overview

The migration involves updating the code structure to align with the new v1.x API, while maintaining all existing functionality including:
- Voice assistant capabilities
- STT, LLM, TTS integration
- Turn detection
- Noise cancellation
- Initial greeting

## Migration Steps

### 1. Update Imports

```python
# Keep standard library imports
import logging
from pathlib import Path
import os
from dotenv import load_dotenv

# Update livekit.agents imports
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    Agent,
    AgentSession,
    RoomInputOptions,
)

# Update plugin imports
from livekit.plugins import (
    cartesia,
    openai,
    deepgram,
    silero,
    noise_cancellation,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
```

### 2. Keep Environment Loading & Logging

Retain the existing environment loading and logger setup:

```python
load_dotenv(dotenv_path=".env.local", override=True)
logger = logging.getLogger("voice-agent")
```

### 3. Refactor Initialization (`prewarm` -> `worker_init`)

```python
def worker_init(proc: JobProcess):
    load_dotenv(Path(__file__).with_name(".env.local"), override=True)
    # Remove VAD loading as it will be handled in AgentSession
```

### 4. Create Custom Agent Class

```python
class MyVoiceAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
                "You should use short and concise responses, and avoiding usage of unpronouncable punctuation. "
                "You were created as a demo to showcase the capabilities of LiveKit's agents framework."
            )
        )
```

### 5. Refactor Main Logic (`entrypoint`)

```python
async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect()
    
    # Create AgentSession with all plugins
    session = AgentSession(
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
        min_endpointing_delay=0.5,  # Original value
        max_endpointing_delay=5.0,  # Original value
    )
    
    # Configure room options
    room_options = RoomInputOptions(
        noise_cancellation=noise_cancellation.BVC(),
    )
    
    # Start the session
    await session.start(
        room=ctx.room,
        agent=MyVoiceAgent(),
        room_input_options=room_options,
    )
    
    # Initial greeting
    await session.generate_reply(
        instructions="Hey, how can I help you today?"
    )
```

### 6. Update CLI Runner

```python
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=worker_init,  # Keep if worker_init is not empty
        ),
    )
```

## Important Notes

1. **Download Turn Detector Weights**: Before first execution, run:
   ```
   python agent.py download-files
   ```

2. **Metrics Handling**: The v1.x approach for metrics collection is not covered in the provided documentation. This functionality may need to be revisited after the initial migration.

## Migration Flow Diagram

```mermaid
graph TD
    A[Start: Old agent.py] --> B{Analyze Code, User Snippet, Docs};
    B --> C{Identify v0.x Patterns & v1.x Structure};
    C --> D{Plan Code Modifications};
    D --> E[Update Imports (Agents, Plugins, Turn Detector)];
    D --> F[Keep Env Loading & Logging];
    D --> G[Refactor prewarm -> worker_init (Remove VAD load)];
    D --> H[Refactor entrypoint Function];
    H --> I[Define Custom Agent Class (with instructions)];
    H --> J[Instantiate AgentSession (Plugins, VAD, Turn Detector, Delays)];
    H --> K[Instantiate RoomInputOptions (Noise Cancellation)];
    H --> L[Call session.start];
    H --> M[Call session.generate_reply (Initial Greeting)];
    D --> N[Update CLI Runner (WorkerOptions)];
    D --> O[Omit Metrics Handling];
    D --> P[Note: Download Turn Detector Weights];
    P --> Q{Final Review Plan};
    Q --> R[End: Final Migrated agent.py Plan];