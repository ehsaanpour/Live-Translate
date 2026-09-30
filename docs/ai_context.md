# AI Context File (Rules & Guidelines)

## Project Context
This is a modern Windows desktop application for Live Translation (Persian <-> English) written entirely in Python. It uses the Google Gemini Multimodal Live API for real-time audio translation. 

## Technology Stack
*   **Language:** Python 3.11+
*   **UI Framework:** `flet` (Provides Flutter-like declarative UI)
*   **Async/Concurrency:** `asyncio`
*   **WebSockets:** `websockets` library for connecting to Gemini.
*   **Audio I/O:** `pyaudio` or `sounddevice`.

## Architectural Guidelines
1.  **Strict Asynchronous Code:** Because we are maintaining a live WebSocket connection and streaming audio, *all* IO-bound code must be fully async. Do not use blocking `time.sleep()` or blocking loops inside the main thread. 
2.  **Decoupling:** Keep the Flet UI logic strictly separated from the Gemini API WebSocket logic and Audio capture logic. Use callbacks or `asyncio.Queue` to pass messages between the UI and the API.
3.  **Error Handling:** Assume the WebSocket might drop. Handle connection closures gracefully by resetting the UI state to "Disconnected" without crashing the app.

## UI / UX Rules
1.  **Modern Aesthetics:** Use Flet's Material 3 design features. Rely on smooth padding, rounded corners, and a clean dark/light mode adaptable layout.
2.  **Dual Column Focus:** The core UI element is the dual-column list (Persian on Left, English on Right). Ensure these lists auto-scroll to the bottom when new text arrives.
3.  **Mic Toggle:** The microphone button must clearly indicate its state (e.g., Red/Pulsing when recording, Grey when idle).

## API Integration Rules
*   **Endpoint:** Implement the Gemini Multimodal Live API using `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key=API_KEY`
*   **Setup Message:** The initial setup message sent to the API must configure the system instructions to act strictly as a Persian-English translator, define the requested voice, and set the response modalities to `["AUDIO", "TEXT"]`.
