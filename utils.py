#TODO add stuff 
import sys
import json
import datetime


def load_config() -> dict:
    with open("./config.json", "r") as f:
        try:
            config = json.load(f)
        except Exception as e:
            print("config failed to load:")
            raise Exception(e)
    return config

config = load_config()

def log(i) -> None:
    if config["logging"]:
        with open("log.txt", "a+") as f:
            f.write(datetime.datetime.now().isoformat() + ": " + str(i) + "\n")


def quit(i, e) -> None:
    print("\x1b[2J\x1b[H", end="")
    print(e) if e else None
    log("close log\n")
    sys.exit(i)


no_op = lambda: None
