# Bookmark viewer and synchronizer for chromium and firefox
import sys, termios  # noqa
import json, subprocess, shutil  # noqa
import datetime  # TODO only import needed stuff?
import setproctitle  # TODO make this optional
from functools import partial

import tui
import bookmarks

setproctitle.setproctitle("bookmark_manager")


def log(i) -> None:
    with open("log.txt", "a+") as f:
        f.write(datetime.datetime.now().isoformat() + ": " + str(i) + "\n")


def quit(i, e):
    print("\x1b[2J\x1b[H", end="")
    print(e) if e else None
    log("close\n")
    sys.exit(i)


no_op = lambda: None


def create_initial_tabs() -> list:
    tabs = []
    main = bookmarks.folder("Main", no_op)
    for f in [("Import Firefox", no_op),
              ("Import Chromium", no_op),
              ("Import Both", no_op),
              ("Quit", partial(quit, 0, ""))]:
        main.add_folder(*f)
    tabs.append(main)
    
    help_m = bookmarks.folder("Help", no_op)
    for f in [("q to quit", partial(quit, 0, "")),
              ("enter to select highlighted option", no_op),
              ("arrow keys to move highlight", no_op)]:
        help_m.add_folder(*f)
    tabs.append(help_m)
    return tabs

def add_tab(tabs: list, folder) -> None:
    tabs.append(folder)


def main() -> None:
    with open("./config.json", "r") as f:
        config = json.load(f)
        log("loaded config")
    #ff_j = bookmarks.import_ff(config["firefox_filepath"])
    #c_j = bookmarks.import_c(config["chromium_filepath"])
    #print(ff_j)
    bookmark_temp = bookmarks.folder("root", no_op)
    for f in [("folder1", no_op), ("folder2", no_op)]:
        bookmark_temp.add_folder(*f)
    for f in [("yt", "https://www.youtube.com/feed/channels"), ("yc", "https://news.ycombinator.com/")]:
        bookmark_temp.add_bookmark(*f)

    tab_highlight = 0
    tabs = create_initial_tabs()
    add_tab(tabs, bookmark_temp)
    op_highlight = 0  # line to be selected

    print("\x1b[2J\x1b[H", end="")  # clear screen
    print("\x1b[4mBookmark Manager\x1b[0m")

    while True:
        tui.draw_tabs(tabs, tab_highlight)
        tui.draw_options(tabs[tab_highlight], op_highlight)

        char = tui.getch(True)

        if char == "q":
            break

        elif char == "\x1b":  # beginning of escape sequence
            char = tui.handle_esc()
            if char == "up" and op_highlight > 0:
                op_highlight -= 1
            elif char == "dn" and op_highlight < len(tabs[tab_highlight].children) - 1:
                op_highlight += 1
            elif char == "lf" and tab_highlight > 0:
                tab_highlight -= 1
                print("\x1b[3;0H\x1b[0J", end="")
            elif char == "rt" and tab_highlight < len(tabs) - 1:
                tab_highlight += 1
                print("\x1b[3;0H\x1b[0J", end="")
            #elif char == "esc":
                #break

        elif ord(char) == 10:
            char = "ent"  # for printing purposes only?
            try:
                pass
                tabs[tab_highlight].children[op_highlight].command()
            except Exception as e:
                log("operation failed: " + tabs[tab_highlight].name + "/" + tabs[tab_highlight].children[op_highlight].name)
                quit(1, e)

        tui.draw_keypress(char)


if __name__ == "__main__":
    main()
    quit(0, "")
