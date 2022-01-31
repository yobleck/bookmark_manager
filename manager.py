# bookmark viewer and synchronizer for chromium and firefox
import sys, termios  # noqa
import json, subprocess, shutil  # noqa
import datetime  # TODO only import needed stuff?
import setproctitle  # TODO make this optional
from functools import partial

setproctitle.setproctitle("bookmark_manager")


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

    def open_bookmark(self, browser: str):
        try:
            subprocess.Popen([browser, self.url])
            log("opened: " + self.url + " with " + browser)
        except Exception as e:
            log(e)
            print(e)
            #sys.exit(1)

    def to_json() -> dict:
        return{"name": self.name, "url": self.url}


class folder():
    def __init__(self, name: str):
        self.name = name
        self.typee = "folder"  # "text/x-moz-place-container"
        self.children = []
        log("created folder: " + name)

    def add_bookmark(self, name: str, url: str):
        self.children.append(bookmark(name, url))  # TODO handle bookmarks with same name/url

    def add_folder(self, name: str):
        if self.search(name, "folder"):
            log("Error: folder: " + name + " already exists")
            print("Error: folder: " + name + " already exists")
            pass
        else:
            self.children.append(folder(name))

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


def getch(blocking: bool = True) -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new = list(old_settings)
    new[3] &= ~(termios.ICANON | termios.ECHO)  # https://manpages.debian.org/bullseye/manpages-dev/termios.3.en.html
    new[6][termios.VMIN] = 1 if blocking else 0
    new[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSADRAIN, new)
    try:
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


esc_chars = {"A": "up", "B": "dn", "C": "rt", "D": "lf"}
def handle_esc() -> str:
    a = getch(False)
    #print("a", a)
    if a == "[":
        k = getch(False)  # assuming 3 bytes for now
        #print("k", k)
        if k in esc_chars.keys():
            return esc_chars[k]
        return "[ error"
    return "esc"


def draw_keypress(ch):
    w, h = shutil.get_terminal_size()
    print("\x1b[" + str(h) + ";0H\x1b[0K\x1b[0G", end="")  # erase bottom line
    print("pressed: " + ch + " \x1b[1A")


def draw_menu(lines, hl):
    w, h = shutil.get_terminal_size()
    print("\x1b[2;0H", end="")
    for i, o in enumerate(lines):
        if i == hl:
            print("\x1b[7m" + o[0] + "\x1b[0m")
        else:
            print(o[0])


def main():
    with open("./config.json", "r") as f:
        config = json.load(f)
        log("loaded config")
    #ff_j = import_ff(config["firefox_filepath"])
    #c_j = import_c(config["chromium_filepath"])
    #print(ff_j)
    bookmarks = folder("root")

    highlight = 0  # line to be selected
    def change_menu(m):
        print("\x1b[2;0H\x1b[0J", end="")
        nonlocal current_menu; current_menu = m
        nonlocal highlight; highlight = 0

    menus = {"start_menu": [("Import Firefox", lambda: 1/0),
                            ("Import Chromium", lambda: None),
                            ("Import Both", lambda: None),
                            ("View Bookmarks", partial(change_menu, "bookmarks")),
                            ("Help", partial(change_menu, "help_menu")),
                            ("Quit", partial(quit, 0, ""))],
             "help_menu": [("q to quit", partial(quit, 0, "")),
                           ("enter to select highlighted option", partial(change_menu, "start_menu")),
                           ("arrow keys to move highlight", partial(change_menu, "start_menu"))],
             "bookmarks": []}  # populate bookmarks list with bookmarks to draw on screen
    current_menu = "start_menu"

    print("\x1b[2J\x1b[H", end="")  # clear screen
    print("\x1b[4mBookmark Manager\x1b[0m")

    while True:
        draw_menu(menus[current_menu], highlight)


        char = getch(True)

        if char == "q":
            break

        elif char == "\x1b":  # beginning of escape sequence
            char = handle_esc()
            if char == "esc":
                break
            elif char == "up" and highlight > 0:
                highlight -= 1
            elif char == "dn" and highlight < len(menus[current_menu]) - 1:
                highlight += 1
            elif char == "lf":
                current_menu = "start_menu"
            # enter for select. esc or bkspc for back or up
            # f to add folder. b for bookmark. input() to prompt for info
            # collapsible folders

        elif ord(char) == 10:
            char = "ent"  # for printing purposes only?
            try:
                menus[current_menu][highlight][1]()
            except Exception as e:
                log("function failed: " + str(menus[current_menu][highlight]))
                quit(1, e)

        draw_keypress(char)


if __name__ == "__main__":
    main()
    quit(0, "")
