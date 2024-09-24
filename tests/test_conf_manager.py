import io
import logging
import os
import pytest
import configparser
import shutil
import yaml
from unittest.mock import patch, mock_open
from click.testing import CliRunner

from tempfile import TemporaryDirectory
from conf_manager.main import load_tool_config, load_override_files, apply_overrides, backup_file, main

@pytest.fixture
def temp_dir():
    with TemporaryDirectory() as tmpdir:
        yield tmpdir

def create_yaml_file(directory, filename, content):
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as f:
        yaml.dump(content, f)
    return file_path

def create_ini_file(directory, filename, content):
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path

def test_load_override_files(temp_dir):
    yaml_content = {
        'metadata': {'priority': 50},
        'overrides': {
            'test.ini': {
                'section1': {'key1': 'value1'},
                'section2': None
            }
        }
    }
    create_yaml_file(temp_dir, 'test_override.yaml', yaml_content)

    override_data, ignore_list = load_override_files(temp_dir)

    assert 'test.ini' in override_data
    assert override_data['test.ini']['section1']['key1'] == 'value1'
    assert override_data['test.ini']['section2'] is None

def test_apply_overrides(temp_dir):
    ini_content = """
[section1]
key1 = old_value
[section2]
key2 = keep_this
"""
    ini_file = create_ini_file(temp_dir, 'test.ini', ini_content)

    override_data = {
        'section1': {'key1': 'new_value'},
        'section3': {'key3': 'new_key'}
    }

    changes_made = apply_overrides(override_data, ini_file, dry_run=False)

    assert changes_made == True

    # Read the file and check its contents
    with open(ini_file, 'r') as f:
        new_content = f.read()

    assert 'key1 = new_value' in new_content
    assert 'key2 = keep_this' in new_content
    assert 'key3 = new_key' in new_content

@pytest.mark.parametrize("yaml_content,ini_content,expected_changes", [
    # Test case 1: Change existing value
    (
        {'overrides': {'test.ini': {'section1': {'key1': 'new_value'}}}},
        "[section1]\nkey1 = old_value",
        True
    ),
    # Test case 2: Add new section
    (
        {'overrides': {'test.ini': {'new_section': {'new_key': 'new_value'}}}},
        "[existing_section]\nkey = value",
        True
    ),
    # Test case 3: No changes needed
    (
        {'overrides': {'test.ini': {'section1': {'key1': 'existing_value'}}}},
        "[section1]\nkey1 = existing_value",
        False
    ),
    # Add more test cases as needed
])
def test_apply_overrides_parametrized(temp_dir, yaml_content, ini_content, expected_changes):
    yaml_file = create_yaml_file(temp_dir, 'test_override.yaml', yaml_content)
    ini_file = create_ini_file(temp_dir, 'test.ini', ini_content)

    override_data, _ = load_override_files(temp_dir)
    changes_made = apply_overrides(override_data['test.ini'], ini_file, dry_run=False)

    assert changes_made == expected_changes

# Test backup functionality
def test_backup_file(temp_dir):
    file_path = os.path.join(temp_dir, 'test.ini')
    with open(file_path, 'w') as f:
        f.write("original content")

    backup_file(file_path)

    # Check if the backup file was created
    assert os.path.exists(f"{file_path}.bak1")

    # Check if the content of the backup file is correct
    with open(f"{file_path}.bak1", 'r') as f:
        assert f.read() == "original content"

    # Check if the original file is unchanged
    with open(file_path, 'r') as f:
        assert f.read() == "original content"

def test_multiple_backups(temp_dir):
    file_path = os.path.join(temp_dir, 'test.ini')
    with open(file_path, 'w') as f:
        f.write("original content")

    # Create multiple backups
    for i in range(3):
        backup_file(file_path)

    # Check if all backup files exist
    for i in range(1, 4):
        assert os.path.exists(f"{file_path}.bak{i}")

    # Check if the content of the latest backup is correct
    with open(f"{file_path}.bak1", 'r') as f:
        assert f.read() == "original content"

def test_backup_nonexistent_file(temp_dir):
    file_path = os.path.join(temp_dir, 'nonexistent.ini')

    # This should raise a FileNotFoundError
    with pytest.raises(FileNotFoundError):
        backup_file(file_path)

# Test for load_tool_config
def test_load_tool_config():
    mock_config = """
    [Paths]
    override_dir = /path/to/override
    config_dir = /path/to/config
    """
    with patch("builtins.open", mock_open(read_data=mock_config)):
        config = load_tool_config()
        assert config['Paths']['override_dir'] == '/path/to/override'
        assert config['Paths']['config_dir'] == '/path/to/config'

