import asyncio
import sounddevice as sd
import numpy as np

class AudioHandler:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()
        self.is_running = False
        self._input_stream = None
        self._output_stream = None
        self.device_index = None
        self.volume_callback = None

    @staticmethod
    def get_input_devices():
        devs = sd.query_devices()
        return [d for d in devs if d['max_input_channels'] > 0]

    def set_device(self, device_index):
        self.device_index = device_index

    def set_volume_callback(self, callback):
        """Callback should be a normal function receiving a float 0.0 - 1.0"""
        self.volume_callback = callback

    async def start(self):
        self.is_running = True
        loop = asyncio.get_running_loop()

        def _input_callback(indata, frames, time, status):
            if status:
                print(status)
            if self.is_running:
                # Calculate RMS volume for visualization
                if self.volume_callback:
                    # Convert raw buffer to int16 numpy array, then to float32
                    indata_np = np.frombuffer(indata, dtype=np.int16)
                    indata_float = indata_np.astype(np.float32)
                    rms = np.sqrt(np.mean(np.square(indata_float)))
                    vol = float(rms) / 32768.0
                    vol = min(1.0, max(0.0, vol * 5.0))
                    loop.call_soon_threadsafe(self.volume_callback, vol)

                loop.call_soon_threadsafe(self.input_queue.put_nowait, bytes(indata))

        self._input_stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16',
            callback=_input_callback,
            blocksize=1024,
            device=self.device_index
        )
        self._input_stream.start()

        # Output stream for Gemini's 24kHz audio responses
        self._output_stream = sd.RawOutputStream(
            samplerate=24000,
            channels=1,
            dtype='int16'
        )
        self._output_stream.start()

    def play_audio(self, audio_data: bytes):
        if self._output_stream and self.is_running:
            try:
                self._output_stream.write(audio_data)
            except Exception as e:
                print(f"Error playing audio: {e}")

    async def stop(self):
        self.is_running = False
        if self._input_stream:
            self._input_stream.stop()
            self._input_stream.close()
            self._input_stream = None
        if self._output_stream:
            self._output_stream.stop()
            self._output_stream.close()
            self._output_stream = None
        if self.volume_callback:
            # reset visualizer
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(self.volume_callback, 0.0)
