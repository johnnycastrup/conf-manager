import os
import shutil
from pathlib import Path

class FileManager:
    def read_file(self, file_path: str) -> str:
        with open(file_path, 'r') as file:
            return file.read()

    def write_file(self, file_path: str, content: str):
        with open(file_path, 'w') as file:
            file.write(content)

    def backup_file(self, file_path: str) -> str:
        original_path = Path(file_path)
        backup_path = original_path.with_suffix(original_path.suffix + '.bak')
        
        # If backup already exists, find a new name
        counter = 1
        while backup_path.exists():
            backup_path = original_path.with_suffix(f"{original_path.suffix}.bak{counter}")
            counter += 1

        shutil.copy2(file_path, backup_path)
        return str(backup_path)