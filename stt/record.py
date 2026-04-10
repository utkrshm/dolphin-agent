import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile

_recording = []
_stream = None

def _callback(indata, frames, time, status):
    _recording.append(indata.copy())

def start_recording():
    global _stream, _recording
    _recording = []
    _stream = sd.InputStream(samplerate=16000, channels=1, callback=_callback)
    _stream.start()
    print("Recording... press Enter to stop.")

def stop_recording() -> str:
    global _stream
    _stream.stop()
    _stream.close()
    audio = np.concatenate(_recording, axis=0)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav.write(tmp.name, 16000, audio)
    return tmp.name