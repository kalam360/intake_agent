# Real Estate Intake Agent

This project implements a voice-based real estate intake agent using LiveKit Agents. The agent conducts professional intake conversations with potential real estate clients to gather essential information about their needs and preferences.

## Features

- Voice-based interaction using LiveKit's agent framework
- Professional intake script following real estate industry best practices
- Collects comprehensive client information:
  - Contact details
  - Property goals (buy/sell/rent)
  - Search criteria
  - Financing information
  - Additional requirements
- **Validation and verification** of collected information
- **Cost tracking and usage monitoring** for all API calls
- Natural conversation flow with appropriate follow-up questions
- Noise cancellation for clear audio
- Turn detection for smooth conversation

## Project Structure

```
intake_agent/
├── voice_agent/
│   ├── agent.py           # Main agent implementation
│   ├── .env.example       # Example environment variables
│   ├── pyproject.toml     # Project dependencies
│   └── intake_core/
│       ├── prompts.py     # Intake script and agent instructions
│       ├── validation.py  # Validation logic for intake information
│       └── cost_tracking.py # API usage and cost tracking functionality
```

## Intake Script

The intake script in `voice_agent/intake_core/prompts.py` is designed to be minimal yet professional, covering all essential information needed for real estate client intake. The script is structured into sections:

| Section | Fields | Source |
|---------|--------|--------|
| Contact Information | name, email, phone, preferred contact | Content Snare |
| Property Goals | buy/sell/rent, timeline, budget/target price | filerequestpro.com |
| Search Criteria | location, bedrooms, property type, must-haves | The Real Estate Team OS - Follow Up Boss |
| Financing | pre-approved status, cash/loan | Content Snare |
| Additional Info | pets, accessibility, urgency, notes | Industry best practices |

## Validation System

The agent includes a comprehensive validation system in `voice_agent/intake_core/validation.py` that:

1. **Validates collected information** for completeness and correctness
2. **Generates clarification questions** for missing or invalid data
3. **Summarizes collected information** for client confirmation
4. **Verifies data accuracy** before concluding the conversation

The validation system checks:
- Contact information format (email, phone)
- Required fields based on transaction type
- Logical consistency of provided information
- Completeness of critical information

## Cost Tracking System

The agent includes a detailed cost tracking system in `voice_agent/intake_core/cost_tracking.py` that:

1. **Monitors API usage** for all services (OpenAI, Deepgram, Cartesia)
2. **Calculates costs** based on current pricing models
3. **Tracks token usage** for LLM calls
4. **Measures audio duration** for STT processing
5. **Counts characters** for TTS synthesis
6. **Provides detailed reports** on usage and costs

### Current API Pricing (April 2025)

| Service | Model | Unit | Price |
|---------|-------|------|-------|
| OpenAI | gpt-4o-mini (input) | per token | $0.00015 |
| OpenAI | gpt-4o-mini (output) | per token | $0.00060 |
| OpenAI | tts-1 | per character | $0.000015 |
| Deepgram | nova-2 | per second | $0.00025 |
| Cartesia | TTS | per character | $0.000010 |

### Cost Reporting

The agent provides cost information through:

1. **Real-time function**: Call `get_session_cost()` during a conversation to see current costs
2. **Session summary**: Detailed breakdown logged at the end of each session
3. **Log files**: All API calls and costs are logged to `voice_agent/KMS/logs/intake_session.log`

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   cd voice_agent
   pip install -e .
   ```
3. Create a `.env.local` file based on `.env.example` with your API keys
4. Download required model files:
   ```bash
   python agent.py download-files
   ```

## Running the Agent

```bash
cd voice_agent
python agent.py
```

## Agent Implementation Details

The agent is implemented in `agent.py` and uses:

- **Speech-to-Text**: Deepgram for accurate transcription
- **Language Model**: OpenAI GPT-4o-mini for natural conversation
- **Text-to-Speech**: Cartesia for high-quality voice output
- **Voice Activity Detection**: Silero VAD for detecting when users are speaking
- **Turn Detection**: Multilingual model for smooth conversation flow
- **Noise Cancellation**: BVC for clear audio

## Conversation Flow

1. Agent introduces itself and explains the purpose of the conversation
2. Systematically collects information through all intake sections
3. Asks appropriate follow-up questions based on client responses
4. **Validates collected information and asks for clarification if needed**
5. **Summarizes information and confirms accuracy with the client**
6. Provides a closing message with next steps
7. **Logs usage statistics and costs**
8. Stores collected information for agent follow-up

## Cost Optimization Tips

To minimize costs while maintaining quality:

1. **Adjust conversation length**: Shorter, more focused conversations reduce token usage
2. **Use efficient prompts**: Clear, concise agent instructions reduce token consumption
3. **Optimize validation**: Only validate critical fields to reduce LLM calls
4. **Monitor usage patterns**: Use the cost tracking system to identify optimization opportunities
5. **Consider model selection**: Balance quality and cost by selecting appropriate models

## Data Extraction and Storage

The agent extracts structured data from the conversation, including:

- Client contact details
- Property preferences and requirements
- Transaction type and timeline
- Budget constraints
- Special requirements

This information is stored in a structured format that can be easily integrated with CRM systems or passed to real estate agents for follow-up.

## Dependencies

- livekit-agents v1.x
- Various LiveKit plugins for STT, TTS, LLM integration
- Python 3.12+

## References

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Content Snare Real Estate Intake Forms](https://contentsnare.com/real-estate-client-intake-form/)
- [File Request Pro Buyer Questionnaire](https://filerequestpro.com/articles/real-estate-buyer-questionnaire)