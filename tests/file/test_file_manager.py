import pytest
from pathlib import Path
from conf_manager.file.file_manager import FileManager

@pytest.fixture
def file_manager():
    return FileManager()

    test_file = tmp_path / "test.txt"
    test_content = "This is a test file."
    test_file.write_text(test_content)

def test_write_to_readonly_file(tmp_path, file_manager):
    # Create a readonly file
    readonly_file = tmp_path / "readonly.txt"
    readonly_file.write_text("Original content")
    readonly_file.chmod(0o444)  # Set file as read-only

    with pytest.raises(PermissionError):
        file_manager.write_file(str(readonly_file), "New content")
