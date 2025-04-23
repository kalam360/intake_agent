import logging
from pathlib import Path
import os
from typing import Dict, Any, List

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

# Import the intake prompts and validation
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


class RealEstateIntakeAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS
        )
        # Initialize client data dictionary to store intake information
        self.client_data: Dict[str, Any] = {}
        # Track conversation state
        self.intake_complete = False
        self.validation_in_progress = False

    async def on_enter(self):
        # This method is called when the agent enters the conversation
        # We'll use it to trigger the initial greeting
        await self.session.generate_reply(
            instructions=INITIAL_GREETING
        )
    
    async def on_user_message(self, message: str):
        # This method is called when a user message is received
        # We'll use it to update our client data based on the conversation
        
        # If we're in validation mode, check if the user confirmed the information
        if self.validation_in_progress:
            if any(confirm in message.lower() for confirm in ["yes", "correct", "that's right", "looks good"]):
                self.intake_complete = True
                transaction_type = self.client_data.get("transaction_type", "real estate")
                closing = CLOSING_MESSAGE.format(transaction_type=transaction_type)
                await self.session.generate_reply(
                    instructions=closing
                )
            else:
                # If they didn't confirm, we'll continue the conversation
                self.validation_in_progress = False
                await self.session.generate_reply(
                    instructions="I understand there are some details to correct. Let's continue with the conversation to make sure we get everything right."
                )
    
    @function_tool
    async def validate_intake_information(self, context: RunContext):
        """
        Validate the collected intake information and ask for clarification if needed.
        """
        # Extract client data from the conversation context
        self.update_client_data(context)
        
        # Validate the collected data
        validation_results = validate_all(self.client_data)
        
        if validation_results:
            # If there are validation issues, generate clarification questions
            clarification_questions = generate_clarification_questions(validation_results)
            clarification_text = "\n".join([f"- {q}" for q in clarification_questions])
            prompt = CLARIFICATION_PROMPT.format(clarification_questions=clarification_text)
            
            return None, prompt
        else:
            # If validation passes, summarize the data and ask for confirmation
            summary = summarize_intake_data(self.client_data)
            prompt = VALIDATION_PROMPT.format(summary=summary)
            self.validation_in_progress = True
            
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
        
        return None, response
    
    def update_client_data(self, context: RunContext):
        """
        Extract client data from the conversation context.
        """
        # This is a simplified implementation - in a real system, you would use
        # more sophisticated NLP to extract structured data from the conversation
        
        # Contact Information
        if context.get("name") or context.get("full_name"):
            self.client_data["full_name"] = context.get("name") or context.get("full_name")
        
        if context.get("email"):
            self.client_data["email"] = context.get("email")
        
        if context.get("phone") or context.get("phone_number"):
            self.client_data["phone"] = context.get("phone") or context.get("phone_number")
        
        if context.get("preferred_contact"):
            self.client_data["preferred_contact"] = context.get("preferred_contact")
        
        # Property Goals
        if context.get("transaction_type"):
            self.client_data["transaction_type"] = context.get("transaction_type")
        elif any(term in str(context).lower() for term in ["buy", "purchase"]):
            self.client_data["transaction_type"] = "buy"
        elif "sell" in str(context).lower():
            self.client_data["transaction_type"] = "sell"
        elif "rent" in str(context).lower():
            self.client_data["transaction_type"] = "rent"
        
        if context.get("timeline"):
            self.client_data["timeline"] = context.get("timeline")
        
        if context.get("budget") or context.get("price_range"):
            self.client_data["budget"] = context.get("budget") or context.get("price_range")
        
        # Search Criteria
        if context.get("location") or context.get("area") or context.get("neighborhood"):
            self.client_data["location"] = context.get("location") or context.get("area") or context.get("neighborhood")
        
        if context.get("bedrooms"):
            self.client_data["bedrooms"] = context.get("bedrooms")
        
        if context.get("property_type"):
            self.client_data["property_type"] = context.get("property_type")
        
        if context.get("must_haves") or context.get("requirements"):
            self.client_data["must_haves"] = context.get("must_haves") or context.get("requirements")
        
        # Financing
        if context.get("pre_approval") is not None:
            self.client_data["pre_approval"] = context.get("pre_approval")
        elif "pre-approved" in str(context).lower():
            self.client_data["pre_approval"] = True
        
        if context.get("payment_method"):
            self.client_data["payment_method"] = context.get("payment_method")
        elif "cash" in str(context).lower():
            self.client_data["payment_method"] = "cash"
        elif any(term in str(context).lower() for term in ["loan", "mortgage", "financing"]):
            self.client_data["payment_method"] = "loan"
        
        # Additional Information
        if context.get("pets"):
            self.client_data["pets"] = context.get("pets")
        
        if context.get("accessibility"):
            self.client_data["accessibility"] = context.get("accessibility")
        
        if context.get("urgency"):
            self.client_data["urgency"] = context.get("urgency")
        
        if context.get("additional_notes") or context.get("notes"):
            self.client_data["additional_notes"] = context.get("additional_notes") or context.get("notes")
    
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
