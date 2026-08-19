import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        uri = os.environ["COGNODB_URI"]
        user = os.environ["COGNODB_USER"]
        password = os.environ["COGNODB_PASSWORD"]
        _driver = GraphDatabase.driver(uri, auth=(user, password))
    return _driver

def close_driver():
    global _driver
    if _driver:
        _driver.close()
        _driver = None
