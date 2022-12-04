import configparser

def init():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config
