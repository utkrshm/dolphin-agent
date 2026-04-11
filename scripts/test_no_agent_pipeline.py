from agent.tools.file_ops import read_file, write_to_file
from agent.tools.summarizer import summarize_file

from stt.record import start_recording, stop_recording
from stt.transcribe import load_model, transcribe

def test_recording() -> str:
    print("###### TEST: Recording ######")
    
    print("Beginning recording, press Enter to stop recording")
    start_recording()

    input()
    path = stop_recording()
    print("Recording stopped")
    
    return path


def test_transcribing(file_path) -> str:
    print("###### TEST: Transcribing ######")
        
    print("Beginning transcription")
    transcript = transcribe(file_path)
    print(f"Transcript returned: {transcript}")

    return transcript

def test_writing_and_reading_file(file_name: str, content: str, mode="write"):
    print("\n###### TEST: Writing to a file, then reading the content from it ######\n")

    print("Writing the transcript to the file")
    write_update = write_to_file(file_name, content, mode)
    print(f"Write to file response: {write_update}\n")
    
    print("Reading the content from the file")
    read_content = read_file(file_name)
    print(f"Content read: {read_content}\n")

    assert content == read_content, "The content transcribed is not the content from the file"


def test_summarization(file_name):
    print("\n###### TEST: Summarizing a file ######\n")

    print("Starting summarizing")
    summary = summarize_file(file_name)
    print(f"Summary response: {summary}")


if __name__ == "__main__":
    audio_path = test_recording()
    
    print("Loading Whisper model for transcription")
    load_model()

    text = test_transcribing(audio_path)
    
    test_writing_and_reading_file("no_agent_pipeline_sample.txt", text)
    test_summarization("no_agent_pipeline_sample.txt")