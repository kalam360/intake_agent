# Real Estate Intake Agent

A real estate intake agent with both text and voice modes. This application allows users to interact with an AI assistant to provide information about their real estate needs.

## Features

- **Dual Mode Support**: Switch seamlessly between text and voice modes
- **Consistent Intake Flow**: Same intake process regardless of mode
- **Cost Optimization**: Text mode uses direct OpenAI API calls (lower cost)
- **State Preservation**: Conversation context is maintained when switching modes
- **Docker Support**: Easy deployment with Docker Compose

## Architecture

The application consists of two main components:

1. **Frontend**: Next.js application with:
   - Text chat interface
   - Voice interface using LiveKit
   - Mode switching capability
   - Zustand for state management

2. **Backend**: Python FastAPI application with:
   - Text agent using OpenAI API directly
   - Voice agent using LiveKit
   - Shared intake core logic
   - Cost tracking

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- Docker and Docker Compose (optional)
- OpenAI API key
- LiveKit server (for voice mode)

### Environment Setup

1. Create `.env.local` in the frontend directory:
   ```
   NEXT_PUBLIC_CONN_DETAILS_ENDPOINT=/api/connection-details
   INTAKE_API_URL=http://localhost:8000/api/intake
   ```

2. Create `.env.local` in the voice_agent directory:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

### Running with Docker

The easiest way to run the application is with Docker Compose:

```bash
# Start the application
docker compose up

# Access the application at http://localhost:3000
```

### Running Locally

#### Backend

```bash
cd voice_agent
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
python main.py
```

#### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## Usage

1. Open the application in your browser
2. By default, the application starts in text mode
3. Type messages to interact with the text agent
4. Click the "Voice Mode" button to switch to voice mode
5. Use the microphone button to speak with the voice agent
6. Click the "Text Mode" button to switch back to text mode

## Development

### Project Structure

```
├── frontend/               # Next.js frontend application
│   ├── app/                # Next.js app directory
│   ├── components/         # React components
│   ├── store/              # Zustand state management
│   └── ...
├── voice_agent/            # Python backend application
│   ├── api/                # FastAPI routes
│   ├── intake_core/        # Shared intake logic
│   ├── agent.py            # Voice agent implementation
│   ├── base_agent.py       # Base agent class
│   ├── text_agent.py       # Text agent implementation
│   └── main.py             # FastAPI application
└── docker-compose.yml      # Docker Compose configuration
```

## License

[MIT License](LICENSE)
