import asyncio
from google import genai
from google.genai import types

class GeminiClient:
    def __init__(self, api_key: str, voice: str, model: str = "models/gemini-2.0-flash-exp"):
        self.api_key = api_key
        self.voice = voice
        # The genai SDK expects model without 'models/' prefix
        self.model = model.replace("models/", "")
        self.client = genai.Client(api_key=api_key)
        self.session = None

    async def connect(self):
        config = types.LiveConnectParameters(
            response_modalities=["AUDIO", "TEXT"],
            system_instruction=types.Content(parts=[
                types.Part.from_text("You are a real-time translator between Persian and English. Whatever I say in Persian, you translate to English. Whatever I say in English, you translate to Persian.")
            ]),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=self.voice
                    )
                )
            )
        )
        # We need to maintain the context manager open while receiving
        # Instead of 'async with' here, we'll open it manually or wrap the receive loop
        pass

    async def run_session(self, input_queue: asyncio.Queue, text_callback, audio_callback):
        config = types.LiveConnectParameters(
            response_modalities=["AUDIO", "TEXT"],
            system_instruction=types.Content(parts=[
                types.Part.from_text("You are a real-time translator between Persian and English. Whatever I say in Persian, you translate to English. Whatever I say in English, you translate to Persian.")
            ]),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=self.voice
                    )
                )
            )
        )
        
        async def send_loop(session):
            try:
                while True:
                    chunk = await input_queue.get()
                    if chunk is None: # sentinel
                        break
                    await session.send_realtime_input(
                        media=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
                    )
            except asyncio.CancelledError:
                pass

        try:
            async with self.client.aio.live.connect(model=self.model, config=config) as session:
                self.session = session
                send_task = asyncio.create_task(send_loop(session))
                
                async for message in session.receive():
                    if message.text:
                        await text_callback(message.text)
                    # Using the latest SDK message structure for audio (inline_data usually)
                    if hasattr(message, "inline_data") and message.inline_data:
                        await audio_callback(message.inline_data.data)
                    # Some versions use server_content
                    if hasattr(message, "server_content") and message.server_content:
                        model_turn = message.server_content.model_turn
                        if model_turn:
                            for part in model_turn.parts:
                                if part.inline_data:
                                    await audio_callback(part.inline_data.data)
                                    
                send_task.cancel()
        except Exception as e:
            print(f"GenAI Live Session Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.session = None

    async def send_audio_chunk(self, pcm_data: bytes):
        # We use input_queue in run_session now, so this is unused
        pass

    async def receive_messages(self, text_callback, audio_callback):
        # Also unused directly
        pass

    async def close(self):
        # Cancellation is handled in the UI
        pass

