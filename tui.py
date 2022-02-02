# UI handler
import sys
import termios
import datetime
import shutil
import json


with open("./config.json", "r") as f:
    try:
        config = json.load(f)
    except Exception as e:
        print("config failed to load:")
        raise Exception(e)


def log(i) -> None:
    if config["logging"]:
        with open("log.txt", "a+") as f:
            f.write(datetime.datetime.now().isoformat() + ": " + str(i) + "\n")


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


esc_chars = {"A": "up", "B": "dn", "C": "rt", "D": "lf", "Z": "shft+tb"}
def handle_esc() -> str:
    a = getch(False)
    #log("a" + a)
    if a == "[":
        k = getch(False)  # assuming 3 bytes for now
        #log("k " + k)
        if k in esc_chars.keys():
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
    for i, o in enumerate(tab[0].children):
        if i == tab[1]:
            print("\x1b[7m" + colors[o.typee] + o.name + "\x1b[0m")
        else:
            print(colors[o.typee] + o.name + "\x1b[0m")
