import curses
import os
import sqlite3
import random
from datetime import datetime

LOGGING = True

if LOGGING:
    with open("cn.log", "w") as f:
        f.write("")

def log(message: str):
    if LOGGING:
        message = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
        with open("cn.log", "a") as f:
            f.write(message)

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

# INSERT INTO notes (name, created, edited, content) VALUES ();

def main(stdscr):
    curses.curs_set(0)
    
    mode = "menu"
    note_active = 0
    menu_items = ["View/edit", "Create", "Delete", "Settings", "Quit"]
    menu_active = 0
    add_char = None
    added_end_position = None
    skip_now = False

    while True:
        stdscr.clear()
        rows, cols = stdscr.getmaxyx()

        if cols < MIN_WIDTH or rows < MIN_HEIGHT:
            return f"Terminal must be at least {MIN_WIDTH} wide by {MIN_HEIGHT} high!"

        note_names = cur.execute("SELECT name FROM notes ORDER BY edited DESC").fetchall()
        note_names = [name[0] for name in note_names]

        if len(note_names) > 0 and note_active >= 0:
            active_title = note_names[note_active]
        else:
            active_title = None

        menu_width = int((1 / 3) * cols)
        editor_width = cols - menu_width
        


        # EDGE RENDERING

        stdscr.addstr(0, 0, TL + HL * (menu_width - 2) + TR)
        stdscr.addstr(0, 2, " CeaseNotes ")
        stdscr.addstr(0, menu_width, TL + HL * (editor_width - 2) + TR)
        
        if active_title and mode != "menu":
            stdscr.addstr(0, menu_width + 2, " " + active_title + " ")
        
        else:
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



        # MODE ACTIONS

        # render action menu
        if mode == "menu":
            for menu_index in range(len(menu_items)):
                if menu_active == menu_index:
                    style = curses.A_REVERSE
                else:
                    style = curses.A_NORMAL

                stdscr.addstr(menu_index + 1, 1, menu_items[menu_index], style)

        # ask before exiting
        elif mode == "askclose":
            y_center = int((rows - 2) / 2)
            x_center = int((menu_width - 2) / 2)
            stdscr.addstr(y_center, x_center - 5, "Press ENTER")
            stdscr.addstr(y_center + 1, x_center - 3, "to exit")

        # all modes which show notes, besides nonotes
        elif mode in ["list", "note", "delete", "nonotes", "create"]:

            # render notes list
            if note_names and mode != "nonotes":
                for note_index in range(len(note_names)):
                    if note_active == note_index:
                        content = cur.execute(
                            "SELECT content FROM notes WHERE name = ?",
                            (note_names[note_index],)
                        ).fetchone()[0]

                        # place note content in viewer/editor
                        words = content.split(" ")
                        line_length = 0
                        row = 1
                        i = 0
                        while i < len(words):
                            added_part = words[i]

                            if i < len(words) - 1:
                                added_part += " "

                            elif i == len(words) - 1 and mode == "note" and add_char:
                                added_part += add_char
                                

                            if line_length + len(added_part) > editor_width - 2:
                                row += 1
                                line_length = 0
                            else:
                                stdscr.addstr(row, menu_width + line_length + 1, added_part)
                                i += 1
                                line_length += len(added_part)
                                added_end_position = stdscr.getyx()

                        # set style of selected note in menu
                        if mode == "note":
                            # TODO curs set stuff
                            curses.curs_set(1)
                            style = curses.A_STANDOUT | curses.A_DIM

                        else:
                            style = curses.A_REVERSE

                        # write new character to note
                        if mode == "note" and add_char:
                            content += add_char
                            cur.execute(
                                "UPDATE notes SET content = ? WHERE name = ?",
                                (content, note_names[note_index])
                            )
                            add_char = None
                            con.commit()

                    else:
                        style = curses.A_NORMAL

                    name = note_names[note_index]
                    if len(name) > menu_width - 2:
                        name = name[:(menu_width - 5)] + "..."
                    stdscr.addstr(note_index + 1, 1, name, style)

                    if added_end_position:
                        stdscr.move(*added_end_position)
                        added_end_position = None

            else:
                y_center = int((rows - 2) / 2)
                x_center = int((menu_width - 2) / 2)
                stdscr.addstr(y_center, x_center - 6, "No notes yet!")
                stdscr.addstr(y_center + 1, x_center - 5, "Press ENTER")
                mode = "nonotes"

        # create new note
        elif mode == "create":
            stdscr.addstr(0, menu_width + 2, " name: ", curses.A_DIM)
            curses.curs_set(2)
            title = ""
            cont = None
            
            while True:
                stdscr.addstr(0, menu_width + 9, title)
                stdscr.addstr(0, menu_width + 9 + len(title), "  ")
                
                key = stdscr.getch()
                if key == 27:
                    cont = False
                    break
                elif key == "\n":
                    cont = True
                    break
                else:
                    title += chr(key)

            curses.curs_set(0)

            if not cont:
                mode = "menu"

            else:
                # create the note
                now = datetime.timestamp(datetime.now())
                cur.execute(
                    "INSERT INTO notes (name, created, edited, content) VALUES (?, ?, ?, ?);",
                    (title, now, now, "")
                )
                note_active = 0
                mode = "note"
        
        else:
            return("Error: Unknown mode!")



        # KEY HANDLING

        if skip_now:
            skip_now = False
        else:
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
                if 0 <= menu_active <= 3:
                    mode = ["list", "create", "delete", "settings"][menu_active]
                else:
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
                curses.curs_set(0)
                mode = "list" if mode == "note" else "menu"

            else:
                add_char = chr(key)

        elif mode == "askclose":
            if key in [curses.KEY_ENTER, 10, 13]:
                break
            else:
                mode = "list"

        elif mode == "nonotes":
            if key in [curses.KEY_ENTER, 10, 13]:
                mode = "menu"
            else:
                pass



if __name__ == "__main__":
    os.environ.setdefault("ESCDELAY", "25")
    message = curses.wrapper(main)
    if message: print(message)