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

    def load_overrides(self):
        self.logger.info(f"Loading overrides from directory: {self.override_dir}")
        for filename in sorted(os.listdir(self.override_dir)):
            if filename.endswith(('.yaml', '.yml')):
                file_path = os.path.join(self.override_dir, filename)
                self.logger.debug(f"Processing file: {file_path}")
                try:
                    with open(file_path, 'r') as f:
                        override_data = yaml.safe_load(f)
                    if override_data and 'overrides' in override_data:
                        for target_file, sections in override_data['overrides'].items():
                            full_target_path = os.path.join(self.config_dir, target_file)
                            for section, keys in sections.items():
                                for key, value in keys.items():
                                    override = Override(full_target_path, section, key, value)
                                    self.override_set.add_override(override)
                                    self.logger.debug(f"Added override: {override}")
                    else:
                        self.logger.warning(f"No valid overrides found in {file_path}")
                except yaml.YAMLError as e:
                    self.logger.error(f"Error parsing YAML file {file_path}: {e}")
                except Exception as e:
                    self.logger.error(f"Unexpected error processing {file_path}: {e}")
        
        self.logger.info(f"Total overrides loaded: {sum(len(overrides) for overrides in self.override_set.overrides.values())}")

    def apply_overrides(self, dry_run: bool = False):
        for target_file in set(override.target_file for overrides in self.override_set.overrides.values() for override in overrides):
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

    def run(self, dry_run: bool = False):
        self.logger.info("Starting configuration management process")
        self.load_overrides()
        self.apply_overrides(dry_run)
        self.logger.info("Configuration management process completed")