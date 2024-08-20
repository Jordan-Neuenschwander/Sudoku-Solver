import tkinter as tk


class SudokuBoard(tk.Frame):
    CELL_SIZE = 30
    BOARD_MARGIN = 10
    NUM_CELLS = 9

    WINDOW_HEIGHT = BOARD_MARGIN * 2 + CELL_SIZE * NUM_CELLS
    WINDOW_WIDTH = BOARD_MARGIN * 2 + CELL_SIZE * NUM_CELLS

    def __init__(self, parent_container):
        tk.Frame.__init__(self, parent_container)
        self.parent = parent_container
        self.selected_cell = (-1, -1)
        self.canvas = tk.Canvas(self, width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT)
        self.puzzle_values = []

        for i in range(self.NUM_CELLS):
            temp_list = []
            self.puzzle_values.append(temp_list)
            for j in range(self.NUM_CELLS):
                self.puzzle_values[i].append(-1)

        self.parent.title("Sudoku Solver")

        # Stretch SudokuWindow tk.Frame to fill entire parent container
        self.pack(fill=tk.BOTH, expand=True)

        # Stretch tk.Canvas to fill entire parent frame
        self.canvas.pack(fill=tk.BOTH, side=tk.TOP)

        self.__draw_board()

        # Event handler for left mouse button click
        self.canvas.bind("<Button-1>", self.__on_left_click)

        # Event handler for key press
        self.canvas.bind("<KeyRelease>", self.__on_key_release)

    def __draw_board(self):
        """
        Draws the vertical and horizontal lines of the grid that represents the sudoku game board
        Every third grid line is drawn darker and thicker to denote the different squares of the sudoku board

        :return: void
        """
        for i in range(self.NUM_CELLS + 1):
            if i % 3 == 0:
                line_color = "black"
                line_width = 2
            else:
                line_color = "gray"
                line_width = 1

            # Draw the vertical gridlines
            x0 = i * self.CELL_SIZE + self.BOARD_MARGIN
            x1 = x0
            y0 = self.BOARD_MARGIN
            y1 = self.WINDOW_HEIGHT - self.BOARD_MARGIN

            self.canvas.create_line(x0, y0, x1, y1, fill=line_color, width=line_width)

            # Draw the horizontal gridlines
            x0 = self.BOARD_MARGIN
            x1 = self.WINDOW_WIDTH - self.BOARD_MARGIN
            y0 = i * self.CELL_SIZE + self.BOARD_MARGIN
            y1 = y0

            self.canvas.create_line(x0, y0, x1, y1, fill=line_color, width=line_width)

    def __draw_values(self, values: []):
        """
        Clears the cell values and repopulates the cells with the values contained within the values list
        :param values: 2D list containing the values of the individual cells on the sudoku board
        :return: null
        """
        self.__clear_values()

        for i in range(len(values)):
            for j in range(self.NUM_CELLS):
                if values[i][j] < 0:
                    continue

                x = self.BOARD_MARGIN + (self.CELL_SIZE * j) + self.CELL_SIZE / 2
                y = self.BOARD_MARGIN + (self.CELL_SIZE * i) + self.CELL_SIZE / 2
                self.canvas.create_text(x, y, text=values[i][j], fill="black", tag="value")

    def __clear_values(self):
        self.canvas.delete("value")

    def __find_cell(self, x: int, y: int):
        """
        Finds the row and column number of the cell that contains the coordinates given
        :param x: the x-coordinate located within a cell
        :param y: the y-coordinate located within a cell
        :return: a tuple containing the row and column number of the cell (row, column)
        """
        cell_row = (x - self.BOARD_MARGIN) // self.CELL_SIZE
        cell_column = (y - self.BOARD_MARGIN) // self.CELL_SIZE

        return cell_row, cell_column

    def __select_cell(self, x: int, y: int):
        self.canvas.delete("selector")
        self.selected_cell = self.__find_cell(x, y)

        x0 = self.BOARD_MARGIN + self.CELL_SIZE * self.selected_cell[0] + 1
        y0 = self.BOARD_MARGIN + self.CELL_SIZE * self.selected_cell[1] + 1

        x1 = self.BOARD_MARGIN + self.CELL_SIZE * (self.selected_cell[0] + 1) - 1
        y1 = self.BOARD_MARGIN + self.CELL_SIZE * (self.selected_cell[1] + 1) - 1
        self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", tag="selector", width=2)

    def __on_key_release(self, event):
        if event.char not in "123456789":
            return

        self.__draw_values(self.puzzle_values)

    def __on_left_click(self, event):
        # Returns if the click was not within the game board
        if not (self.BOARD_MARGIN < event.x < self.WINDOW_WIDTH - self.BOARD_MARGIN
                and self.BOARD_MARGIN < event.y < self.WINDOW_HEIGHT - self.BOARD_MARGIN):
            return

        self.__select_cell(event.x, event.y)
        self.canvas.focus_set()

    def get_selected_cell(self):
        return self.selected_cell

    def get_canvas(self):
        return self.canvas


class SudokuModel:
    def __init__(self):
        self.game_board = []
        for i in range(9):
            temp_list = []
            self.game_board.append(temp_list)
            for j in range(9):
                self.game_board[i].append(-1)

        self.active_puzzle_start = self.game_board.copy()
        self.active_puzzle_solution = self.game_board.copy()

    def __find_cell(self, x: int, y: int):
        """
        Finds the row and column number of the cell that contains the coordinates given
        :param x: the x-coordinate located within a cell
        :param y: the y-coordinate located within a cell
        :return: a tuple containing the row and column number of the cell (row, column)
        """
        cell_row = (x - self.BOARD_MARGIN) // self.CELL_SIZE
        cell_column = (y - self.BOARD_MARGIN) // self.CELL_SIZE

        return cell_row, cell_column

    def __select_cell(self, x: int, y: int):
        self.canvas.delete("selector")
        self.selected_cell = self.__find_cell(x, y)

        x0 = self.BOARD_MARGIN + self.CELL_SIZE * self.selected_cell[0] + 1
        y0 = self.BOARD_MARGIN + self.CELL_SIZE * self.selected_cell[1] + 1

        x1 = self.BOARD_MARGIN + self.CELL_SIZE * (self.selected_cell[0] + 1) - 1
        y1 = self.BOARD_MARGIN + self.CELL_SIZE * (self.selected_cell[1] + 1) - 1
        self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", tag="selector", width=2)

    def __on_key_release(self, event):
        if event.char not in "123456789":
            return

        self.__update_values(self.puzzle_values)

    def __on_left_click(self, event):
        # Returns if the click was not within the game board
        if not (self.BOARD_MARGIN < event.x < self.WINDOW_WIDTH - self.BOARD_MARGIN
                and self.BOARD_MARGIN < event.y < self.WINDOW_HEIGHT - self.BOARD_MARGIN):
            return

        self.__select_cell(event.x, event.y)
        self.canvas.focus_set()


class SudokuController:

    def __init__(self, model: SudokuModel, view: SudokuView):
        self.model = model
        self.view = view

        # Event handler for left mouse button click
        self.canvas.bind("<Button-1>", self.__on_left_click)

        # Event handler for key press
        self.canvas.bind("<KeyRelease>", self.__on_key_release)