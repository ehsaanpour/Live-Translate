import flet as ft
import asyncio
from audio_handler import AudioHandler
from gemini_client import GeminiClient

class MainView(ft.Container):
    def __init__(self, page: ft.Page):
        self.main_page = page
        self.audio_handler = AudioHandler()
        
        # --- Settings Components ---
        devices = AudioHandler.get_input_devices()
        self.audio_dropdown = ft.Dropdown(
            label="Audio Input Source",
            options=[ft.dropdown.Option(key=str(d['index']), text=d['name']) for d in devices],
            width=400
        )
        if devices:
            self.audio_dropdown.value = str(devices[0]['index'])
            self.audio_handler.set_device(devices[0]['index'])

        self.api_key_input = ft.TextField(
            label="Gemini API Key", 
            password=True, 
            can_reveal_password=True, 
            width=400
        )
        
        self.model_dropdown = ft.Dropdown(
            label="AI Model",
            options=[ft.dropdown.Option("models/gemini-3.1-flash-live-preview")],
            value="models/gemini-3.1-flash-live-preview",
            width=400
        )
        
        self.check_status_text = ft.Text(color=ft.Colors.GREEN)

        self.settings_dialog = ft.AlertDialog(
            title=ft.Text("Settings"),
            content=ft.Column([
                self.api_key_input,
                ft.Row([
                    ft.FilledButton("Check API Key", on_click=self.check_api_key),
                    self.check_status_text
                ]),
                self.model_dropdown,
                self.audio_dropdown,
            ], tight=True),
            actions=[
                ft.TextButton("Accept", on_click=self.close_settings)
            ]
        )
        self.main_page.overlay.append(self.settings_dialog)
        
        # Main App Bar for Title and Settings Icon
        self.main_page.appbar = ft.AppBar(
            title=ft.Text("Live Translation", size=24, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.SURFACE,
            actions=[
                ft.IconButton(ft.Icons.SETTINGS, on_click=self.open_settings)
            ]
        )

        # --- Main View Components ---
        self.voice_selector = ft.Dropdown(
            label="Voice",
            options=[ft.dropdown.Option(x) for x in ["Aoede", "Charon", "Fenrir", "Kore", "Puck"]],
            value="Aoede",
            width=200,
        )
        
        self.mic_toggle = ft.FloatingActionButton(icon=ft.Icons.MIC_OFF, on_click=self.toggle_mic, bgcolor=ft.Colors.GREY_700)
        
        # Audio Visualizer
        self.audio_visualizer = ft.ProgressBar(width=150, value=0.0, color=ft.Colors.GREEN_500, bgcolor=ft.Colors.GREY_800)
        
        self.control_bar = ft.Row(
            controls=[
                self.voice_selector, 
                ft.Row([ft.Icon(ft.Icons.VOLUME_UP, color=ft.Colors.GREY_500), self.audio_visualizer]), 
                self.mic_toggle
            ],
            alignment=ft.MainAxisAlignment.END
        )

        self.persian_list = ft.ListView(spacing=10, auto_scroll=True, expand=True)
        self.english_list = ft.ListView(spacing=10, auto_scroll=True, expand=True)

        self.transcript_columns = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text("Persian (فارسی)", weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_400),
                        self.persian_list
                    ]),
                    expand=True, 
                    bgcolor=ft.Colors.GREY_900, 
                    padding=10,
                    border_radius=10,
                    border=ft.Border.all(1, ft.Colors.OUTLINE)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("English", weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_400),
                        self.english_list
                    ]),
                    expand=True, 
                    bgcolor=ft.Colors.GREY_900, 
                    padding=10,
                    border_radius=10,
                    border=ft.Border.all(1, ft.Colors.OUTLINE)
                )
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH
        )

        super().__init__(
            expand=True,
            padding=10,
            content=ft.Column(
                expand=True,
                controls=[
                    self.control_bar,
                    self.transcript_columns
                ]
            )
        )
        self.is_recording = False
        self.audio_handler.set_volume_callback(self.update_visualizer)

    def open_settings(self, e):
        self.settings_dialog.open = True
        self.main_page.update()

    def close_settings(self, e):
        self.settings_dialog.open = False
        if self.audio_dropdown.value:
            self.audio_handler.set_device(int(self.audio_dropdown.value))
        self.main_page.update()

    def check_api_key(self, e):
        import urllib.request
        import json
        key = self.api_key_input.value
        if not key:
            self.check_status_text.value = "Enter API Key!"
            self.check_status_text.color = ft.Colors.RED
            self.main_page.update()
            return
            
        self.check_status_text.value = "Checking..."
        self.check_status_text.color = ft.Colors.YELLOW
        self.main_page.update()
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    try:
                        data = json.loads(response.read().decode('utf-8'))
                        # Filter for models that support bidiGenerateContent
                        bidi_models = []
                        for m in data.get('models', []):
                            methods = m.get('supportedGenerationMethods', [])
                            if 'bidiGenerateContent' in methods:
                                bidi_models.append(m['name'])
                        
                        # Ensure known live models are always available
                        known_live_models = ['models/gemini-3.1-flash-live-preview', 'models/gemini-3.5-live-translate-preview', 'models/gemini-2.0-flash']
                        for km in known_live_models:
                            if km not in bidi_models:
                                bidi_models.insert(0, km)
                            
                        self.model_dropdown.options = [ft.dropdown.Option(m) for m in bidi_models]
                        if self.model_dropdown.value not in bidi_models:
                            self.model_dropdown.value = "models/gemini-3.1-flash-live-preview"
                    except Exception as e:
                        print("Error parsing models:", e)
                    
                    self.check_status_text.value = "Valid Key!"
                    self.check_status_text.color = ft.Colors.GREEN
        except Exception as ex:
            self.check_status_text.value = "Invalid Key"
            self.check_status_text.color = ft.Colors.RED
        self.main_page.update()

    def update_visualizer(self, volume: float):
        self.audio_visualizer.value = volume
        try:
            self.audio_visualizer.update()
        except Exception:
            pass # ignore update errors during shutdown

    async def toggle_mic(self, e):
        self.is_recording = not self.is_recording
        if self.is_recording:
            try:
                key = self.api_key_input.value
                if not key:
                    self.is_recording = False
                    self.settings_dialog.open = True
                    self.main_page.update()
                    return

                print(f"Starting Gemini Client with voice {self.voice_selector.value}", flush=True)
                self.gemini_client = GeminiClient(
                    api_key=key, 
                    voice=self.voice_selector.value, 
                    model=self.model_dropdown.value or "models/gemini-3.1-flash-live-preview"
                )

                self.mic_toggle.icon = ft.Icons.MIC
                self.mic_toggle.bgcolor = ft.Colors.RED_500
                self.main_page.update()

                await self.audio_handler.start()
                print("Audio handler started, creating session task", flush=True)

                # Start the monolithic session
                self.session_task = asyncio.create_task(
                    self.gemini_client.run_session(
                        self.audio_handler.input_queue,
                        self.on_text,
                        self.on_audio
                    )
                )
            except Exception as e:
                print(f"Error starting mic: {e}", flush=True)
                import traceback
                traceback.print_exc()
        else:
            self.mic_toggle.icon = ft.Icons.MIC_OFF
            self.mic_toggle.bgcolor = ft.Colors.GREY_700
            self.audio_visualizer.value = 0.0
            self.main_page.update()

            if hasattr(self, 'session_task'):
                self.session_task.cancel()
            
            # Send sentinel to queue
            self.audio_handler.input_queue.put_nowait(None)
            await self.audio_handler.stop()

    async def on_text(self, text: str):
        is_persian = any('\u0600' <= c <= '\u06FF' for c in text)
        self.add_transcript(text, "fa" if is_persian else "en")

    async def on_audio(self, audio_data: bytes):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.audio_handler.play_audio, audio_data)

    def add_transcript(self, text: str, lang: str):
        if lang == "fa":
            self.persian_list.controls.append(ft.Text(text))
        elif lang == "en":
            self.english_list.controls.append(ft.Text(text))
        self.main_page.update()
