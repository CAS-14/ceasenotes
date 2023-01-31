import curses

HL = "\u2500"
VL = "\u2502"
TL = "\u250C"
TR = "\u2510"
BL = "\u2514"
BR = "\u2518"

def main(stdscr):
    curses.curs_set(0)

    menu_width = int((1 / 3) * curses.COLS)
    editor_width = curses.COLS - menu_width
    stdscr.addstr(TL)
    stdscr.addstr(HL * (menu_width - 2))
    stdscr.addstr(TR)
    stdscr.addstr(TL)
    stdscr.addstr(HL * (editor_width - 2))
    stdscr.addstr(TR)
    
    for line in range(curses.LINES - 2):
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
    #stdscr.addstr(BR)

    stdscr.getkey()

if __name__ == "__main__":
    message = curses.wrapper(main)
    print(message)