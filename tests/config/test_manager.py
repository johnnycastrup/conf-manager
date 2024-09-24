import pytest
from pathlib import Path
from conf_manager.config.manager import ConfigManager
from conf_manager.override.processor import Override
from conf_manager.utils.logging_config import setup_logging
import logging

@pytest.fixture(autouse=True)
def setup_test_logging(caplog):
    setup_logging(level=logging.DEBUG)
    caplog.set_level(logging.DEBUG)

@pytest.fixture
def config_manager(tmp_path):
    override_dir = tmp_path / "override.d"
    override_dir.mkdir()
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return ConfigManager(str(override_dir), str(config_dir))

def test_load_all_overrides(config_manager, tmp_path, caplog):
    # Create sample override files
    override1 = tmp_path / "override.d" / "01-override.yaml"
    override1.write_text("""
    overrides:
      config.ini:
        Section1:
          key1: value1
    """)

    override2 = tmp_path / "override.d" / "02-override.yaml"
    override2.write_text("""
    overrides:
      config.ini:
        Section1:
          key2: value2
    """)

    config_manager.load_all_overrides()

    assert len(config_manager.override_set.overrides) == 1
    overrides = list(config_manager.override_set.overrides.values())[0]
    assert len(overrides) == 2

    # Check log messages
    assert any("Loading overrides from directory" in record.message for record in caplog.records)
    assert any("Total overrides loaded: 2" in record.message for record in caplog.records)

def test_apply_all_overrides(config_manager, tmp_path, caplog):
    # Create a sample config file
    config_file = tmp_path / "config" / "config.ini"
    config_file.write_text("""
    [Section1]
    key1 = original1
    key2 = original2
    """)

    # Create sample override files
    override1 = tmp_path / "override.d" / "01-override.yaml"
    override1.write_text("""
    overrides:
      config.ini:
        Section1:
          key1: new_value1
    """)

    override2 = tmp_path / "override.d" / "02-override.yaml"
    override2.write_text("""
    overrides:
      config.ini:
        Section1:
          key2: new_value2
    """)

    config_manager.load_all_overrides()
    config_manager.apply_all_overrides(dry_run=False)

    # Check the result
    with open(config_file, 'r') as f:
        content = f.read()
    assert "key1 = new_value1" in content
    assert "key2 = new_value2" in content

    # Check log messages
    assert any("Applied overrides to" in record.message for record in caplog.records)

def test_run(config_manager, tmp_path, caplog):
    # Create a sample config file
    config_file = tmp_path / "config" / "config.ini"
    config_file.write_text("""
    [Section1]
    key1 = original1
    key2 = original2
    """)

    # Create a sample override file
    override_file = tmp_path / "override.d" / "override.yaml"
    override_file.write_text("""
    overrides:
      config.ini:
        Section1:
          key1: new_value1
        Section2:
          key3: new_value3
    """)

    config_manager.run()

    # Check the result
    with open(config_file, 'r') as f:
        content = f.read()
    assert "key1 = new_value1" in content
    assert "key2 = original2" in content
    assert "key3 = new_value3" in content

    # Check log messages
    assert any("Starting configuration management process" in record.message for record in caplog.records)
    assert any("Configuration management process completed" in record.message for record in caplog.records)

def test_dry_run(config_manager, tmp_path, caplog):
    # Create a sample config file
    config_file = tmp_path / "config" / "config.ini"
    config_file.write_text("""
    [Section1]
    key1 = original1
    """)

    # Create a sample override file
    override_file = tmp_path / "override.d" / "override.yaml"
    override_file.write_text("""
    overrides:
      config.ini:
        Section1:
          key1: new_value1
    """)

    config_manager.run(dry_run=True)

    # Check that the file hasn't been modified
    with open(config_file, 'r') as f:
        content = f.read()
    assert "key1 = original1" in content
    assert "key1 = new_value1" not in content

    # Check log messages
    assert any("Would apply overrides to" in record.message for record in caplog.records)