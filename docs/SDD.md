# System Design Document (SDD)

## 1. Architecture Overview
The application will follow an asynchronous, event-driven architecture using Python's `asyncio`. The frontend will be rendered by the `flet` library, while the backend logic will handle audio buffering and WebSocket communication concurrently without blocking the UI.

## 2. System Components

### 2.1 UI Layer (app.py / ui.py)
*   **Role:** Handles all visual rendering, user inputs, and updating transcript text in real-time.
*   **Components:**
    *   `MainView`: Contains the overall layout.
    *   `TranscriptColumns`: A responsive Flet Row containing two `ListView` controls (Persian and English).
    *   `ControlBar`: Contains the Mic Toggle Button and Voice Selector dropdown.

### 2.2 Audio Manager (audio_handler.py)
*   **Role:** Manages the hardware microphone and speaker.
*   **Input:** Uses an async-compatible input stream to capture audio chunks (e.g., 1024 frames) and pushes them to a queue.
*   **Output:** Reads decoded PCM audio chunks from an output queue and plays them through a sound stream.

### 2.3 API Client (gemini_client.py)
*   **Role:** Manages the connection to the Google Gemini Multimodal Live API.
*   **Tasks:**
    *   Initialize the WebSocket connection with the selected System Instructions (acting as a translator) and Voice configuration.
    *   Task 1 (Sender): Pulls audio chunks from the Audio Manager queue, serializes them to JSON, and sends them over the WebSocket.
    *   Task 2 (Receiver): Listens to the WebSocket, parses incoming JSON.
        *   If it receives Text: Fires an event to update the UI Layer.
        *   If it receives Audio: Pushes the PCM data to the Audio Manager playback queue.

## 3. Data Flow
1. **User Speaks:** Microphone -> `audio_handler` queue.
2. **Streaming:** `gemini_client` reads queue -> encodes to Base64 -> sends via WebSocket.
3. **Receiving:** Gemini processes audio -> sends JSON response via WebSocket.
4. **Routing:** `gemini_client` splits response:
   *   Text payload -> Sent to UI via callback -> Renders in Dual Columns.
   *   Audio payload -> Sent to `audio_handler` -> Speaker plays translated voice.

## 4. Error Handling
*   **Connection Drops:** If the WebSocket disconnects, the UI must display an error toast and reset the Mic toggle to OFF.
*   **Missing API Key:** Prompt the user to enter the key before allowing the microphone to activate.
