import click
import yaml
import configparser
import os
import logging
from pathlib import Path
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_tool_config():
    config = configparser.ConfigParser()
    config_path = Path.home() / 'Projects' / 'conf-manager' / 'conf_manager' / 'config.ini'
    config.read(config_path)
    return config

def backup_file(file_path):
    for i in range(2, 0, -1):
        old = f"{file_path}.bak{i}"
        new = f"{file_path}.bak{i+1}"
        if os.path.exists(old):
            shutil.move(old, new)
    shutil.copy2(file_path, f"{file_path}.bak1")

def load_override_files(override_dir):
    override_data = {}
    ignore_list = set()
    for file in sorted(os.listdir(override_dir)):  # Sort to process in a consistent order
        if file.endswith('.yaml') or file.endswith('.yml'):
            file_path = os.path.join(override_dir, file)
            try:
                with open(file_path, 'r') as f:
                    file_data = yaml.safe_load(f)
                if file_data and isinstance(file_data, dict):
                    # Process metadata if present
                    if 'metadata' in file_data:
                        priority = file_data['metadata'].get('priority', 0)
                        logging.info(f"Processing {file} with priority {priority}")
                    else:
                        priority = 0

                    # Update overrides
                    if 'overrides' in file_data and isinstance(file_data['overrides'], dict):
                        for config_file, config_data in file_data['overrides'].items():
                            if config_file not in override_data:
                                override_data[config_file] = {}
                            if isinstance(config_data, dict):
                                for section, section_data in config_data.items():
                                    if section not in override_data[config_file]:
                                        override_data[config_file][section] = {}
                                    if isinstance(section_data, dict):
                                        override_data[config_file][section].update(section_data)
                                    elif section_data is None:
                                        # Handle empty sections
                                        override_data[config_file][section] = None
                                    else:
                                        logging.warning(f"Skipping invalid section data in {file}: {section}")
                            else:
                                logging.warning(f"Skipping invalid config data in {file}: {config_file}")

                    # Update ignore list
                    if 'ignore' in file_data and isinstance(file_data['ignore'], list):
                        ignore_list.update(file_data['ignore'])
                else:
                    logging.warning(f"Skipping invalid YAML file: {file}")
            except yaml.YAMLError as e:
                logging.error(f"Error parsing {file_path}: {e}")
                raise  # Re-raise the YAMLError
            except Exception as e:
                logging.error(f"Error reading {file_path}: {e}")
    return override_data, ignore_list

def apply_overrides(override_data, target_file, dry_run=False):
    config = configparser.ConfigParser()
    config.read(target_file)

    changes_made = False

    for section, keys in override_data.items():
        if section not in config:
            config[section] = {}
            changes_made = True
            logging.info(f"{'Would create' if dry_run else 'Created'} new section [{section}] in {target_file}")

        if keys is not None:  # If the section has key-value pairs
            for key, value in keys.items():
                if key not in config[section] or config[section][key] != value:
                    changes_made = True
                    if not dry_run:
                        config[section][key] = value
                    logging.info(f"{'Would change' if dry_run else 'Changed'} [{section}]{key} to {value} in {target_file}")
        elif section not in config:
            # Only log for empty sections if they don't exist in the config
            logging.info(f"{'Would create' if dry_run else 'Created'} empty section [{section}] in {target_file}")

    if changes_made and not dry_run:
        backup_file(target_file)
        with open(target_file, 'w') as configfile:
            config.write(configfile)

    return changes_made

@click.command()
@click.option('--override-dir', '-o', type=click.Path(exists=True), help='Path to the override.d directory')
@click.option('--config-dir', '-c', type=click.Path(exists=True), help='Directory containing config files to modify')
@click.option('--dry-run', '-d', is_flag=True, help='Perform a dry run without making changes')
def main(override_dir, config_dir, dry_run):
    tool_config = load_tool_config()

    if not override_dir:
        override_dir = tool_config.get('Paths', 'override_dir', fallback=None)
    if not override_dir:
        raise click.UsageError("No override directory specified. Use --override-dir or set it in the tool's config.")

    override_dir = os.path.expanduser(override_dir)

    if not config_dir:
        config_dir = tool_config.get('Paths', 'config_dir', fallback=str(Path.home() / '.config'))

    config_dir = os.path.expanduser(config_dir)

    logging.info(f"Using override directory: {override_dir}")
    logging.info(f"Searching for config files in: {config_dir}")
    logging.info(f"Dry run: {'Yes' if dry_run else 'No'}")

    override_data, ignore_list = load_override_files(override_dir)
    if not override_data:
        logging.warning("No valid override files found in the specified directory.")
        return 1

    changes_made = False
    errors_occurred = False
    for config_file, config_data in override_data.items():
        file_path = os.path.join(config_dir, config_file)
        if os.path.exists(file_path):
            try:
                if apply_overrides(config_data, file_path, dry_run):
                    changes_made = True
            except PermissionError:
                logging.error(f"Permission denied: Unable to modify {file_path}")
                errors_occurred = True
            except Exception as e:
                logging.error(f"Error processing {file_path}: {e}")
                errors_occurred = True
        else:
            logging.warning(f"Config file not found: {file_path}")
            errors_occurred = True

    if dry_run:
        logging.info("Dry run completed. No changes were made.")
    elif changes_made and not errors_occurred:
        logging.info("All changes applied successfully.")
    elif changes_made and errors_occurred:
        logging.warning("Some changes were applied, but errors occurred. Please check the log for details.")
    elif not changes_made and errors_occurred:
        logging.error("Errors occurred while processing files. No changes were applied.")
    else:
        logging.info("No changes were necessary.")

    return 1 if errors_occurred else 0

if __name__ == '__main__':
    main()