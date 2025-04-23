import logging
from pathlib import Path
import os

from dotenv import load_dotenv
from livekit.agents import (
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    Agent,
    AgentSession,
    RoomInputOptions,
)
from livekit.plugins import (
    cartesia,
    openai,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel


load_dotenv(dotenv_path=".env.local", override=True)
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger("voice-agent")


def worker_init(proc: JobProcess):
    load_dotenv(Path(__file__).with_name(".env.local"), override=True)
    # VAD loading is now handled in AgentSession initialization


class MyVoiceAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
                "You should use short and concise responses, and avoiding usage of unpronouncable punctuation. "
                "You were created as a demo to showcase the capabilities of LiveKit's agents framework."
            )
        )

    async def on_enter(self):
        # This method is called when the agent enters the conversation
        # We'll use it to trigger the initial greeting
        self.session.generate_reply()


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
    
    # Configure room options with noise cancellation
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


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=worker_init,
        ),
    )
