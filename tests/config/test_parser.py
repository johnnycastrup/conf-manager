import pytest
from conf_manager.config.parser import ConfigParser, ConfigFileFormat

def test_parse_ini_file(tmp_path):
    # Create a temporary INI file
    ini_content = """
    [Section1]
    key1 = value1
    key2 = value2

    [Section2]
    key3 = value3
    """
    ini_file = tmp_path / "test.ini"
    ini_file.write_text(ini_content)

    parser = ConfigParser()
    config_data = parser.parse(str(ini_file))

    assert config_data == {
        'Section1': {'key1': 'value1', 'key2': 'value2'},
        'Section2': {'key3': 'value3'}
    }
    assert parser.determine_file_format(str(ini_file)) == ConfigFileFormat.INI

def test_parse_yaml_file(tmp_path):
    # Create a temporary YAML file
    yaml_content = """
    Section1:
      key1: value1
      key2: value2
    Section2:
      key3: value3
    """
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml_content)

    parser = ConfigParser()
    config_data = parser.parse(str(yaml_file))

    assert config_data == {
        'Section1': {'key1': 'value1', 'key2': 'value2'},
        'Section2': {'key3': 'value3'}
    }
    assert parser.determine_file_format(str(yaml_file)) == ConfigFileFormat.YAML

def test_parse_unsupported_format(tmp_path):
    # Create a file with an unsupported extension
    unsupported_file = tmp_path / "test.txt"
    unsupported_file.write_text("Some content")

    parser = ConfigParser()
    with pytest.raises(ValueError, match="Unsupported file format"):
        parser.parse(str(unsupported_file))

def test_serialize_ini(tmp_path):
    config_data = {
        'Section1': {'key1': 'value1', 'key2': 'value2'},
        'Section2': {'key3': 'value3'}
    }
    parser = ConfigParser()
    ini_file = tmp_path / "output.ini"
    
    parser.serialize(config_data, str(ini_file))
    
    assert ini_file.read_text() == """[Section1]
key1 = value1
key2 = value2

[Section2]
key3 = value3

"""

def test_serialize_yaml(tmp_path):
    config_data = {
        'Section1': {'key1': 'value1', 'key2': 'value2'},
        'Section2': {'key3': 'value3'}
    }
    parser = ConfigParser()
    yaml_file = tmp_path / "output.yaml"
    
    parser.serialize(config_data, str(yaml_file))
    
    assert yaml_file.read_text() == """Section1:
  key1: value1
  key2: value2
Section2:
  key3: value3
"""