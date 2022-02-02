# Bookmark viewer and synchronizer for chromium and firefox
import sys, termios  # noqa
import json, subprocess, shutil  # noqa
import datetime  # TODO only import needed stuff?
import setproctitle  # TODO make this optional
from functools import partial

import tui
import bookmarks

setproctitle.setproctitle("bookmark_manager")


with open("./config.json", "r") as f:
    try:
        config = json.load(f)
    except Exception as e:
        print("config failed to load:")
        print(e)


def log(i) -> None:
    if config["logging"]:
        with open("log.txt", "a+") as f:
            f.write(datetime.datetime.now().isoformat() + ": " + str(i) + "\n")


def quit(i, e):
    print("\x1b[2J\x1b[H", end="")
    print(e) if e else None
    log("close log\n")
    sys.exit(i)


no_op = lambda: None


def add_tab(tabs: list, folder) -> None:
    tabs.append([folder, 0])


def main() -> None:
    # Generate fake folders for menus
    tabs = []
    tab_highlight = 0

    def enter_folder() -> None:
        tab = tabs[tab_highlight]
        option = tab[0].children[tab[1]]
        log(option.name)
        tabs[tab_highlight] = [option, 0]

    def parent_folder() -> None:
        tab = tabs[tab_highlight]
        parent = tab[0].parent
        log(parent.name)
        tabs[tab_highlight] = [parent, 0]

    def create_initial_tabs() -> list:
        tabs = []
        main = bookmarks.folder("Main", no_op)
        for f in [("Import Firefox", no_op),
                ("Import Chromium", no_op),
                ("Import Both", no_op),
                ("Help", partial(enter_folder)),
                ("Quit", partial(quit, 0, ""))]:
            main.add_folder(*f)
        tabs.append([main, 0])  # NOTE second item keeps track of highlight pos

        help_m = main.children[3]  # TODO DONT HARD CODE THIS. bookmarks.folder("Help", no_op)
        for f in [("tab/shift+tab to change tabs", no_op),
                  ("up/down arrow keys to change selection", no_op),
                  ("right arrow key to enter folder", no_op),
                  ("left arrow key to return to parent folder", no_op),
                  ("enter to select highlighted option", no_op),
                  ("folders are green and urls are blue", no_op),
                  ("q to quit", partial(quit, 0, "")),]:
            help_m.add_folder(*f)
        #tabs.append([help_m, 0])
        return tabs
    tabs = create_initial_tabs()

    #ff_j = bookmarks.import_ff(config["firefox_filepath"])
    #c_j = bookmarks.import_c(config["chromium_filepath"])
    #print(ff_j)
    bookmark_temp = bookmarks.folder("root", no_op)
    for f in [("folder1", partial(enter_folder)), ("folder2", partial(enter_folder))]:
        bookmark_temp.add_folder(*f)
        bookmark_temp.children[-1].add_bookmark("yc", "https://news.ycombinator.com/")
    for f in [("yt", "https://www.youtube.com/feed/channels"), ("yc", "https://news.ycombinator.com/")]:
        bookmark_temp.add_bookmark(*f)

    add_tab(tabs, bookmark_temp)

    print("\x1b[2J\x1b[H", end="")  # clear screen
    print("\x1b[4mBookmark Manager\x1b[0m")

    char = "w"

    while True:
        tui.draw_tabs(tabs, tab_highlight)
        tui.draw_options(tabs[tab_highlight])
        tui.draw_keypress(char)
        char = tui.getch(True)

        if char == "q":
            break

        elif char == "\x1b":  # beginning of escape sequence
            char = tui.handle_esc()
            if char == "up" and tabs[tab_highlight][1] > 0:
                tabs[tab_highlight][1] -= 1
            elif char == "dn" and tabs[tab_highlight][1] < len(tabs[tab_highlight][0].children) - 1:
                tabs[tab_highlight][1] += 1
            elif char == "shft+tb" and tab_highlight > 0:
                tab_highlight -= 1
                print("\x1b[3;0H\x1b[0J", end="")
            elif char == "lf":
                parent_folder()
            elif char == "rt":
                if tabs[tab_highlight][0].children[tabs[tab_highlight][1]].typee == "folder":
                    tabs[tab_highlight][0].children[tabs[tab_highlight][1]].command()

        elif char == "\t":  # NOTE tab isn't an ansi esc sequence os its handled here instead
            char = "tab"  # to show on screen
            if tab_highlight < len(tabs) - 1:
                tab_highlight += 1
                print("\x1b[3;0H\x1b[0J", end="")

        elif ord(char) == 10:
            char = "ent"  # to show on screen
            try:
                pass
                tabs[tab_highlight][0].children[tabs[tab_highlight][1]].command()
            except Exception as e:
                log("operation failed: " + tabs[tab_highlight][0].name + "/" + tabs[tab_highlight][0].children[tabs[tab_highlight][1]].name)
                quit(1, e)

        #tui.draw_keypress(char)


if __name__ == "__main__":
    main()
    quit(0, "")
