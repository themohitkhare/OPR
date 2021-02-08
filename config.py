from sys import setrecursionlimit

import configparser

config = configparser.ConfigParser()
config.read('settings.config')


def getValueOrDefault(section: str, option: str, default):
    if config.has_option(section, option):
        return config[section][option]
    return default

setrecursionlimit(getValueOrDefault("System", "RecursionLimit", 10000))
