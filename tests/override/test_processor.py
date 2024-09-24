import pytest
import os
from conf_manager.override.processor import OverrideProcessor, Override, OverrideSet
from conf_manager.config.parser import ConfigParser

@pytest.fixture
def config_parser():
    return ConfigParser()

@pytest.fixture
def override_processor(config_parser):
    return OverrideProcessor(config_parser)

def test_apply_simple_override(tmp_path, override_processor, config_parser):
    # Create a simple INI file
    original_content = """
    [Section1]
    key1 = value1
    key2 = value2
    """
    config_file = tmp_path / "config.ini"
    config_file.write_text(original_content)

    # Create an override with the full path
    override = Override(target_file=str(config_file), section="Section1", key="key1", value="new_value1")
    override_set = OverrideSet()
    override_set.add_override(override)

    # Apply the override
    override_processor.process(override_set, str(config_file))

    # Check the result
    result = config_parser.parse(str(config_file))
    print(f"Original content: {original_content}")
    print(f"Result after override: {result}")
    assert result == {
        'Section1': {'key1': 'new_value1', 'key2': 'value2'}
    }

def test_apply_multiple_overrides(tmp_path, override_processor, config_parser):
    # Create a simple INI file
    original_content = """
    [Section1]
    key1 = value1
    key2 = value2

    [Section2]
    key3 = value3
    """
    config_file = tmp_path / "config.ini"
    config_file.write_text(original_content)

    # Create multiple overrides
    overrides = [
        Override(target_file=str(config_file), section="Section1", key="key1", value="new_value1"),
        Override(target_file=str(config_file), section="Section2", key="key3", value="new_value3"),
        Override(target_file=str(config_file), section="Section1", key="key2", value="new_value2")
    ]
    override_set = OverrideSet()
    for override in overrides:
        override_set.add_override(override)

    # Apply the overrides
    override_processor.process(override_set, str(config_file))

    # Check the result
    result = config_parser.parse(str(config_file))
    assert result == {
        'Section1': {'key1': 'new_value1', 'key2': 'new_value2'},
        'Section2': {'key3': 'new_value3'}
    }

def test_apply_override_new_section(tmp_path, override_processor, config_parser):
    # Create a simple INI file
    original_content = """
    [Section1]
    key1 = value1
    """
    config_file = tmp_path / "config.ini"
    config_file.write_text(original_content)

    # Create an override for a new section
    override = Override(target_file=str(config_file), section="NewSection", key="new_key", value="new_value")
    override_set = OverrideSet()
    override_set.add_override(override)

    # Apply the override
    override_processor.process(override_set, str(config_file))

    # Check the result
    result = config_parser.parse(str(config_file))
    assert result == {
        'Section1': {'key1': 'value1'},
        'NewSection': {'new_key': 'new_value'}
    }

def test_apply_override_priority(tmp_path, override_processor, config_parser):
    # Create a simple INI file
    original_content = """
    [Section1]
    key1 = value1
    """
    config_file = tmp_path / "config.ini"
    config_file.write_text(original_content)

    # Create overrides with different priorities
    override1 = Override(target_file=str(config_file), section="Section1", key="key1", value="low_priority", priority=1)
    override2 = Override(target_file=str(config_file), section="Section1", key="key1", value="high_priority", priority=2)
    override_set = OverrideSet()
    override_set.add_override(override1)
    override_set.add_override(override2)

    # Apply the overrides
    override_processor.process(override_set, str(config_file))

    # Check the result (high priority override should win)
    result = config_parser.parse(str(config_file))
    assert result == {
        'Section1': {'key1': 'high_priority'}
    }

def test_apply_override_to_nonexistent_file(tmp_path, override_processor):
    nonexistent_file = tmp_path / "nonexistent.ini"
    override = Override(target_file=str(nonexistent_file), section="Section1", key="key1", value="value1")
    override_set = OverrideSet()
    override_set.add_override(override)

    with pytest.raises(FileNotFoundError):
        override_processor.process(override_set, str(nonexistent_file))