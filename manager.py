# Bookmark viewer and synchronizer for chromium and firefox
import sys
from functools import partial
import setproctitle  # TODO make this optional

import tui
import bookmarks
import utils


setproctitle.setproctitle("bookmark_manager")


def main() -> None:
    # Generate fake folders for menus
    tabs = []
    tab_highlight = 0


    def enter_folder() -> None:
        tab = tabs[tab_highlight]
        option = tab[0].children[tab[1]]
        utils.log("enter folder: " + option.name)
        tabs[tab_highlight] = [option, 0]
        #tabs[tab_highlight] = [tabs[tab_highlight][0].children[tabs[tab_highlight][1]], 0]  # TODO condense to one line


    def parent_folder() -> None:
        tab = tabs[tab_highlight]
        parent = tab[0].parent
        utils.log("go up to folder: " + parent.name)
        tabs[tab_highlight] = [parent, 0]


    def add_tab(folder) -> None:
        nonlocal tabs  # WARNING I've coded myself into a corner here. TOO BAD
        tabs.append([folder, 0])  # tab as object?


    def do_chromium():
        nonlocal tabs
        c_j = bookmarks.import_c(utils.config["chromium_filepath"])
        c_fol = bookmarks.create_c_tree(c_j, None, enter_folder)
        tab_exists = False
        for i, t in enumerate(tabs):
            if t[0].name == "chromium":
                tab_exists = True
                break
        if tab_exists:
            tabs[i] = [c_fol, 0]
        else:
            add_tab(c_fol)  # BUG adds new tab if old tab is in subfolder


    def create_initial_tabs() -> list:
        nonlocal tabs
        #tabs = []
        main = bookmarks.folder("Main", utils.no_op)
        for f in [("Import Firefox", utils.no_op),
                ("Import Chromium", do_chromium),
                ("Import Both", utils.no_op),
                ("Help", enter_folder),
                ("Quit", partial(utils.quit, 0, ""))]:
            main.add_folder(*f)
        tabs.append([main, 0])  # NOTE second item keeps track of highlight pos

        help_m = main.children[3]  # TODO DONT HARD CODE THIS. bookmarks.folder("Help", utils.no_op)
        for f in [("tab/shift+tab to change tabs", utils.no_op),
                  ("up/down arrow keys to change selection", utils.no_op),
                  ("right arrow key to enter folder", utils.no_op),
                  ("left arrow key to return to parent folder", utils.no_op),
                  ("d to delete tab", utils.no_op),
                  ("enter to select highlighted option", utils.no_op),
                  ("\x1b[32mfolders are green and\x1b[34m urls are blue\x1b[0m", utils.no_op),
                  ("q to quit", partial(utils.quit, 0, "")),]:
            help_m.add_folder(*f)
        return tabs
    tabs = create_initial_tabs()


    #ff_j = bookmarks.import_ff(utils.config["firefox_filepath"])


    bookmark_temp = bookmarks.folder("test", utils.no_op)
    for f in [("folder1", enter_folder), ("folder2", enter_folder)]:
        bookmark_temp.add_folder(*f)
        bookmark_temp.children[-1].add_bookmark("yc", "https://news.ycombinator.com/")
    for f in [("yt", "https://www.youtube.com/feed/channels"), ("yc", "https://news.ycombinator.com/")]:
        bookmark_temp.add_bookmark(*f)

    add_tab(bookmark_temp)


    print("\x1b[2J\x1b[H", end="")  # clear screen
    print("\x1b[4mBookmark Manager\x1b[0m")


    char = "w"  # null character?

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
                utils.log("operation failed: " + tabs[tab_highlight][0].name + "/" + tabs[tab_highlight][0].children[tabs[tab_highlight][1]].name)
                utils.quit(1, e)


        elif char == "d":
            if tab_highlight > 0:
                old = tab_highlight
                tab_highlight = 0
                try:
                    del tabs[old]
                except Exception as e:
                    utils.log("failed to delete folder")
                    utils.quit(1, e)


if __name__ == "__main__":
    main()
    utils.quit(0, "")
