from define.utils.singleton import SingletonMeta


class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self.config_dir = None
        self.__data = dict()

