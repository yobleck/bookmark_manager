# UI handler
import sys
import termios
import datetime
import shutil


def log(i) -> None:
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


def draw_tabs(tabs: list, hl: int) -> None:
    w, h = shutil.get_terminal_size()
    print("\x1b[2;0H", end="")
    for i, t in enumerate(tabs):
        if i == hl:
            print("\x1b[7m" + t[0].name + "\x1b[0m", end=" ")
        else:
            print(t[0].name, end=" ")


def draw_options(tab):
    w, h = shutil.get_terminal_size()

    print("\x1b[3;0H", end="")
    for i, o in enumerate(tab[0].children):
        if i == tab[1]:
            print("\x1b[7m" + o.name + "\x1b[0m")
        else:
            print(o.name)
