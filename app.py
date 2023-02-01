import curses
import os

HL = "\u2500"
VL = "\u2502"
TL = "\u250C"
TR = "\u2510"
BL = "\u2514"
BR = "\u2518"

log = open("log", "w")

def main(stdscr):
    curses.curs_set(0)
    
    mode = "menu"
    active = 0
    
    titles = ["one", "two", "three"]
    bodies = ["oneneone", "this my note", "threeeed"]

    while True:
        stdscr.clear()
        rows, cols = stdscr.getmaxyx()

        active_title = titles[active]

        log.write(mode)

        menu_width = int((1 / 3) * cols)
        editor_width = cols - menu_width
        stdscr.addstr(0, 0, TL + HL + " CeaseNotes " + HL * (menu_width - 15) + TR)
        stdscr.addstr(0, menu_width, TL + HL + " " + active_title + " " + HL * (editor_width - (len(active_title) + 5)) + TR)
        
        for line in range(rows - 2):
            y = line + 1
            stdscr.addstr(y, 0, VL)
            stdscr.addstr(y, menu_width, VL)
            stdscr.addstr(y, menu_width - 1, VL)
            stdscr.addstr(y, menu_width + editor_width - 1, VL)

        stdscr.addstr(BL + HL * (menu_width - 2) + BR + BL + HL * (editor_width - 2))
        try:
            stdscr.addstr(BR)
        except:
            pass

        if mode == "askclose":
            ask_y = int((rows - 2) / 2)
            x_center = int((menu_width - 2) / 2)
            stdscr.addstr(ask_y, x_center - 5, "Press ENTER")
            stdscr.addstr(ask_y + 1, x_center - 3, "to exit")

        else:
            for index in range(len(titles)):
                if active == index:
                    if mode == "menu":
                        style = curses.A_UNDERLINE
                    else:
                        style = curses.A_STANDOUT
                else:
                    style = curses.A_NORMAL

                stdscr.addstr(index + 1, 1, titles[index], style)

        key = stdscr.getkey()

        if mode == "menu":
            if key == "^[":
                mode = "askclose"
            elif key == "KEY_DOWN":
                active += 1
                if active > len(titles) - 1:
                    active = 0
            elif key == "KEY_UP":
                active -= 1
                if active < 0:
                    active = len(titles) - 1
            elif key == "\n":
                mode = "note"

        elif mode == "note":
            if key == "^[":
                mode = "menu"
            else:
                pass

        elif mode == "askclose":
            if key == "\n":
                break
            else:
                mode = "menu"

if __name__ == "__main__":
    os.environ.setdefault("ESCDELAY", "25")
    message = curses.wrapper(main)
    if message: print(message)

    log.close()