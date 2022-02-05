# handles actual bookmarks
import json
import shutil
import subprocess

import utils


def import_ff(filepath: str) -> dict:  # ignoring the dumb places.sqlite file that doesn't even include the uri's
    try:
        newest_file = "bookmarks-2022-02-04_2567_-hj38Gj4gqd1-t5nsLoINA==.jsonlz4"  # TODO get most recetn
        shutil.copy2(filepath + newest_file, "./firefox/bookmarks.jsonlz4")

        with open("./firefox/bookmarks.json", "w+") as f:
            subprocess.run(["lz4jsoncat", "./firefox/bookmarks.jsonlz4"], stdout=f)  # decompress mozilla's moronic compression

        with open("./firefox/bookmarks.json", "r") as f:  # can the above open() be used in rw+ mode?
            j = json.load(f)
        utils.log("imported firefox bookmarks")
        j["title"] = "firefox"
        return j
    except Exception as e:
        utils.quit(1, e)


def create_ff_tree(js, par, command) -> dict:
    #print("start")
    temp_folder = folder(name=js["title"], command=command, parent=par)
    if "children" in js:
        for c in js["children"]:
            if c["type"] == "text/x-moz-place":  # bookmark
                #print("uri", c["title"])
                temp_folder.add_bookmark(name=c["title"], url=c["uri"])
            elif c["type"] == "text/x-moz-place-container":  # folder
                #print("folder", c["title"])
                create_ff_tree(c, temp_folder, command)
    return temp_folder


def import_c(filepath: str) -> dict:  # filepath to Bookmarks file
    try:
        shutil.copy2(filepath, "./chromium/bookmarks.json")
        with open("./chromium/bookmarks.json", "r") as f:
            j = json.load(f)
        utils.log("imported chromium bookmarks")

        # change chromium's root dict to have the same format as the rest
        j = j["roots"]
        j["type"] = "folder"; j["name"] = "chromium"
        j["children"] = [j["bookmark_bar"], j["other"], j["synced"]]
        del j["bookmark_bar"]; del j["other"]; del j["synced"]  # don't hard code this?

        return j  # TODO delete sync_metadata key?
    except Exception as e:
        utils.quit(1, e)


def create_c_tree(js, par, command):
    #print("start")
    assert isinstance(js, dict) and "type" in js and js["type"] == "folder" and "children" in js
    #[print(x) for x in js]
    temp_folder = folder(name=js["name"], command=command, parent=par)
    for c in js["children"]:
        if c["type"] == "url":
            #print("url", c["name"])
            temp_folder.add_bookmark(name=c["name"], url=c["url"])
        elif c["type"] == "folder":
            #print("folder", c["name"])
            create_c_tree(c, temp_folder, command)
    return temp_folder


def convert():
    pass


# TODO dont need the bookmark and folder class. just use a function that make a dict
class bookmark():
    def __init__(self, name: str, url: str, parent):
        self.name = name
        self.url = url  # uri for firefox
        self.date_added = None
        self.idd = None  # tuple of firefox/chromium? firefox calls this index?
        self.guid = None  # ditto?
        self.typee = "url"  # "text/x-moz-place"
        self.parent = parent

    def command(self, browser: str = "chromium"):  # This runs when the user hit enter
        try:
            subprocess.Popen([browser, self.url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            utils.log("opened: " + self.url + " with " + browser)
        except Exception as e:
            utils.log(e)
            print(e)
            #sys.exit(1)

    def to_json(self) -> dict:
        return{"name": self.name, "url": self.url}


class folder():
    def __init__(self, name: str, command, parent=None):
        self.name = name
        self.typee = "folder"  # "text/x-moz-place-container"
        self.children = []
        self.command = command
        if parent is None:
            self.parent = self
        else:  # TODO type check for folder
            self.parent = parent
            self.parent.children.append(self)
        utils.log("created folder: " + name)

    def add_bookmark(self, name: str, url: str):
        self.children.append(bookmark(name, url, parent=self))  # TODO handle bookmarks with same name/url with uuid
        utils.log("added bookmark: " + name)

    def add_folder(self, name: str, command):
        if self.search(name, "folder"):  # remove this and use uuid?
            utils.log("Error: folder: " + name + " already exists")
            print("Error: folder: " + name + " already exists")
            pass
        else:
            folder(name, command, parent=self)
            #self.children.append(folder(name, command, parent = self))
            #utils.log("added folder: " + name)

    def search(self, name: str, typee: str) -> list:
        results = []
        # TODO
        return results

    def to_json(self) -> dict:
        return {"name": self.name, "children": self.children}  # TODO add typee


def export_c(root: folder) -> None:
    pass


def export_ff(root: folder) -> None:
    pass


def sync():
    pass


def save(root: folder) -> None:
    pass
