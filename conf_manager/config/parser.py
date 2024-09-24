import configparser
import yaml
from enum import Enum
from pathlib import Path

class ConfigFileFormat(Enum):
    INI = 'ini'
    YAML = 'yaml'

class ConfigParser:
    def parse(self, file_path: str) -> dict:
        file_format = self.get_file_format(file_path)
        if file_format == ConfigFileFormat.INI:
            return self._parse_ini(file_path)
        elif file_format == ConfigFileFormat.YAML:
            return self._parse_yaml(file_path)
        else:
            raise ValueError("Unsupported file format")

    def serialize(self, config_data: dict, file_path: str):
        file_format = self.get_file_format(file_path)
        if file_format == ConfigFileFormat.INI:
            self._serialize_ini(config_data, file_path)
        elif file_format == ConfigFileFormat.YAML:
            self._serialize_yaml(config_data, file_path)
        else:
            raise ValueError("Unsupported file format")

    def get_file_format(self, file_path: str) -> ConfigFileFormat:
        extension = Path(file_path).suffix.lower()
        if extension in ('.ini', '.cfg'):
            return ConfigFileFormat.INI
        elif extension in ('.yaml', '.yml'):
            return ConfigFileFormat.YAML
        else:
            raise ValueError("Unsupported file format")

    def _parse_ini(self, file_path: str) -> dict:
        config = configparser.ConfigParser()
        config.read(file_path)
        return {section: dict(config[section]) for section in config.sections()}

    def _parse_yaml(self, file_path: str) -> dict:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def _serialize_ini(self, config_data: dict, file_path: str):
        config = configparser.ConfigParser()
        config.read_dict(config_data)
        with open(file_path, 'w') as file:
            config.write(file)

    def _serialize_yaml(self, config_data: dict, file_path: str):
        with open(file_path, 'w') as file:
            yaml.dump(config_data, file, default_flow_style=False)