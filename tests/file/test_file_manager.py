import pytest
from pathlib import Path
from conf_manager.file.file_manager import FileManager

@pytest.fixture
def file_manager():
    return FileManager()

def test_read_file(tmp_path, file_manager):
    # Create a temporary file
    test_file = tmp_path / "test.txt"
    test_content = "This is a test file."
    test_file.write_text(test_content)

    # Read the file
    content = file_manager.read_file(str(test_file))
    assert content == test_content

def test_write_file(tmp_path, file_manager):
    # Define file path and content
    test_file = tmp_path / "test_write.txt"
    test_content = "This is a test write operation."

    # Write to the file
    file_manager.write_file(str(test_file), test_content)

    # Verify the file was written correctly
    assert test_file.read_text() == test_content

def test_backup_file(tmp_path, file_manager):
    # Create a file to backup
    original_file = tmp_path / "original.txt"
    original_content = "This is the original file."
    original_file.write_text(original_content)

    # Backup the file
    backup_path = file_manager.backup_file(str(original_file))

    # Check if backup file exists and contains the correct content
    assert Path(backup_path).exists()
    assert Path(backup_path).read_text() == original_content

def test_backup_file_multiple_times(tmp_path, file_manager):
    # Create a file to backup
    original_file = tmp_path / "original.txt"
    original_content = "This is the original file."
    original_file.write_text(original_content)

    # Backup the file multiple times
    for i in range(3):
        backup_path = file_manager.backup_file(str(original_file))
        assert Path(backup_path).exists()
        assert Path(backup_path).read_text() == original_content

    # Check if we have the expected number of backups
    backups = list(tmp_path.glob("original.txt.bak*"))
    assert len(backups) == 3

def test_read_nonexistent_file(tmp_path, file_manager):
    non_existent_file = tmp_path / "nonexistent.txt"
    with pytest.raises(FileNotFoundError):
        file_manager.read_file(str(non_existent_file))

def test_write_to_readonly_file(tmp_path, file_manager):
    # Create a readonly file
    readonly_file = tmp_path / "readonly.txt"
    readonly_file.write_text("Original content")
    readonly_file.chmod(0o444)  # Set file as read-only

    with pytest.raises(PermissionError):
        file_manager.write_file(str(readonly_file), "New content")