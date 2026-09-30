import asyncio
import websockets
import json
import base64

class GeminiClient:
    def __init__(self, api_key: str, voice: str, model: str = "models/gemini-2.0-flash"):
        self.api_key = api_key
        self.voice = voice
        self.model = model
        self.ws = None
        self.uri = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key={self.api_key}"

    async def connect(self):
        self.ws = await websockets.connect(self.uri)
        await self._send_setup_message()

    async def _send_setup_message(self):
        setup_message = {
            "setup": {
                "model": self.model,
                "systemInstruction": {
                    "parts": [{"text": "You are a real-time translator between Persian and English. Whatever I say in Persian, you translate to English. Whatever I say in English, you translate to Persian."}]
                },
                "generationConfig": {
                    "responseModalities": ["AUDIO", "TEXT"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {
                                "voiceName": self.voice
                            }
                        }
                    }
                }
            }
        }
        await self.ws.send(json.dumps(setup_message))

    async def send_audio_chunk(self, pcm_data: bytes):
        if not self.ws:
            return
        
        b64_data = base64.b64encode(pcm_data).decode("utf-8")
        msg = {
            "realtimeInput": {
                "mediaChunks": [
                    {
                        "mimeType": "audio/pcm;rate=16000",
                        "data": b64_data
                    }
                ]
            }
        }
        await self.ws.send(json.dumps(msg))

    async def receive_messages(self, text_callback, audio_callback):
        if not self.ws:
            return

        try:
            async for message in self.ws:
                data = json.loads(message)
                # Handle incoming server content
                if "serverContent" in data:
                    model_turn = data["serverContent"].get("modelTurn")
                    if model_turn:
                        for part in model_turn.get("parts", []):
                            if "text" in part:
                                await text_callback(part["text"])
                            elif "inlineData" in part:
                                # Audio response
                                audio_b64 = part["inlineData"].get("data")
                                if audio_b64:
                                    audio_bytes = base64.b64decode(audio_b64)
                                    await audio_callback(audio_bytes)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed.")

    async def close(self):
        if self.ws:
            await self.ws.close()
            self.ws = None
