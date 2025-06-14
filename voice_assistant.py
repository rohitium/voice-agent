import os
from agents import Agent, trace, function_tool, WebSearchTool, FileSearchTool, set_default_openai_key
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.voice import AudioInput, SingleAgentVoiceWorkflow, VoicePipeline, TTSModelSettings, VoicePipelineConfig
import numpy as np
import sounddevice as sd

# Set OpenAI API key from environment variable
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# --- Tool 1: Fetch account information (dummy) ---
@function_tool
def get_account_info(user_id: str) -> dict:
    """Return dummy account info for a given user."""
    return {
        "user_id": user_id,
        "name": "Bugs Bunny",
        "account_balance": "£72.50",
        "membership_status": "Gold Executive"
    }

# --- Agent: Search Agent ---
search_agent = Agent(
    name="SearchAgent",
    instructions=(
        "You immediately provide an input to the WebSearchTool to find up-to-date information on the user's query."
    ),
    tools=[WebSearchTool()],
)

# --- Agent: Knowledge Agent ---
knowledge_agent = Agent(
    name="KnowledgeAgent",
    instructions=(
        "You answer user questions on our product portfolio with concise, helpful responses using the FileSearchTool."
    ),
    tools=[FileSearchTool(
            max_num_results=3,
            vector_store_ids=["vs_684d08ec736081919e5054369da78030"],
        ),],
)

# --- Agent: Account Agent ---
account_agent = Agent(
    name="AccountAgent",
    instructions=(
        "You provide account information based on a user ID using the get_account_info tool."
    ),
    tools=[get_account_info],
)

# --- Agent: Triage Agent ---
triage_agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions("""
You are the virtual assistant for Acme Shop. Welcome the user and ask how you can help.
Based on the user's intent, route to:
- AccountAgent for account-related queries
- KnowledgeAgent for product FAQs
- SearchAgent for anything requiring real-time web search
"""),
    handoffs=[account_agent, knowledge_agent, search_agent],
)

async def voice_assistant():
    # Use standard CD quality sample rate
    samplerate = 24000
    
    # Custom TTS settings for a deeper, slower voice
    tts_settings = TTSModelSettings(
        instructions="Personality: upbeat, friendly, persuasive guide"
    "Tone: Friendly, clear, and reassuring, creating a calm atmosphere and making the listener feel confident and comfortable."
    "Pronunciation: Clear, articulate, and steady, ensuring each instruction is easily understood while maintaining a natural, conversational flow."
    "Tempo: Speak relatively fast, include brief pauses and after before questions"
    "Emotion: Warm and supportive, conveying empathy and care, ensuring the listener feels guided and safe throughout the journey."
    )
    voice_pipeline_config = VoicePipelineConfig(tts_settings=tts_settings)

    while True:
        pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(triage_agent), config=voice_pipeline_config)

        # Check for input to either provide voice or exit
        cmd = input("Press Enter to start recording (or type 'esc' to exit): ")
        if cmd.lower() == "esc":
            print("Exiting...")
            break       
        print("Recording... Press Enter again to stop recording")
        recorded_chunks = []

        # Start streaming from microphone with fixed sample rate
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', callback=lambda indata, frames, time, status: recorded_chunks.append(indata.copy())):
            input()

        if not recorded_chunks:
            print("No audio recorded. Please try again.")
            continue

        print("\nProcessing your request...")
        print("1. Converting speech to text...")
        
        # Concatenate chunks into single buffer
        recording = np.concatenate(recorded_chunks, axis=0)

        # Input the buffer and await the result
        audio_input = AudioInput(buffer=recording)

        print("2. Analyzing your request...")
        with trace("ACME App Voice Assistant"):
            result = await pipeline.run(audio_input)

        print("3. Generating response...")
        # Transfer the streamed result into chunks of audio
        response_chunks = []
        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                response_chunks.append(event.data)

        response_audio = np.concatenate(response_chunks, axis=0)

        # Play response with the same sample rate
        print("4. Speaking response...")
        sd.play(response_audio, samplerate=samplerate)
        sd.wait()
        print("---\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(voice_assistant()) 