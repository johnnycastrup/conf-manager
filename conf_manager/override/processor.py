import os
from dataclasses import dataclass
from typing import List, Dict
from conf_manager.config.parser import ConfigParser
from conf_manager.utils.logging_config import get_logger

@dataclass
class Override:
    target_file: str
    section: str
    key: str
    value: str
    priority: int = 0

class OverrideSet:
    def __init__(self):
        self.overrides: Dict[str, List[Override]] = {}
        self.logger = get_logger(__name__)

    def add_override(self, override: Override):
        normalized_path = os.path.normpath(override.target_file)
        if normalized_path not in self.overrides:
            self.overrides[normalized_path] = []
        self.overrides[normalized_path].append(override)
        self.logger.debug(f"Added override: {override}")

    def get_overrides_for_file(self, target_file: str) -> List[Override]:
        normalized_path = os.path.normpath(target_file)
        overrides = self.overrides.get(normalized_path, [])
        return sorted(overrides, key=lambda x: x.priority)

class OverrideProcessor:
    def __init__(self, config_parser: ConfigParser):
        self.config_parser = config_parser
        self.logger = get_logger(__name__)

    def process(self, override_set: OverrideSet, target_file: str):
        self.ensure_file_exists(target_file)
        self.logger.info(f"Processing overrides for {target_file}")
        
        config_data = self.load_config_data(target_file)
        overrides = override_set.get_overrides_for_file(target_file)
        
        self.apply_overrides(config_data, overrides)
        self.save_config_data(config_data, target_file)
        
        self.logger.info(f"Finished processing overrides for {target_file}")

    def ensure_file_exists(self, target_file: str):
        if not os.path.exists(target_file):
            raise FileNotFoundError(f"The file {target_file} does not exist.")

    def load_config_data(self, target_file: str) -> dict:
        return self.config_parser.parse(target_file)

    def apply_overrides(self, config_data: dict, overrides: List[Override]):
        for override in overrides:
            self.apply_single_override(config_data, override)

    def apply_single_override(self, config_data: dict, override: Override):
        if override.section not in config_data:
            config_data[override.section] = {}
        config_data[override.section][override.key] = override.value
        self.logger.debug(f"Applied override: {override}")

    def save_config_data(self, config_data: dict, target_file: str):
        self.config_parser.serialize(config_data, target_file)