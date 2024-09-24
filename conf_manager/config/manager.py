import os
import yaml
from typing import List
from conf_manager.config.parser import ConfigParser
from conf_manager.override.processor import OverrideProcessor, OverrideSet, Override
from conf_manager.file.file_manager import FileManager
from conf_manager.utils.logging_config import get_logger

class ConfigManager:
    def __init__(self, override_dir: str, config_dir: str):
        self.override_dir = override_dir
        self.config_dir = config_dir
        self.config_parser = ConfigParser()
        self.file_manager = FileManager()
        self.override_processor = OverrideProcessor(self.config_parser)
        self.override_set = OverrideSet()
        self.logger = get_logger(__name__)

    def run(self, dry_run: bool = False):
        self.logger.info("Starting configuration management process")
        self.load_all_overrides()
        self.apply_all_overrides(dry_run)
        self.logger.info("Configuration management process completed")

    def load_all_overrides(self):
        self.logger.info(f"Loading overrides from directory: {self.override_dir}")
        override_files = self.get_sorted_override_files()
        for file_path in override_files:
            self.process_override_file(file_path)
        self.log_total_overrides()

    def get_sorted_override_files(self):
        return sorted(
            [os.path.join(self.override_dir, f) for f in os.listdir(self.override_dir)
             if f.endswith(('.yaml', '.yml'))]
        )

    def process_override_file(self, file_path):
        self.logger.debug(f"Processing file: {file_path}")
        try:
            override_data = self.load_yaml_file(file_path)
            if self.is_valid_override_data(override_data):
                self.add_overrides_from_data(override_data)
            else:
                self.logger.warning(f"No valid overrides found in {file_path}")
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML file {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error processing {file_path}: {e}")

    def load_yaml_file(self, file_path):
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)

    def is_valid_override_data(self, override_data):
        return override_data and 'overrides' in override_data

    def add_overrides_from_data(self, override_data):
        for target_file, sections in override_data['overrides'].items():
            full_target_path = os.path.join(self.config_dir, target_file)
            for section, keys in sections.items():
                for key, value in keys.items():
                    override = Override(full_target_path, section, key, value)
                    self.override_set.add_override(override)
                    self.logger.debug(f"Added override: {override}")

    def log_total_overrides(self):
        total_overrides = sum(len(overrides) for overrides in self.override_set.overrides.values())
        self.logger.info(f"Total overrides loaded: {total_overrides}")

    def apply_all_overrides(self, dry_run: bool):
        for target_file in self.get_unique_target_files():
            self.apply_overrides_to_file(target_file, dry_run)

    def get_unique_target_files(self):
        return set(override.target_file for overrides in self.override_set.overrides.values() for override in overrides)

    def apply_overrides_to_file(self, target_file: str, dry_run: bool):
        if os.path.exists(target_file):
            if not dry_run:
                try:
                    self.override_processor.process(self.override_set, target_file)
                    self.logger.info(f"Applied overrides to {target_file}")
                except Exception as e:
                    self.logger.error(f"Error applying overrides to {target_file}: {e}")
            else:
                self.logger.info(f"Would apply overrides to {target_file}")
        else:
            self.logger.warning(f"Target file does not exist: {target_file}")