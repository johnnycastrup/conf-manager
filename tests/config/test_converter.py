import pytest
from conf_manager.config.converter import ConfigConverter
import yaml
from pathlib import Path

def test_convert_to_override(tmp_path):
    # Create a mock config file
    config_file = tmp_path / "test_config.conf"
    config_file.write_text("key1=value1\nkey2=value2")

    # Create a mock override directory
    override_dir = tmp_path / "override.d"
    override_dir.mkdir()

    # Initialize the converter
    converter = ConfigConverter()

    # Convert the config file
    yaml_file_path = converter.convert_to_override(str(config_file), str(override_dir))

    # Check if the YAML file was created
    yaml_file = override_dir / "test_config.yml"
    assert yaml_file.exists()
    assert yaml_file_path == str(yaml_file)

    # Verify the content of the YAML file
    with yaml_file.open() as f:
        data = yaml.safe_load(f)
        assert data == {"key1": "value1", "key2": "value2"}

def test_convert_file_with_comments_and_empty_lines(tmp_path):
    # Create a mock config file with comments and empty lines
    config_file = tmp_path / "test_config.conf"
    config_file.write_text("""
    # This is a comment
    key1 = value1

    # Another comment
    key2 = value2

    # Empty line above
    """)

    # Create a mock override directory
    override_dir = tmp_path / "override.d"
    override_dir.mkdir()

    # Initialize the converter
    converter = ConfigConverter()

    # Convert the config file
    yaml_file_path = converter.convert_to_override(str(config_file), str(override_dir))

    # Verify the content of the YAML file
    with open(yaml_file_path, 'r') as f:
        data = yaml.safe_load(f)
        assert data == {"key1": "value1", "key2": "value2"}

def test_convert_file_with_sections(tmp_path):
    # Create a mock config file with sections
    config_file = tmp_path / "test_config.ini"
    config_file.write_text("""
    [Section1]
    key1 = value1
    key2 = value2

    [Section2]
    key3 = value3
    """)

    # Create a mock override directory
    override_dir = tmp_path / "override.d"
    override_dir.mkdir()

    # Initialize the converter
    converter = ConfigConverter()

    # Convert the config file
    yaml_file_path = converter.convert_to_override(str(config_file), str(override_dir))

    # Verify the content of the YAML file
    with open(yaml_file_path, 'r') as f:
        data = yaml.safe_load(f)
        assert data == {
            "Section1": {"key1": "value1", "key2": "value2"},
            "Section2": {"key3": "value3"}
        }

def test_convert_nonexistent_file(tmp_path):
    # Create a mock override directory
    override_dir = tmp_path / "override.d"
    override_dir.mkdir()

    # Initialize the converter
    converter = ConfigConverter()

    # Try to convert a non-existent file
    with pytest.raises(FileNotFoundError):
        converter.convert_to_override(str(tmp_path / "nonexistent.conf"), str(override_dir))