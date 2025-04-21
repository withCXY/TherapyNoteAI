# Medical Conversation Analysis System

A web application for doctors to record, transcribe, and analyze patient conversations using AI.

## Features

- Record and transcribe doctor-patient conversations
- Generate structured summaries of conversations
- Generate medical reports using RAG framework
- Search and review previous conversations
- Export reports to PDF

## Prerequisites

- Docker and Docker Compose
- OpenAI API key

## Setup

1. Clone the repository
2. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

3. Build and start the services:
   ```bash
   docker-compose up --build
   ```

4. The backend API will be available at `http://localhost:8000`

## API Documentation

Once the services are running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage

1. Place medical case PDF files in the `backend/data/cases` directory
2. Use the API endpoints to:
   - Create new conversations
   - Upload audio recordings
   - Generate summaries and reports
   - Search previous conversations

## Development

To run the backend service in development mode:
```bash
cd backend
uvicorn main:app --reload
```

## License

MIT 