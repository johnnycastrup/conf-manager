import sys
import click
import logging
from conf_manager.config.manager import ConfigManager
from conf_manager.config.converter import ConfigConverter
from conf_manager.utils.logging_config import setup_logging

@click.group()
@click.option('--dry-run', '-d', is_flag=True, help='Perform a dry run without making changes')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, dry_run, verbose):
    ctx.ensure_object(dict)
    ctx.obj['DRY_RUN'] = dry_run
    ctx.obj['VERBOSE'] = verbose
    
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(level=log_level)

def main(override_dir, config_dir, dry_run, verbose):
    if not override_dir or not config_dir:
        click.echo("Error: Both override directory and config directory must be provided.")
        return 1  # Failure

    config_manager = ConfigManager(override_dir, config_dir)
    exit_code = config_manager.run(dry_run=dry_run)
    return exit_code

@cli.command()
@click.argument('from_dir', type=click.Path(exists=True))
@click.argument('to_dir', type=click.Path(exists=True))
@click.pass_context
def override(ctx, from_dir, to_dir):
    """Apply overrides FROM a directory TO another directory."""
    exit_code = main(from_dir, to_dir, ctx.obj['DRY_RUN'], ctx.obj['VERBOSE'])
    sys.exit(exit_code)

@cli.command()
@click.argument('from_file', type=click.Path(exists=True))
@click.argument('to_dir', type=click.Path(exists=True))
@click.pass_context
def convert(ctx, from_file, to_dir):
    """Convert a config file FROM one format TO an override YAML file in the specified directory."""
    converter = ConfigConverter()
    try:
        yaml_file = converter.convert_to_override(from_file, to_dir)
        click.echo(f"Config file converted and saved as: {yaml_file}")
        sys.exit(0)  # Success
    except Exception as e:
        click.echo(f"Error converting file: {e}", err=True)
        sys.exit(1)  # Failure

if __name__ == '__main__':
    cli()
