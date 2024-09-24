import configparser
import yaml
from enum import Enum
from pathlib import Path
from typing import Dict, Any

class ConfigFileFormat(Enum):
    INI = 'ini'
    YAML = 'yaml'

class ConfigParser:
    def parse(self, file_path: str) -> Dict[str, Any]:
        file_format = self.determine_file_format(file_path)
        parser = self.get_parser_for_format(file_format)
        return parser(file_path)

    def serialize(self, config_data: Dict[str, Any], file_path: str):
        file_format = self.determine_file_format(file_path)
        serializer = self.get_serializer_for_format(file_format)
        serializer(config_data, file_path)

    def determine_file_format(self, file_path: str) -> ConfigFileFormat:
        extension = Path(file_path).suffix.lower()
        if extension in ('.ini', '.cfg'):
            return ConfigFileFormat.INI
        elif extension in ('.yaml', '.yml'):
            return ConfigFileFormat.YAML
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    def get_parser_for_format(self, file_format: ConfigFileFormat):
        parsers = {
            ConfigFileFormat.INI: self.parse_ini,
            ConfigFileFormat.YAML: self.parse_yaml
        }
        return parsers.get(file_format, lambda _: ValueError(f"No parser for format: {file_format}"))

    def get_serializer_for_format(self, file_format: ConfigFileFormat):
        serializers = {
            ConfigFileFormat.INI: self.serialize_ini,
            ConfigFileFormat.YAML: self.serialize_yaml
        }
        return serializers.get(file_format, lambda _: ValueError(f"No serializer for format: {file_format}"))

    def parse_ini(self, file_path: str) -> Dict[str, Any]:
        config = configparser.ConfigParser()
        config.read(file_path)
        return {section: dict(config[section]) for section in config.sections()}

    def parse_yaml(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def serialize_ini(self, config_data: Dict[str, Any], file_path: str):
        config = configparser.ConfigParser()
        config.read_dict(config_data)
        with open(file_path, 'w') as file:
            config.write(file)

    def serialize_yaml(self, config_data: Dict[str, Any], file_path: str):
        with open(file_path, 'w') as file:
            yaml.dump(config_data, file, default_flow_style=False)