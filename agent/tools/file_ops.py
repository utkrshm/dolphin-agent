from pathlib import Path
from typing import Literal

# Point to outputs in the root directory
OUTPUT_DIRECTORY = Path(__file__).parent.parent.parent / "outputs"

def _check_location(path: Path):
    resolved_path = (OUTPUT_DIRECTORY / path).resolve()
    if not resolved_path.is_relative_to(OUTPUT_DIRECTORY.resolve()):
        raise PermissionError(f"{resolved_path} is outside the output directory, cannot allow access.")
    
    return resolved_path


# @tool
def read_file(file_name: str):
    path = _check_location(Path(file_name))
    
    if not path.exists():
        return f"Error: {path} does not exist."
    
    ext = path.suffix.lower()
    
    if ext == ".pdf":
        # TODO: Implement this function, using PyPDF
        raise NotImplementedError
    elif ext == ".docx":
        # TODO: Implement this using python-docx
        raise NotImplementedError
    else:
        return path.read_text(encoding="utf-8")


# @tool
def write_to_file(file_name: str, content: str, mode: Literal['write', 'append']):
    path = _check_location(Path(file_name))
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    
    file_mode = "a" if mode == "append" else "w"
    
    with path.open(mode=file_mode, encoding="utf-8") as f: 
        f.write(content)
    
    action = "Appended to" if mode == "append" else "Written to"
    return f"{action} '{file_name}' successfully - ({len(content)} characters)."
