# Config
import configparser
config = configparser.ConfigParser()
config.read('settings.config')


def getValueOrDefault(section: str, option: str, default):
    if config.has_option(section, option):
        return config[section][option]
    return default

# Helper Functions


def isBlank(string: str) -> bool:
    return string is None or string == None or string == "" or len(string) == 0


def isNotBlank(string: str) -> bool:
    return not isBlank(string)


def hasNumbers(string: str) -> bool:
    if isNotBlank(string):
        return any(char.isdigit() for char in string)
    return False


def startsWith(string: str, ch: str) -> bool:
    if isNotBlank(string) and isNotBlank(ch):
        return string[0:len(ch)] == ch
    return False


def endsWith(string: str, ch: str) -> bool:
    if isNotBlank(string) and isNotBlank(ch):
        return string[-1*len(ch):] == ch
    return False


def isEmpty(array: list) -> bool:
    return len(array) == 0 or array is None


def isNotEmpty(array: list) -> bool:
    return not isEmpty(array)
