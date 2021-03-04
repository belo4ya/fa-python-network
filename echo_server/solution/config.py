import os
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".config.ini"))

HOST = config["DEFAULT"]["HOST"]
PORT = int(config["DEFAULT"]["PORT"])
ENCODING = config["DEFAULT"]["ENCODING"]
