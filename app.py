import curses

HL = "\u2500"
VL = "\u2502"
TL = "\u250C"
TR = "\u2510"
BL = "\u2514"
BR = "\u2518"

def main(stdscr):
    curses.curs_set(0)
    active_note = None
    mode = "menu"
    active_item = 0
    notes = ["one", "two", "three"]

    while True:
        stdscr.clear()
        rows, cols = stdscr.getmaxyx()

        if active_note:
            active_title = "blah blah blah"
        else:
            active_title = "No note selected"

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

        stdscr.addstr(BL)
        stdscr.addstr(HL * (menu_width - 2))
        stdscr.addstr(BR)
        stdscr.addstr(BL)
        stdscr.addstr(HL * (editor_width - 2))
        try:
            stdscr.addstr(BR)
        except:
            pass

        key = stdscr.getkey()

        stdscr.addstr(0, 0, key)

        key = stdscr.getkey()

        if key in ["^[", "KEY_ESCAPE"]:
            if mode == "menu":
                mode = "askclose"

            else:
                mode = "menu"

        elif mode == "menu":
            if key == "KEY_DOWN":
                active_item += 1

if __name__ == "__main__":
    message = curses.wrapper(main)
    if message: print(message)