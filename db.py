import psycopg2
import json

def load_config(env="local"):
    with open("config.json") as f:
        config = json.load(f)
    return config[env]

def get_connection(env="local"):
    cfg = load_config(env)
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        dbname=cfg["database"]
    )