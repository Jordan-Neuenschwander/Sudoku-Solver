import tkinter as tk
import csv
import copy
import random

CELL_SIZE = 30
BOARD_MARGIN = 10
NUM_CELLS = 9
MAX_PUZZLES = 50
BUTTON_SIZE = 50

WINDOW_HEIGHT = BOARD_MARGIN * 2 + CELL_SIZE * NUM_CELLS
WINDOW_WIDTH = BOARD_MARGIN * 2 + CELL_SIZE * NUM_CELLS


class SudokuBoard(tk.Frame):

    def __init__(self, parent_container):
        tk.Frame.__init__(self, parent_container)
        self.parent = parent_container
        self.selected_cell = (-1, -1)
        self.canvas = tk.Canvas(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.puzzle_values = []
        self.protected_cells = []
        self.puzzle_dictionary = {}

        for i in range(NUM_CELLS):
            temp_list = []
            self.puzzle_values.append(temp_list)
            for j in range(NUM_CELLS):
                self.puzzle_values[i].append(0)

        self.blocks = {}

        block_cells = []
        for i in range(NUM_CELLS//3):
            for j in range(NUM_CELLS//3):
                self.blocks[(i, j)] = []
                block_cells.append((i, j))

        for i in range(NUM_CELLS//3):
            for j in range(NUM_CELLS//3):
                for cell in block_cells:
                    self.blocks.get((i, j)).append((cell[0] + 3 * i, cell[1] + 3 * j))

        self.parent.title("Sudoku Solver")

        # Stretch SudokuWindow tk.Frame to fill entire parent container
        self.pack(fill=tk.BOTH, expand=True)

        # Stretch tk.Canvas to fill entire parent frame
        self.canvas.pack(fill=tk.BOTH, side=tk.TOP)

        self.__draw_board()
        self.__draw_buttons()

        # Event handler for left mouse button click
        self.canvas.bind("<Button-1>", self.__on_left_click)

        # Event handler for key press
        self.canvas.bind("<KeyRelease>", self.__on_key_release)

        self.__read_puzzle_csv()

        self.__load_puzzle()

    def __draw_buttons(self):
        new_puzzle_button = tk.Button(self.parent, text='New Puzzle', command=self.__on_click_new_puzzle)
        clear_button = tk.Button(self.parent, text='Clear Puzzle', command=self.__on_click_clear)
        solve_puzzle_button = tk.Button(self.parent, text='Solve Puzzle', command=self.__on_click_solve)

        new_puzzle_button.pack(side=tk.LEFT, expand=True)
        clear_button.pack(side=tk.RIGHT, expand=True)
        solve_puzzle_button.pack(side=tk.RIGHT, expand=True)

    def __draw_board(self):
        """
        Draws the vertical and horizontal lines of the grid that represents the sudoku game board
        Every third grid line is drawn darker and thicker to denote the different squares of the sudoku board

        :return: void
        """
        for i in range(NUM_CELLS + 1):
            if i % 3 == 0:
                line_color = "black"
                line_width = 2
            else:
                line_color = "gray"
                line_width = 1

            # Draw the vertical gridlines
            x0 = i * CELL_SIZE + BOARD_MARGIN
            x1 = x0
            y0 = BOARD_MARGIN
            y1 = WINDOW_HEIGHT - BOARD_MARGIN

            self.canvas.create_line(x0, y0, x1, y1, fill=line_color, width=line_width)

            # Draw the horizontal gridlines
            x0 = BOARD_MARGIN
            x1 = WINDOW_WIDTH - BOARD_MARGIN
            y0 = i * CELL_SIZE + BOARD_MARGIN
            y1 = y0

            self.canvas.create_line(x0, y0, x1, y1, fill=line_color, width=line_width)

    def __draw_values(self):
        """
        Clears the cell values and repopulates the cells with the values contained within the values list
        :param values: 2D list containing the values of the individual cells on the sudoku board
        :return: null
        """
        self.canvas.delete("value")

        for i in range(len(self.puzzle_values)):
            for j in range(NUM_CELLS):
                if self.puzzle_values[i][j] < 1:
                    continue

                x = BOARD_MARGIN + (CELL_SIZE * j) + CELL_SIZE / 2
                y = BOARD_MARGIN + (CELL_SIZE * i) + CELL_SIZE / 2

                if (i, j) in self.protected_cells:
                    color = "red"
                else:
                    color = "black"

                self.canvas.create_text(x, y, text=self.puzzle_values[i][j], fill=color, tag="value")

    def __clear_values(self):
        self.canvas.delete("value")
        self.puzzle_values.clear()

        for i in range(NUM_CELLS):
            temp_list = []
            self.puzzle_values.append(temp_list)
            for j in range(NUM_CELLS):
                self.puzzle_values[i].append(0)

    def __find_cell(self, x: int, y: int) -> tuple:
        """
        Finds the row and column number of the cell that contains the coordinates given
        :param x: the x-coordinate located within a cell
        :param y: the y-coordinate located within a cell
        :return: a tuple containing the row and column number of the cell (row, column)
        """
        cell_row = (y - BOARD_MARGIN) // CELL_SIZE
        cell_column = (x - BOARD_MARGIN) // CELL_SIZE

        return cell_row, cell_column

    def __select_cell(self, x: int, y: int):
        self.canvas.delete("selector")
        self.selected_cell = self.__find_cell(x, y)

        x0 = BOARD_MARGIN + CELL_SIZE * self.selected_cell[1] + 1
        y0 = BOARD_MARGIN + CELL_SIZE * self.selected_cell[0] + 1

        x1 = BOARD_MARGIN + CELL_SIZE * (self.selected_cell[1] + 1) - 1
        y1 = BOARD_MARGIN + CELL_SIZE * (self.selected_cell[0] + 1) - 1
        self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", tag="selector", width=2)

    def __on_click_clear(self):
        self.__load_puzzle(self.puzzle_id)

    def __on_click_solve(self):
        self.___solve_puzzle()

    def __on_click_new_puzzle(self):
        self.__load_puzzle(random.choice(range(len(self.puzzle_dictionary))))

    def __on_key_release(self, event):
        if event.char not in "0123456789":
            return

        valid_str = self.__validate_move(int(event.char))
        if 'Valid' in valid_str:
            self.puzzle_values[self.selected_cell[0]][self.selected_cell[1]] = int(event.char)
            self.__draw_values()
            if self.__check_victory():
                print('victory')
        else:
            print(valid_str)

    def __on_left_click(self, event):
        # Returns if the click was not within the game board
        if not (BOARD_MARGIN < event.x < WINDOW_WIDTH - BOARD_MARGIN
                and BOARD_MARGIN < event.y < WINDOW_HEIGHT - BOARD_MARGIN):
            return

        self.__select_cell(event.x, event.y)
        self.canvas.focus_set()

    def __validate_move(self, move: int) -> str:
        if self.selected_cell in self.protected_cells:
            return 'Invalid Move: Cannot alter starting value'

        if move == 0:
            self.puzzle_values[self.selected_cell[0]][self.selected_cell[1]] = 0
            return 'Valid Move'

        for i in range(NUM_CELLS):
            # check row
            if self.puzzle_values[self.selected_cell[0]][i] == move:
                return 'Invalid Move: Duplicate value in row'

            # check column
            elif self.puzzle_values[i][self.selected_cell[1]] == move:
                return 'Invalid Move: Duplicate value in column'

        block_row = self.selected_cell[0]//3
        block_col = self.selected_cell[1]//3

        # check block
        current_block = self.blocks.get((block_row, block_col))
        for cell in current_block:
            if self.puzzle_values[cell[0]][cell[1]] == move:
                return 'Invalid Move: Duplicate value in block'

        return 'Valid Move'

    def __check_victory(self) -> bool:
        # check rows
        check_set = set()
        for i in range(NUM_CELLS):
            check_set.clear()
            for j in range(NUM_CELLS):
                check_set.add(self.puzzle_values[i][j])
                if j == NUM_CELLS - 1 and check_set != set(range(1, 10)):
                    return False

        # check columns
        for i in range(NUM_CELLS):
            check_set.clear()
            for j in range(NUM_CELLS):
                check_set.add(self.puzzle_values[j][i])
                if j == NUM_CELLS - 1 and check_set != set(range(1, 10)):
                    return False

        # check blocks
        for i in range(3):
            for j in range(3):
                cell_list = self.blocks.get((i, j))
                for cell in cell_list:
                    check_set.add(self.puzzle_values[cell[0]][cell[1]])
                    if j == NUM_CELLS - 1 and check_set != set(range(1, 10)):
                        return False

                check_set.clear()

        return True

    def __load_puzzle(self, new_puzzle_id=5):
        self.protected_cells.clear()
        self.puzzle_id = new_puzzle_id
        self.__clear_values()

        self.puzzle_values = copy.deepcopy(self.puzzle_dictionary.get(new_puzzle_id))

        for i in range(9):
            for j in range(9):
                if self.puzzle_values[i][j] != 0:
                    self.protected_cells.append((i, j))

        self.__draw_values()

    def __read_puzzle_csv(self):
        with open('resources/puzzles.csv') as csv_puzzles:
            reader = csv.reader(csv_puzzles, delimiter=',')
            line_count = 0
            for row in reader:
                if line_count == 0:
                    line_count += 1
                    continue
                if line_count == MAX_PUZZLES:
                    break

                self.puzzle_dictionary[line_count-1] = []

                for i in range(9):
                    self.puzzle_dictionary[line_count-1].append([])
                    for j in range(9):
                        self.puzzle_dictionary[line_count-1][i].append(int(row[0][9 * i + j]))

                line_count += 1

    # start solve AI
    # split into different object?
    def ___solve_puzzle(self):
        self.preemptive_sets = {}
        for i in range(9):
            for j in range(9):
                self.preemptive_sets[(i, j)] = set(range(1, 10))

        change = True

        while change is True:
            change = False
            # create pre-emptive sets
            self.__update_preemptive_by_block()
            self.__update_preemptive_by_row()
            self.__update_preemptive_by_col()

            # add forced
            for cell in self.preemptive_sets:
                if len(self.preemptive_sets.get(cell)) == 1:
                    self.puzzle_values[cell[0]][cell[1]] = min(self.preemptive_sets.get(cell))
                    change = True

            self.__draw_values()

        if self.__check_victory():
            print('Victory!')
        # look for pre-emptive groups in col, row, square
        # repeat until no groups found and select a random cell and a random number
        # repeat

    def __update_preemptive_by_block(self):
        for block_coords in self.blocks:
            block_set = set()

            for cell in self.blocks.get(block_coords):
                if self.puzzle_values[cell[0]][cell[1]] != 0:
                    block_set.add(self.puzzle_values[cell[0]][cell[1]])

            for cell in self.blocks.get(block_coords):
                if self.puzzle_values[cell[0]][cell[1]] != 0:
                    self.preemptive_sets[cell] = set()
                else:
                    self.preemptive_sets[cell] = self.preemptive_sets.get(cell).difference(block_set)

    def __update_preemptive_by_row(self):
        for i in range(9):
            row_set = set()

            for j in range(9):
                if self.puzzle_values[i][j] != 0:
                    row_set.add(self.puzzle_values[i][j])

            for k in range(9):
                if self.puzzle_values[i][k] != 0:
                    self.preemptive_sets[(i, k)] = set()
                else:
                    self.preemptive_sets[(i, k)] = self.preemptive_sets.get((i, k)).difference(row_set)

    def __update_preemptive_by_col(self):
        for i in range(9):
            col_set = set()

            for j in range(9):
                if self.puzzle_values[j][i] != 0:
                    col_set.add(self.puzzle_values[j][i])

            for k in range(9):
                self.preemptive_sets[(k, i)] = self.preemptive_sets.get((k, i)).difference(col_set)




if __name__ == '__main__':
    main_window = tk.Tk()

    SudokuBoard(main_window)
    main_window.mainloop()
