import configparser
config = configparser.ConfigParser()
config.read('settings.config')


def getValueOrDefault(section: str, option: str, default):
    if config.has_option(section, option):
        return config[section][option]
    return default

from sys import setrecursionlimit
setrecursionlimit(getValueOrDefault("System", "RecursionLimit", 10000))
