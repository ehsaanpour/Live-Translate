# Software Requirements Specification (SRS)

## 1. Introduction
This document specifies the software requirements for the Live Translation Windows App, a Python-based desktop application utilizing the Google Gemini Multimodal Live API.

## 2. Functional Requirements

### 2.1 Audio Processing
*   **REQ-001 (Microphone Input):** The system shall capture continuous raw audio from the default Windows microphone at a sample rate compatible with Gemini (e.g., 16kHz or 24kHz PCM).
*   **REQ-002 (Audio Playback):** The system shall playback raw PCM audio streams received from the Gemini API through the default Windows speaker.

### 2.2 Network & API
*   **REQ-003 (WebSocket Connection):** The system shall establish an asynchronous WebSocket connection to the Gemini Multimodal Live API endpoint.
*   **REQ-004 (Bidirectional Streaming):** The system shall send base64-encoded audio chunks to the API and simultaneously receive text and audio responses.

### 2.3 User Interface (Flet)
*   **REQ-005 (Dual Column Layout):** The UI shall contain a left scrollable column for Persian text and a right scrollable column for English text.
*   **REQ-006 (Toggle Button):** A visual button shall control the active state of the microphone recording and websocket streaming.
*   **REQ-007 (Settings Panel):** The UI shall provide a dropdown to select the active Gemini Voice (Aoede, Charon, Fenrir, Kore, Puck) and an input field for the API key.

## 3. External Interfaces
*   **Software Framework:** Flet (Python UI framework based on Flutter).
*   **API Provider:** Google Gemini API (`wss://generativelanguage.googleapis.com/...`).
*   **Audio Libraries:** `sounddevice` or `pyaudio` for audio I/O.

## 4. Hardware Requirements
*   **OS:** Windows 10/11.
*   **Peripherals:** Working microphone and speakers/headphones.
*   **Network:** Stable internet connection for WebSocket streaming.
