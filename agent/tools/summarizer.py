import os
import ollama
from dotenv import load_dotenv
from .file_ops import read_file

load_dotenv()

SYSTEM_PROMPT = """You are a precise summarizer. When given a text, you produce a clear and faithful summary that preserves the core ideas without omitting critical details. 
Your summary must:
- Be shorter than the original text
- Preserve the key points in the order they appear
- Never add information that isn't in the original
- Use plain, direct language"""

def summarize_file(file_name: str) -> str:
    """Summarize a file from outputs using the configured Ollama model.

    Args:
        file_name: Relative path of the file inside the outputs directory.

    Returns:
        A summary string, or an error string when the file cannot be read.

    Raises:
        Exception: If Ollama is unavailable, the model is missing, or another
            Ollama response error occurs.
    """

    model = os.getenv("SUMMARY_MODEL", "gemma3:1b")

    file_content = read_file(file_name)
    if file_content.startswith("Error:"):
        return file_content

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Summarize the following:\n\n{file_content}"}
            ]
        )

        return response["message"]["content"]
    except ollama.ResponseError as e:
        if e.status_code == 404:
            raise Exception("Cannot load Ollama service or model. Please check if that service is running and try again")
        else:
            raise Exception(f"Ollama error: {e.error}")