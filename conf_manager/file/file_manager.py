import os
import shutil
from pathlib import Path
from typing import Optional

class FileManager:
    def read_file(self, file_path: str) -> str:
        self._ensure_file_exists(file_path)
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except IOError as e:
            raise IOError(f"Error reading file {file_path}: {e}")

    def write_file(self, file_path: str, content: str):
        try:
            with open(file_path, 'w') as file:
                file.write(content)
        except PermissionError as e:
            raise PermissionError(f"Permission denied when writing to file {file_path}: {e}")
        except IOError as e:
            raise IOError(f"Error writing to file {file_path}: {e}")

    def backup_file(self, file_path: str) -> str:
        self._ensure_file_exists(file_path)
        original_path = Path(file_path)
        backup_path = self._generate_unique_backup_path(original_path)
        
        try:
            shutil.copy2(file_path, backup_path)
            return str(backup_path)
        except IOError as e:
            raise IOError(f"Error creating backup of {file_path}: {e}")

    def _ensure_file_exists(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

    def _generate_unique_backup_path(self, original_path: Path) -> Path:
        backup_path = original_path.with_suffix(original_path.suffix + '.bak')
        counter = 1
        while backup_path.exists():
            backup_path = original_path.with_suffix(f"{original_path.suffix}.bak{counter}")
            counter += 1
        return backup_path