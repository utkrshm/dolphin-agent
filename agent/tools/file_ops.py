from pathlib import Path
from typing import Literal

# Point to outputs in the root directory
OUTPUT_DIRECTORY = Path(__file__).parent.parent.parent / "outputs"

def _check_location(path: Path):
    resolved_path = (OUTPUT_DIRECTORY / path).resolve()
    if not resolved_path.is_relative_to(OUTPUT_DIRECTORY.resolve()):
        raise PermissionError(f"{resolved_path} is outside the output directory, cannot allow access.")
    
    return resolved_path


def read_file(file_name: str):
    """Read a file from the outputs directory and return its contents.

    Args:
        file_name: Relative path of the file inside the outputs directory.

    Returns:
        The file contents as a UTF-8 string, or an error string if the file
        does not exist.
    """
    
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


def write_to_file(file_name: str, content: str, mode: Literal['write', 'append']):
    """Write or append text content to a file in the outputs directory.

    Args:
        file_name: Relative path of the target file inside the outputs directory.
        content: Text content to write.
        mode: Either "write" to overwrite or "append" to add to the file.

    Returns:
        A status string describing what action was performed.

    Notes:
        Access is restricted to the outputs directory.
    """
    
    path = _check_location(Path(file_name))
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    
    file_mode = "a" if mode == "append" else "w"
    
    with path.open(mode=file_mode, encoding="utf-8") as f: 
        f.write(content)
    
    action = "Appended to" if mode == "append" else "Written to"
    return f"{action} '{file_name}' successfully - ({len(content)} characters)."
