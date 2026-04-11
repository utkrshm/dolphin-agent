# scripts/test_tools.py

"""
Layer 1 tool tests.
Run from project root: uv run python -m scripts.test_tools
"""

from agent.tools.file_ops import read_file, write_to_file
from agent.tools.summarizer import summarize_file


def test_write_and_read_text():
    print("--- Test: Write then Read a text file ---")

    write_result = write_to_file("test_sample.txt", "Hello, this is a test file.\nIt has two lines.")
    print(f"Write result: {write_result}")
    assert "Written to" in write_result, "Write failed"

    read_result = read_file("test_sample.txt")
    print(f"Read result: {read_result}")
    assert read_result == "Hello, this is a test file.\nIt has two lines.", "Read content mismatch"

    print("PASSED\n")


def test_read_nonexistent_file():
    print("--- Test: Read a file that doesn't exist ---")

    result = read_file("ghost_file.txt")
    print(f"Result: {result}")
    assert result.startswith("Error:"), "Expected an error string for missing file"

    print("PASSED\n")


def test_jail_check():
    print("--- Test: Path traversal attempt ---")

    try:
        result = read_file("../../etc/passwd")
        assert result.startswith("Error:") or "denied" in result.lower()
        print(f"Result: {result}")
    except PermissionError as e:
        print(f"Correctly raised PermissionError: {e}")

    print("PASSED\n")


def test_summarize_file():
    print("--- Test: Summarize a text file ---")

    content = (
        "The mitochondria is the powerhouse of the cell. "
        "It produces ATP through a process called cellular respiration. "
        "Without mitochondria, cells would not have the energy required to function. "
        "They also play a role in regulating cell death, known as apoptosis."
    )
    write_to_file("test_summary_input.txt", content)

    result = summarize_file("test_summary_input.txt")
    print(f"Summary result:\n{result}")

    assert not result.startswith("Error:"), "Summarizer returned an error"
    assert len(result) > 0, "Summary is empty"
    assert len(result) < len(content), "Summary should be shorter than the original"

    print("PASSED\n")


def test_summarize_nonexistent_file():
    print("--- Test: Summarize a file that doesn't exist ---")

    result = summarize_file("ghost_file.txt")
    print(f"Result: {result}")
    assert result.startswith("Error:"), "Expected error to propagate from read_file"

    print("PASSED\n")


if __name__ == "__main__":
    test_write_and_read_text()
    test_read_nonexistent_file()
    test_jail_check()
    test_summarize_file()
    test_summarize_nonexistent_file()
    print("All tests passed.")