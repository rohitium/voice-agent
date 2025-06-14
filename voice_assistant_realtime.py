import os
import json
import websocket
import numpy as np
import sounddevice as sd
import asyncio
import threading
import queue
import time

# Audio settings
SAMPLERATE = 24000
CHANNELS = 1
DTYPE = 'int16'

# WebSocket settings
WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
HEADERS = [
    f"Authorization: Bearer {os.environ.get('OPENAI_API_KEY')}",
    "OpenAI-Beta: realtime=v1"
]

class VoiceAssistant:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.ws = None
        self.setup_websocket()

    def setup_websocket(self):
        self.ws = websocket.WebSocketApp(
            WS_URL,
            header=HEADERS,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

    def on_open(self, ws):
        print("Connected to OpenAI realtime API")
        # Start the WebSocket connection in a separate thread
        threading.Thread(target=self.ws.run_forever).start()

    def on_message(self, ws, message):
        data = json.loads(message)
        if data.get("type") == "audio":
            # Handle audio response
            audio_data = np.frombuffer(data["audio"], dtype=np.int16)
            sd.play(audio_data, SAMPLERATE)
            sd.wait()
        elif data.get("type") == "text":
            # Handle text response
            print(f"\nAssistant: {data['text']}")

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")
        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def start_recording(self):
        print("\nRecording... Press Enter to stop")
        self.is_recording = True
        recorded_chunks = []

        with sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS, dtype=DTYPE, 
                          callback=self.audio_callback):
            input()

        self.is_recording = False
        print("Processing...")

        # Concatenate all recorded chunks
        while not self.audio_queue.empty():
            recorded_chunks.append(self.audio_queue.get())

        if not recorded_chunks:
            print("No audio recorded. Please try again.")
            return None

        return np.concatenate(recorded_chunks, axis=0)

    def send_audio(self, audio_data):
        if audio_data is not None:
            # Convert audio to bytes and send
            audio_bytes = audio_data.tobytes()
            self.ws.send(json.dumps({
                "type": "audio",
                "audio": audio_bytes.hex(),
                "sample_rate": SAMPLERATE
            }))

    def run(self):
        print("Voice Assistant Ready!")
        print("Press Enter to start recording (or type 'esc' to exit)")
        
        while True:
            cmd = input()
            if cmd.lower() == "esc":
                print("Exiting...")
                self.ws.close()
                break

            # Record audio
            audio_data = self.start_recording()
            
            # Send audio to OpenAI
            if audio_data is not None:
                self.send_audio(audio_data)

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run() 