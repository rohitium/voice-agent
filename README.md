# Voice Assistant for ACME Shop

This is a voice-enabled assistant for ACME Shop that can help users with account information, product knowledge, and real-time web searches.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

3. For the Knowledge Agent to work, you'll need to create a vector store:
```bash
python vector_store_utils.py
```
This will create a vector store and upload the product catalog. Note the vector store ID from the output and update it in `voice_assistant.py`.

## Usage

Run the voice assistant:
```bash
python voice_assistant.py
```

The assistant will:
1. Wait for you to press Enter to start recording
2. Record your voice input until you press Enter again
3. Process your query and respond with voice output
4. Type 'esc' to exit the program

## Features

- **Account Agent**: Provides account information using a dummy function
- **Knowledge Agent**: Answers questions about products using vector store search
- **Search Agent**: Performs real-time web searches for up-to-date information
- **Triage Agent**: Routes queries to the appropriate specialized agent

## Voice Customization

The assistant uses a friendly, warm tone optimized for voice interaction. You can customize the voice settings by modifying the `custom_tts_settings` in `voice_assistant.py`. 