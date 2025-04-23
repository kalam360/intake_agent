import logging
from pathlib import Path
import os
import json
from typing import Dict, Any, List, Optional

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
from livekit.agents.llm import function_tool
from livekit.agents.voice import RunContext
from livekit.plugins import (
    cartesia,
    openai,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Import the base agent and intake core
from .base_agent import BaseIntakeAgent
from intake_core import (
    AGENT_INSTRUCTIONS,
    INITIAL_GREETING,
    CLOSING_MESSAGE,
    VALIDATION_PROMPT,
    CLARIFICATION_PROMPT,
    validate_all,
    generate_clarification_questions,
    summarize_intake_data,
    tracker,
    track_llm,
    track_stt,
    track_tts
)


load_dotenv(dotenv_path=".env.local", override=True)
logger = logging.getLogger("real-estate-intake-agent")


def worker_init(proc: JobProcess):
    load_dotenv(Path(__file__).with_name(".env.local"), override=True)
    # VAD loading is now handled in AgentSession initialization


class RealEstateIntakeAgent(BaseIntakeAgent, Agent):
    def __init__(self, imported_state: Optional[Dict[str, Any]] = None) -> None:
        # Initialize both parent classes
        BaseIntakeAgent.__init__(self)
        Agent.__init__(self, instructions=AGENT_INSTRUCTIONS)
        
        # Import state if provided (for mode switching)
        if imported_state:
            self.import_state(imported_state)
            logger.info(f"Imported state with {len(self.client_data)} client data fields")

    async def on_enter(self):
        # This method is called when the agent enters the conversation
        # If we have imported state, generate a transition message
        if self.conversation_history:
            transition_message = self.get_transition_message()
            await self.session.generate_reply(
                instructions=transition_message
            )
        else:
            # Otherwise, use the initial greeting
            await self.session.generate_reply(
                instructions=INITIAL_GREETING
            )
    
    async def on_user_message(self, message: str):
        # This method is called when a user message is received
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # If we're in validation mode, check if the user confirmed the information
        if self.validation_in_progress:
            if any(confirm in message.lower() for confirm in ["yes", "correct", "that's right", "looks good"]):
                self.intake_complete = True
                transaction_type = self.client_data.get("transaction_type", "real estate")
                closing = CLOSING_MESSAGE.format(transaction_type=transaction_type)
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": closing
                })
                
                await self.session.generate_reply(
                    instructions=closing
                )
            else:
                # If they didn't confirm, we'll continue the conversation
                self.validation_in_progress = False
                response = "I understand there are some details to correct. Let's continue with the conversation to make sure we get everything right."
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                await self.session.generate_reply(
                    instructions=response
                )
    
    @function_tool
    async def validate_intake_information(self, context: RunContext):
        """
        Validate the collected intake information and ask for clarification if needed.
        """
        # Extract client data from the conversation context
        self.update_client_data(context)
        
        # Use the base class validation method
        validation_result = super().validate_intake_information()
        
        if not validation_result["valid"]:
            # If there are validation issues, generate clarification questions
            clarification_text = "\n".join([f"- {q}" for q in validation_result["questions"]])
            prompt = CLARIFICATION_PROMPT.format(clarification_questions=clarification_text)
            self.current_stage = "clarification"
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": prompt
            })
            
            return None, prompt
        else:
            # If validation passes, summarize the data and ask for confirmation
            prompt = VALIDATION_PROMPT.format(summary=validation_result["summary"])
            self.validation_in_progress = True
            self.current_stage = "confirmation"
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": prompt
            })
            
            return None, prompt
    
    @function_tool
    async def get_session_cost(self, context: RunContext):
        """
        Get the current cost of the session.
        """
        summary = tracker.get_usage_summary()
        
        response = (
            f"Current session cost: ${summary['total_cost']:.4f}\n\n"
            f"Usage breakdown:\n"
            f"- LLM: {summary['total_input_tokens']} input tokens, {summary['total_output_tokens']} output tokens\n"
            f"- STT: {summary['total_audio_seconds']:.2f} seconds of audio processed\n"
            f"- TTS: {summary['total_characters']} characters synthesized\n\n"
            f"API costs:\n"
        )
        
        for api, cost in summary['costs_by_api'].items():
            response += f"- {api}: ${cost:.4f}\n"
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return None, response
    
    @function_tool
    async def export_state_to_metadata(self, context: RunContext):
        """
        Export the current agent state to room metadata.
        This allows the frontend to retrieve the state when switching modes.
        """
        state = self.export_state()
        state_json = json.dumps(state)
        
        # In a real implementation, you would update the room metadata
        # await ctx.room.update_metadata(state_json)
        
        logger.info(f"Exported state with {len(self.client_data)} client data fields")
        
        return None, "State exported successfully"
    
    async def on_exit(self):
        # This method is called when the agent exits the conversation
        # Log the collected data for future reference
        logger.info(f"Collected client data: {self.client_data}")
        
        # Get the usage summary
        summary = tracker.get_usage_summary()
        
        # Log the cost summary to console (not spoken by the agent)
        logger.info("=== SESSION COST SUMMARY ===")
        logger.info(f"Total session cost: ${summary['total_cost']:.4f}")
        logger.info(f"Audio processed: {summary['total_audio_seconds']:.1f} seconds")
        logger.info(f"Input tokens: {summary['total_input_tokens']} tokens")
        logger.info(f"Output tokens: {summary['total_output_tokens']} tokens")
        logger.info(f"Characters synthesized: {summary['total_characters']} characters")
        logger.info("===========================")
        
        # Log detailed usage summary
        tracker.log_usage_summary()
        
        # Return cost data for frontend display (added to room metadata)
        # This can be picked up by your frontend for toast display
        cost_data = {
            "total_cost": f"${summary['total_cost']:.4f}",
            "audio_seconds": f"{summary['total_audio_seconds']:.1f}s",
            "tokens": f"{summary['total_input_tokens'] + summary['total_output_tokens']}",
            "characters": f"{summary['total_characters']}"
        }
        
        # Export state to metadata for potential mode switching
        await self.export_state_to_metadata(RunContext())
        
        # If working with LiveKit's room metadata, you could do something like:
        # await ctx.room.update_metadata(json.dumps({"session_cost": cost_data}))
        # But since we don't have direct access to ctx here, just log it
        logger.info(f"FRONTEND_COST_DATA: {cost_data}")
        
        # If we haven't completed the intake and validation, do it now
        if not self.intake_complete:
            await self.validate_intake_information(RunContext())


