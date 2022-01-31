# handles actual bookmarks
import sys
import json, subprocess, shutil  # noqa
import datetime  # TODO only import needed stuff?
from functools import partial 


def log(i) -> None:
    with open("log.txt", "a+") as f:
        f.write(datetime.datetime.now().isoformat() + ": " + str(i) + "\n")


def quit(i, e):
    print("\x1b[2J\x1b[H", end="")
    print(e) if e else None
    log("close\n")
    sys.exit(i)


def import_ff(filepath: str) -> dict:  # ignoring the dumb places.sqlite file that doesn't even include the uri's
    try:
        newest_file = "bookmarks-2022-01-27_2565_mBmGREArjfEBRyoUiPg3bw==.jsonlz4"  # TODO get most recetn
        shutil.copy2(filepath + newest_file, "./firefox/bookmarks.jsonlz4")

        with open("./firefox/bookmarks.json", "w+") as f:
            subprocess.run(["lz4jsoncat", "./firefox/bookmarks.jsonlz4"], stdout=f)  # decompress mozilla's moronic compression

        with open("./firefox/bookmarks.json", "r") as f:  # van the above open() be used in rw+ mode?
            j = json.load(f)
        log("imported firefox bookmarks")
        return j
    except Exception as e:
        quit(1, e)


def import_c(filepath: str) -> dict:  # filepath to Bookmarks file
    try:
        shutil.copy2(filepath, "./chromium/bookmarks.json")
        with open("./chromium/bookmarks.json", "r") as f:
            j = json.load(f)
        log("imported chromium bookmarks")
        return j  # TODO delete sync_metadata key?
    except Exception as e:
        quit(1, e)


# TODO dont need the bookmark and folder class. just use a function that make a dict
class bookmark():
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url  # uri for firefox
        self.date_added = None
        self.idd = None  # tuple of firefox/chromium? firefox calls this index?
        self.guid = None  # ditto?
        self.typee = "url"  # "text/x-moz-place"

    def command(self, browser: str = "chromium"):  # This runs when the user hit enter
        try:
            subprocess.Popen([browser, self.url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log("opened: " + self.url + " with " + browser)
        except Exception as e:
            log(e)
            print(e)
            #sys.exit(1)

    def to_json() -> dict:
        return{"name": self.name, "url": self.url}


class folder():
    def __init__(self, name: str, command):
        self.name = name
        self.typee = "folder"  # "text/x-moz-place-container"
        self.children = []
        self.command = command
        log("created folder: " + name)

    def add_bookmark(self, name: str, url: str):
        self.children.append(bookmark(name, url))  # TODO handle bookmarks with same name/url with uuid

    def add_folder(self, name: str, command):
        if self.search(name, "folder"):  # remove this?
            log("Error: folder: " + name + " already exists")
            print("Error: folder: " + name + " already exists")
            pass
        else:
            self.children.append(folder(name, command))

    def search(self, name: str, typee: str) -> list:
        results = []
        # TODO
        return results

    def to_json() -> dict:
        return {"name": self.name, "children": self.children}  # TODO add typee


def export_c(root: folder) -> None:
    pass


def export_ff(root: folder) -> None:
    pass


def sync():
    pass


def save(root: folder) -> None:
    pass
