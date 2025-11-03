import os.path

import tomli
import tomli_w

from define.utils.directory_manager import DirectoryManager
from define.utils.singleton import SingletonMeta


class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self.config_dir = DirectoryManager.get_config_directory()
        self.__data = dict()

    def read_config(self):
        if os.path.exists(f"{self.config_dir}/config.toml"):
            try:
                with open(f"{self.config_dir}/config.toml", "rb") as f:
                    data = tomli.load(f)
            except tomli.TOMLDecodeError as e:
                raise ValueError(f"Invalid TOML file; {e}")
            except Exception as e:
                raise ValueError(f"Error reading config file; {e}")

            self.__data = data
            return self.__data

        else:
            return None

    def set_data_dict(self, data):
        self.__data.update(data)

    def write_config(self):
        default = {
            "THESAURUS KEY": "",
            "DICTIONARY KEY":"",


        }

        for key, default_value in default.items():
            current_value = self.__data.get(key)
            if current_value is None or current_value == "":
                self.__data[key] = default_value
            else:
                self.__data[key] = current_value
        with open(f"{self.config_dir}/config.toml", "wb") as f:
            tomli_w.dump(self.__data, f)

    def get_data(self,key):
        if key in self.__data.keys():
            return {key:self.__data[key]}
        else:
            return None