import yaml
import os
import re

class ConfigConverter:
    def convert_to_override(self, config_file, override_dir):
        # Read the config file
        with open(config_file, 'r') as f:
            content = f.read()

        # Parse the config file
        config_dict = {}
        current_section = None
        for line in content.splitlines():
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                config_dict[current_section] = {}
            elif '=' in line:
                key, value = map(str.strip, line.split('=', 1))
                if current_section:
                    config_dict[current_section][key] = value
                else:
                    config_dict[key] = value

        # Create the YAML content
        yaml_content = yaml.dump(config_dict, default_flow_style=False)

        # Create the new YAML file in the override directory
        base_name = os.path.basename(config_file)
        yaml_file_name = os.path.splitext(base_name)[0] + '.yml'
        yaml_file_path = os.path.join(override_dir, yaml_file_name)

        # Write the YAML content to the new file
        with open(yaml_file_path, 'w') as f:
            f.write(yaml_content)

        return yaml_file_path
