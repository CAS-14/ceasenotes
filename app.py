import curses
import os
import sqlite3
import random

HL = "\u2500"
VL = "\u2502"
TL = "\u250C"
TR = "\u2510"
BL = "\u2514"
BR = "\u2518"

MIN_WIDTH = 48
MIN_HEIGHT = 7

con = sqlite3.connect("notes.db")
cur = con.cursor()

tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
if not tables:
    cur.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL, created INTEGER NOT NULL, edited INTEGER NOT NULL, content TEXT NOT NULL)")
    con.commit()

def main(stdscr):
    curses.curs_set(0)
    
    mode = "menu"
    note_active = 0
    menu_items = ["View/edit", "Create", "Delete", "Settings", "Quit"]
    menu_active = 0

    while True:
        stdscr.clear()
        rows, cols = stdscr.getmaxyx()

        if cols < MIN_WIDTH or rows < MIN_HEIGHT:
            return f"Terminal must be at least {MIN_WIDTH} wide by {MIN_HEIGHT} high!"

        note_names = cur.execute("SELECT name FROM notes ORDER BY edited DESC").fetchall()

        if len(note_names) > 0:
            active_title = note_names[note_active]
        else:
            active_title = None

        menu_width = int((1 / 3) * cols)
        editor_width = cols - menu_width
        
        stdscr.addstr(0, 0, TL + HL * (menu_width - 2) + TR)
        stdscr.addstr(0, 2, " CeaseNotes ")
        stdscr.addstr(0, menu_width, TL + HL * (editor_width - 2) + TR)
        
        if active_title:
            stdscr.addstr(0, menu_width + 2, " " + active_title + " ")
        
        else:
            note_names = ["John", "The World", "I like Food", "Dingleton", "MYLIFEASAMOVIESTAR", "the final meal", "Notes on song", "lyrics2"]

            for name in note_names:
                place_y = random.randint(1, rows - 2)
                place_x = random.randint(menu_width + 1, cols - (2 + len(name)))
                stdscr.addstr(place_y, place_x, name)
        
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

        if mode == "menu":
            for menu_index in range(len(menu_items)):
                if menu_active == menu_index:
                    style = curses.A_REVERSE

                else:
                    style = curses.A_NORMAL

                stdscr.addstr(menu_index + 1, 1, menu_items[menu_index], style)

        elif mode == "askclose":
            ask_y = int((rows - 2) / 2)
            x_center = int((menu_width - 2) / 2)
            stdscr.addstr(ask_y, x_center - 5, "Press ENTER")
            stdscr.addstr(ask_y + 1, x_center - 3, "to exit")

        elif mode in ["list", "note"]:
            for note_index in range(len(note_names)):
                if note_active == note_index:
                    if mode == "list":
                        style = curses.A_REVERSE
                    else:
                        style = curses.A_STANDOUT | curses.A_DIM
                else:
                    style = curses.A_NORMAL

                stdscr.addstr(note_index + 1, 1, note_names[note_index], style)

        else:
            return("Error: Unknown mode")

        key = stdscr.getch()

        if mode == "menu":
            if key == 27:
                mode = "askclose"
            elif key == curses.KEY_DOWN:
                menu_active += 1
                if menu_active > len(menu_items) - 1:
                    menu_active = 0
            elif key == curses.KEY_UP:
                menu_active -= 1
                if menu_active < 0:
                    menu_active = len(menu_items) - 1
            elif key in [curses.KEY_ENTER, 10, 13]:
                if menu_active == 0:
                    mode = "list"
                elif menu_active == 1:
                    mode = "create"
                elif menu_active == 2:
                    mode = "delete"
                elif menu_active == 3:
                    mode = "settings"
                elif menu_active == 4:
                    break

        elif mode == "list":
            if key == 27:
                mode = "menu"
            elif key == curses.KEY_DOWN:
                note_active += 1
                if note_active > len(note_names) - 1:
                    note_active = 0
            elif key == curses.KEY_UP:
                note_active -= 1
                if note_active < 0:
                    note_active = len(note_names) - 1
            elif key in [curses.KEY_ENTER, 10, 13]:
                mode = "note"

        elif mode == "note":
            if key == 27:
                mode = "list"
            else:
                pass

        elif mode == "askclose":
            if key in [curses.KEY_ENTER, 10, 13]:
                break
            else:
                mode = "list"

if __name__ == "__main__":
    os.environ.setdefault("ESCDELAY", "25")
    message = curses.wrapper(main)
    if message: print(message)