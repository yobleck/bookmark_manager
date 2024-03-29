# UI handler
import shutil
import sys
import termios

import utils


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
    #utils.log(bytes(ch, "utf-8"))
    return ch


esc_chars = {"A": "up", "B": "dn", "C": "rt", "D": "lf", "Z": "shft+tb", "5": "pgup", "6": "pgdn"}


def handle_esc() -> str:
    a = getch(False)
    #utils.log("a" + a)
    if a == "[":
        k = getch(False)  # assuming 3 bytes for now
        #utils.log("k " + k)
        if k in esc_chars.keys():
            if k in ["5","6"]:
                getch(False)  # eat useless ~ char
            return esc_chars[k]
        return "esc[ error: " + a + k
    return "esc"


def draw_keypress(ch: str) -> None:
    w, h = shutil.get_terminal_size()
    print("\x1b[" + str(h) + ";0H\x1b[0K\x1b[0G", end="")  # erase bottom line
    print("pressed: " + ch + " \x1b[1A")


def draw_tabs(tabs: list, hl: int) -> None:
    w, h = shutil.get_terminal_size()
    print("\x1b[2;0H\x1b[0K", end="")
    for i, t in enumerate(tabs):
        if i == hl:
            print("\x1b[7m" + t[0].name + "\x1b[0m", end=" ")
        else:
            print(t[0].name, end=" ")


colors = {"folder": "\x1b[32m", "url": "\x1b[34m"}


def draw_options(tab: list) -> None:
    w, h = shutil.get_terminal_size()
    print("\x1b[3;0H\x1b[0J", end="")

    t = 0; b = h-3
    if tab[1] >= h-3:
        t = tab[1] - h-3 +7
        b = t + h-3

    for i, o in enumerate(tab[0].children):
        if i >= t and i < b:
            if i == tab[1]:
                print("\x1b[7m" + colors[o.typee] + o.name[:w] + "\x1b[0m")
            else:
                print(colors[o.typee] + o.name[:w] + "\x1b[0m")
