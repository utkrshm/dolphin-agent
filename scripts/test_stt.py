"""Test file to check whether the Audio Input + STT code is working"""
from stt.transcribe import load_model, transcribe
from stt.record import start_recording, stop_recording

if __name__ == "__main__":
    # Load whisper model
    print("Loading Whisper model")
    load_model("tiny")
    
    print("Model loaded.")
    
    start_recording()
    print("Starting stream... Press Enter when you're finished to stop recording")
    
    input()
    
    path = stop_recording()
    print("Recording stopped")
    
    print("Beginning transcription")
    transcript = transcribe(path)
    print(f"Transcribed text: {transcript}")