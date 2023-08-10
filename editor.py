""" A simple text editor using curses library """

import curses
import curses.ascii
import sys


def main(_: "curses._CursesWindow") -> None:
    # create a second screen over the first layer
    stdscr = curses.initscr()
    # disable default character echoing
    curses.noecho()
    # disable normal line buffering, quit/suspend and other flow control keys
    curses.raw()
    # enable non-blocking mode for `getch()`
    stdscr.nodelay(1)
    # enable extra keys such as ENTER, BACKSPACE, CTRL etc.
    stdscr.keypad(1)

    # initialize a content buffer: 2D list of ASCII values of characters
    buffer: list[list[int]] = list()
    # name of the source file
    source_file = "default.txt"

    if len(sys.argv) == 2:
        # a filename is provided
        source_file = sys.argv[1]

    try:
        # try opening the source file in read mode
        # and load the available content in the buffer
        with open(source_file) as fd:
            for line in fd.readlines():
                buffer.append([ord(char) for char in line.rstrip()])
    except FileNotFoundError:
        buffer.append([])

    # get height and width of the screen
    height, width = stdscr.getmaxyx()

    # top left coordinates of the visible screen wrt the absolute origin
    scr_row = scr_col = 0
    # cursor position wrt the absolute origin
    cursor_row = cursor_col = 0

    # event loop
    while True:
        stdscr.move(0, 0)

        # adjust screen coordinates to ensure that the cursor is always visible
        if cursor_row < scr_row:
            scr_row = cursor_row
        elif cursor_row >= scr_row + height:
            scr_row = cursor_row - height + 1
        if cursor_col < scr_col:
            scr_col = cursor_col
        elif cursor_col >= scr_col + width:
            scr_col = cursor_col - width + 1

        for row in range(height):
            for col in range(width):
                try:
                    stdscr.addch(row, col, buffer[scr_row + row][scr_col + col])
                except IndexError:
                    pass
            # clear remaining characters on the line (possibly previously printed)
            stdscr.clrtoeol()
            # add new line character
            try:
                stdscr.addch("\n")
            except:
                pass

        # move the cursor to the current position
        # `cursor_row` and `cursor_col` are wrt to the absolute origin
        # actual position is calculated relative to `scr_row` and `scr_col`
        curses.curs_set(0)
        stdscr.move(cursor_row - scr_row, cursor_col - scr_col)
        curses.curs_set(1)
        stdscr.refresh()

        # wait for character input
        char = -1
        while char < 0:
            char = stdscr.getch()

        # `CTRL+Q` to quit
        if char == curses.ascii.ctrl(ord("q")):
            break
        # `CTRL+S` to save file
        if char == curses.ascii.ctrl(ord("s")):
            with open(source_file, "w") as fd:
                fd.write("\n".join(["".join(chr(c) for c in line) for line in buffer]))
        # move up
        elif char == curses.KEY_UP and cursor_row > 0:
            cursor_row -= 1
        # move down
        elif char == curses.KEY_DOWN and cursor_row < len(buffer) - 1:
            cursor_row += 1
        # move left with wrap around to previous line
        elif char == curses.KEY_LEFT:
            if cursor_row > 0 or cursor_col > 0:
                cursor_col -= 1
            if cursor_col < 0:
                cursor_row -= 1
                cursor_col = len(buffer[cursor_row])
        # move right with wrap around to next line
        elif char == curses.KEY_RIGHT:
            if cursor_row < len(buffer) - 1 or cursor_col < len(buffer[cursor_row]):
                cursor_col += 1
            if cursor_col > len(buffer[cursor_row]):
                cursor_row += 1
                cursor_col = 0
        # jump to beginning of the current line
        elif char == curses.KEY_HOME:
            cursor_col = 0
        # jump to the end of the current line
        elif char == curses.KEY_END:
            cursor_col = len(buffer[cursor_row])
        # insert new line with `ENTER`
        elif chr(char) == "\n":
            next_row_content = buffer[cursor_row][cursor_col:]
            buffer[cursor_row] = buffer[cursor_row][:cursor_col]
            cursor_row += 1
            cursor_col = 0
            buffer.insert(cursor_row, next_row_content)
        # delete a character with `BACKSPACE`
        elif char == curses.KEY_BACKSPACE:
            if cursor_col > 0:
                cursor_col -= 1
                del buffer[cursor_row][cursor_col]
            elif cursor_row > 0:
                cursor_col = len(buffer[cursor_row - 1])
                buffer[cursor_row - 1].extend(buffer[cursor_row])
                del buffer[cursor_row]
                cursor_row -= 1
        # printable character
        elif 31 < char < 127:
            if cursor_col == len(buffer[cursor_row]):
                buffer[cursor_row].append(char)
            else:
                buffer[cursor_row].insert(cursor_col, char)
            cursor_col += 1

        # fix `cursor_col` if its out of buffer line
        if cursor_row >= len(buffer):
            cursor_col = 0
        elif cursor_col > len(buffer[cursor_row]):
            cursor_col = len(buffer[cursor_row])


if __name__ == "__main__":
    curses.wrapper(main)
