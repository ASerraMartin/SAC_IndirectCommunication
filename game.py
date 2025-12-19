import json


class Game:
    """Class with the data structures and logic to represent a 3x3 Tic Tac Toe game, with two players ('X' and 'O')."""

    def __init__(self):

        # By default, 'X' starts (arbitrarily chosen)
        self.current_turn = "X"

        # 3x3 tic-tac-toe board
        self.board = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""],
        ]

    def check_winner(self):
        """
        Checks all rows, columns, and the two diagonals of the game board for a winning condition. Also
        detects if the board is full and the game ends in a draw. If none is satisfied, returns None.
        """

        # Check every row
        for row in range(3):
            if (
                self.board[row][0] == self.board[row][1] == self.board[row][2]
                and self.board[row][0] != ""
            ):
                return self.board[row][0]

        # Check every column
        for col in range(3):
            if (
                self.board[0][col] == self.board[1][col] == self.board[2][col]
                and self.board[0][col] != ""
            ):
                return self.board[0][col]

        # Check diagonals
        if (
            self.board[0][0] != ""
            and self.board[0][0] == self.board[1][1] == self.board[2][2]
        ):
            return self.board[0][0]
        if (
            self.board[0][2] != ""
            and self.board[0][2] == self.board[1][1] == self.board[2][0]
        ):
            return self.board[0][2]

        # Check for a draw
        if all(cell != "" for row in self.board for cell in row):
            return "Draw"

        return None

    def is_valid(self, topic, row, col):
        """Checks if the move is within bounds, if the cell is empty, and if it is the player's turn."""

        # Check turn
        if self.current_turn != topic:
            return False, f"Not {topic}'s turn. Current turn is {self.current_turn}."

        # Check bounds
        if not (0 <= row < 3 and 0 <= col < 3):
            return False, "Move out of bounds. Use rows and columns between 0 and 2."

        # Check if the cell is empty
        if self.board[row][col] != "":
            return False, "This cell is not empty. Choose a different one."

        return True, ""

    def make_move(self, row, col, topic):
        """Updates the game board with the move and switches the turn."""

        self.board[row][col] = topic
        self.current_turn = "O" if self.current_turn == "X" else "X"

    def get_state(self):
        """Returns the current game state as a dictionary with board and current turn."""

        return {
            "board": self.board,
            "turn": self.current_turn
        }

    def set_state(self, state):
        """Sets the game state from a dictionary containing board and current turn."""

        self.board = state["board"]
        self.current_turn = state["turn"]

    def serialize_state(self):
        """Serializes the current game state to a JSON string."""

        return json.dumps(self.get_state())

    def deserialize_state(self, state_str):
        """Deserializes a JSON string and sets the game state."""
        
        self.set_state(json.loads(state_str))

    def print_board(self):
        """
        Prints the game board in the terminal, with an ASCII friendly format.
        """

        print("\n")
        print(f"Current turn: {self.current_turn}")
        print("-------------")
        for row in self.board:
            print("|", end=" ")
            for col in row:
                print(col if col else " ", end=" | ")
            print("\n-------------")