# Wrap the original plugin classes with cost tracking
class TrackedSTT(deepgram.STT):
    @track_stt("nova-2")
    async def transcribe(self, *args, **kwargs):
        return await super().transcribe(*args, **kwargs)


class TrackedLLM(openai.LLM):
    @track_llm("gpt-4o-mini")
    async def generate(self, *args, **kwargs):
        return await super().generate(*args, **kwargs)


class TrackedTTS(cartesia.TTS):
    @track_tts("cartesia-tts")
    async def synthesize(self, *args, **kwargs):
        return await super().synthesize(*args, **kwargs)


async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect()
    
    # Create AgentSession with all plugins (using tracked versions)
    session = AgentSession(
        stt=TrackedSTT(),
        llm=TrackedLLM(model="gpt-4o-mini"),
        tts=TrackedTTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
        min_endpointing_delay=0.5,
        max_endpointing_delay=5.0,
    )
    
    # Configure room options with noise cancellation
    room_options = RoomInputOptions(
        noise_cancellation=noise_cancellation.BVC(),
    )
    
    # Start the session
    await session.start(
        room=ctx.room,
        agent=RealEstateIntakeAgent(),
        room_input_options=room_options,
    )


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("intake_session.log")
        ]
    )
    
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=worker_init,
        ),
    )