# Additional tests for load_override_files
def test_load_override_files_multiple_yaml(temp_dir):
    yaml_content1 = {
        'metadata': {'priority': 50},
        'overrides': {'test1.ini': {'section1': {'key1': 'value1'}}},
        'ignore': ['ignore1.ini']
    }
    yaml_content2 = {
        'metadata': {'priority': 60},
        'overrides': {'test2.ini': {'section2': {'key2': 'value2'}}},
        'ignore': ['ignore2.ini']
    }
    create_yaml_file(temp_dir, 'test1.yaml', yaml_content1)
    create_yaml_file(temp_dir, 'test2.yaml', yaml_content2)

    override_data, ignore_list = load_override_files(temp_dir)

    assert 'test1.ini' in override_data
    assert 'test2.ini' in override_data
    assert override_data['test1.ini']['section1']['key1'] == 'value1'
    assert override_data['test2.ini']['section2']['key2'] == 'value2'
    assert 'ignore1.ini' in ignore_list
    assert 'ignore2.ini' in ignore_list

def test_load_override_files_invalid_yaml(temp_dir):
    with open(os.path.join(temp_dir, 'invalid.yaml'), 'w') as f:
        f.write("invalid: yaml: content:")

    with pytest.raises(yaml.YAMLError):
        load_override_files(temp_dir)

# Tests for main CLI function
def test_main_cli():
    runner = CliRunner()
    log_output = io.StringIO()
    handler = logging.StreamHandler(log_output)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    with patch('conf_manager.main.load_override_files') as mock_load, \
         patch('conf_manager.main.apply_overrides') as mock_apply, \
         patch('os.path.exists') as mock_exists:
        mock_load.return_value = ({'test.ini': {'section1': {'key1': 'value1'}}}, set())
        mock_apply.return_value = True
        mock_exists.return_value = True  # Simulate that the config file exists
        result = runner.invoke(main, ['--override-dir', '/tmp', '--config-dir', '/tmp', '--dry-run'])

        assert result.exit_code == 0
        log_contents = log_output.getvalue()
        assert "Dry run completed" in log_contents

    logging.getLogger().removeHandler(handler)

def test_main_cli_missing_override_dir():
    runner = CliRunner()
    with patch('conf_manager.main.load_tool_config') as mock_config:
        mock_config.return_value = configparser.ConfigParser()  # Empty config
        result = runner.invoke(main, ['--config-dir', '/tmp'])
        assert result.exit_code != 0
        assert "No override directory specified" in result.output

# Additional tests for apply_overrides
def test_apply_overrides_dry_run(temp_dir):
    ini_content = "[section1]\nkey1 = old_value"
    ini_file = create_ini_file(temp_dir, 'test.ini', ini_content)
    override_data = {'section1': {'key1': 'new_value'}}

    changes_made = apply_overrides(override_data, ini_file, dry_run=True)

    assert changes_made == True
    with open(ini_file, 'r') as f:
        assert f.read() == ini_content  # File should be unchanged

def test_apply_overrides_empty_section(temp_dir):
    ini_content = "[section1]\nkey1 = value1"
    ini_file = create_ini_file(temp_dir, 'test.ini', ini_content)
    override_data = {'section2': None}

    changes_made = apply_overrides(override_data, ini_file, dry_run=False)

    assert changes_made == True
    with open(ini_file, 'r') as f:
        new_content = f.read()
        assert '[section2]' in new_content

# Test for error handling
def test_apply_overrides_permission_error(temp_dir):
    ini_file = create_ini_file(temp_dir, 'test.ini', "[section1]\nkey1 = value1")
    os.chmod(ini_file, 0o444)  # Make file read-only

    with pytest.raises(PermissionError):
        apply_overrides({'section1': {'key1': 'new_value'}}, ini_file, dry_run=False)

# Test for logging
def test_apply_overrides_logging(temp_dir, caplog):
    ini_file = create_ini_file(temp_dir, 'test.ini', "[section1]\nkey1 = old_value")
    override_data = {'section1': {'key1': 'new_value'}}

    apply_overrides(override_data, ini_file, dry_run=False)

    assert "Changed [section1]key1 to new_value" in caplog.text

# Integration test
def test_main_integration(temp_dir):
    # Create a mock configuration
    config_content = "[Paths]\noverride_dir = {}\nconfig_dir = {}".format(temp_dir, temp_dir)
    with open(os.path.join(temp_dir, 'config.ini'), 'w') as f:
        f.write(config_content)

    # Create a mock override file
    yaml_content = {
        'overrides': {
            'test.ini': {
                'section1': {'key1': 'new_value'}
            }
        }
    }
    create_yaml_file(temp_dir, 'override.yaml', yaml_content)

    # Create a mock config file to be modified
    create_ini_file(temp_dir, 'test.ini', "[section1]\nkey1 = old_value")

    # Set up logging capture
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    # Run the main function
    runner = CliRunner()
    with patch('conf_manager.main.load_tool_config') as mock_config:
        config = configparser.ConfigParser()
        config.read_string(config_content)
        mock_config.return_value = config
        result = runner.invoke(main)

    assert result.exit_code == 0

    # Check the captured log output
    log_output = log_capture.getvalue()
    assert "All changes applied successfully" in log_output

    # Remove the handler after the test
    logging.getLogger().removeHandler(handler)

    # Verify the changes
    with open(os.path.join(temp_dir, 'test.ini'), 'r') as f:
        assert 'key1 = new_value' in f.read()
