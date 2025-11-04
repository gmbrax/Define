import os
from pathlib import Path


class DirectoryManager:

    @staticmethod
    def get_config_directory()-> Path:
        home = Path.home()
        config_dir = home / ".Define"
        config_dir.mkdir(exist_ok=True)
        os.chmod(config_dir,0o744)

        return config_dir
