# Product Requirements Document (PRD)
**Project Name:** Live Translation Windows App
**Platform:** Windows Desktop (Python)
**Core Tech:** Google Gemini Multimodal Live API

## 1. Objective
To build a modern, beautiful, and low-latency real-time translation application for Windows. The app will facilitate seamless live communication between Persian and English speakers by translating spoken words into both text and spoken audio in real-time.

## 2. Target Audience
Users who need real-time, hands-free translation during conversations, meetings, or media consumption on their Windows PC without incurring high API costs.

## 3. Core Features
*   **Real-Time Live Translation:** Translates audio between Persian and English instantly.
*   **Dual-Column Text Display:** A running transcript visually separated into two columns (Left: Persian, Right: English) so users can track the conversation clearly.
*   **Toggle Microphone Interaction:** A prominent UI button to start and stop continuous listening.
*   **Voice Customization:** Users can change the speaker's voice using the available Gemini Live API preset voices (e.g., Aoede, Charon, Fenrir, Kore, Puck).
*   **Audio Playback:** The translated response is spoken aloud through the computer's speakers.

## 4. Non-Functional Requirements
*   **Design:** Must have a beautiful, modern layout (Material Design) leveraging the Flet framework.
*   **Cost:** Must utilize the Google Gemini Multimodal Live API (Google AI Studio) to take advantage of generous free tiers.
*   **Performance:** The app must be responsive, non-blocking, and minimize audio latency.

## 5. User Flow
1. User launches the app and inputs their Gemini API Key (if not saved).
2. User selects their preferred AI Voice from a dropdown menu.
3. User clicks the "Microphone" toggle button to start listening.
4. User speaks in either Persian or English.
5. The UI updates the Dual-Column view with the live transcript of the original and translated text.
6. The app plays the translated audio back to the user.
7. User clicks the Microphone toggle to stop listening.
