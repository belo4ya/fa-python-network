import os
import configparser
import logging

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".config.ini"))

HOST = config["DEFAULT"]["HOST"]
PORT = int(config["DEFAULT"]["PORT"])
ENCODING = config["DEFAULT"]["ENCODING"]

logging.basicConfig(format="%(asctime)s.%(msecs)03d\t%(message)s", datefmt="%H:%M:%S", level=logging.INFO)
logger = logging.getLogger("tcpserver")
