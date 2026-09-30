import asyncio
import sys
import os
import json
import base64

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from gemini_client import GeminiClient

async def test_gemini():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Set GEMINI_API_KEY env var to test.")
        return
        
    client = GeminiClient(api_key, "Aoede")
    print("Connecting...")
    await client.connect()
    print("Connected! Sending audio...")
    
    # Send a dummy clientContent text message just to see if it responds!
    msg = {
        "clientContent": {
            "turns": [
                {
                    "role": "user",
                    "parts": [{"text": "Hello, how are you? Translate this to Persian."}]
                }
            ],
            "turnComplete": True
        }
    }
    await client.ws.send(json.dumps(msg))
    
    # Wait for response
    async def txt_cb(text):
        print(f"TEXT RECEIVED: {text}")
        
    async def aud_cb(audio):
        print(f"AUDIO RECEIVED: {len(audio)} bytes")
        
    try:
        await asyncio.wait_for(client.receive_messages(txt_cb, aud_cb), timeout=5.0)
    except asyncio.TimeoutError:
        print("Timeout waiting for response")
    
if __name__ == "__main__":
    asyncio.run(test_gemini())
