# conf-manager
A collection of scripts to manage overriding individual ini settings on a system

## Description

The `conf-manager` package provides a set of scripts for managing override files, which allow you to customize individual ini settings on your system. This package is designed to be highly customizable and extensible.

## Features

* Load override files from a specified directory
* Apply overrides to config files in a target directory
* Supports dry run mode to simulate changes without modifying the system
* Log file changes and errors for auditing purposes
* Configurable paths for override directories and config files

## Installation

To install `conf-manager`, clone the project and use the following command:
```
poetry install conf-manager
```

## Usage

You can run the main script using the following command:
```
conf-manager -o <override_directory> -c <config_directory> [-d]
```
Replace `<override_directory>` with the path to your override files, and `<config_directory>` with the directory containing the config files you want to modify. The `-d` flag enables dry run mode.

## Configuration

You can configure the `conf-manager` package by setting environment variables or using a configuration file. For more information, see the [configuration documentation](TODO: link to configuration documentation).

## Development

To contribute to the development of `conf-manager`, clone this repository and install the dependencies using:
```
poetry install
```

Then, run the tests using:
```
pytest
```

Finally, build and package the project using:
```
poetry build
```

## License

`conf-manager` is licensed under the MIT License. For more information, see the [LICENSE](LICENSE) file.

## Authors

* Johnny Castrup <johnny@castrup.net>

**Note:** This README was generated based on the provided `pyproject.toml` and `main.py` files.