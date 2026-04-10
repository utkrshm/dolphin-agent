import whisper

_model = None

def load_model(model_size="base"):
    global _model
    _model = whisper.load_model(model_size)
    

def transcribe(audio_path: str):
    if _model is None:
        return Exception("The whisper model has not been initiated yet")
    
    transcription = _model.transcribe(
        audio=audio_path, 
        word_timestamps=False
    )

    return transcription['text']