import configparser

import json


config = configparser.ConfigParser()
config.read('config.ini')

keyword_filepath = config["KEYWORDS"]["file_path"]

file = open(keyword_filepath, encoding='utf-8')
cookies = json.load(file)
file.close()
t = [keyword for keyword in cookies.values()]

print(t)