import click
from conf_manager.config.manager import ConfigManager
from conf_manager.utils.logging_config import setup_logging
import logging

@click.command()
@click.option('--override-dir', '-o', type=click.Path(exists=True), help='Path to the override.d directory')
@click.option('--config-dir', '-c', type=click.Path(exists=True), help='Directory containing config files to modify')
@click.option('--dry-run', '-d', is_flag=True, help='Perform a dry run without making changes')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(override_dir, config_dir, dry_run, verbose):
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(level=log_level)

    config_manager = ConfigManager(override_dir, config_dir)
    config_manager.run(dry_run=dry_run)

if __name__ == '__main__':
    main()