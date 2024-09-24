# conf-manager

A tool for managing configuration file overrides in a system.

## Description

The `conf-manager` package provides a set of tools for managing override files, allowing you to customize individual settings in configuration files across your system. It's designed to be highly customizable, extensible, and easy to use.

## Features

- Load override files from a specified directory
- Apply overrides to config files in a target directory
- Support for both INI and YAML configuration file formats
- Dry run mode to simulate changes without modifying the system
- Detailed logging for auditing and debugging purposes
- Configurable paths for override directories and config files
- Backup creation before applying changes

## Installation

### Using Nix Flakes (Recommended)

If you have Nix with flakes enabled, you can install and run `conf-manager` directly:

1. To run without installing:
   ```bash
   nix run github:johnnycastrup/conf-manager
   ```

2. To install in your current environment:
   ```bash
   nix profile install github:johnnycastrup/conf-manager
   ```

3. To use in a project, add it to your `flake.nix` inputs:
   ```nix
   {
     inputs.conf-manager.url = "github:johnnycastrup/conf-manager";
     # ...
   }
   ```

### Using Poetry

Alternatively, you can install using Poetry:

1. Clone the repository:
   ```bash
   git clone https://github.com/johnnycastrup/conf-manager.git
   cd conf-manager
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

## Usage

### With Nix Flakes

Run the main script using:

```bash
nix run github:johnnycastrup/conf-manager -- -o <override_directory> -c <config_directory> [options]
```

### With Poetry

Run the main script using:

```bash
poetry run conf-manager -o <override_directory> -c <config_directory> [options]
```

Options:
- `-o, --override-dir`: Path to the directory containing override files (required)
- `-c, --config-dir`: Path to the directory containing config files to modify (required)
- `-d, --dry-run`: Perform a dry run without making changes
- `-v, --verbose`: Enable verbose logging

Example:
```bash
nix run github:johnnycastrup/conf-manager -- -o /etc/conf-manager/override.d -c /etc/myapp -v
```

## Configuration

Override files should be placed in the specified override directory and follow this YAML format:

```yaml
overrides:
  config_file_name:
    section_name:
      key: new_value
```

For example:
```yaml
overrides:
  app_config.ini:
    Database:
      host: new_database_host
      port: 5432
```

## Development

### Using Nix Flakes

To enter a development environment:

```bash
nix develop github:johnnycastrup/conf-manager
```

This will give you a shell with all necessary dependencies.

### Using Poetry

To set up the development environment:

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Run tests:
   ```bash
   poetry run pytest
   ```

## Project Structure

```
conf-manager/
├── conf_manager/
│   ├── config/
│   │   ├── manager.py
│   │   └── parser.py
│   ├── file/
│   │   └── file_manager.py
│   ├── override/
│   │   └── processor.py
│   └── utils/
│       └── logging_config.py
├── tests/
│   ├── config/
│   ├── file/
│   └── override/
├── pyproject.toml
├── flake.nix
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Authors

- Johnny Castrup <johnny@castrup.net>

## Acknowledgments

- Thanks to all contributors who have helped shape this project.
- Special thanks to the Python community for providing excellent libraries that make this project possible.
- Gratitude to the Nix community for enabling reproducible builds and deployments.