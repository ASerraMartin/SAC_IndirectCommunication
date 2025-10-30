import socket
import threading

HOST = "localhost"
PORT = 9000

# By default, 'X' starts
current_turn = "X"

# Possible topics and their players
topics = {"X": None, "O": None}

# 3x3 tic-tac-toe board
board = [["", "", ""], ["", "", ""], ["", "", ""]]


def print_board():
    """
    Prints the board in the terminal, with an ASCII format.
    """

    print("-------------")
    for row in board:
        print("|", end=" ")
        for col in row:
            print(col if col else " ", end=" | ")
        print("\n-------------")


def release_topic(target):
    """
    Releases the topic associated with a disconnected player (target). Iterates through the topics
    dictionary until it finds a match and sets its value to None to release it.
    """

    for topic, player in topics.items():
        if target == player:
            topics[topic] = None
            print(f"Player {topic} disconnected.")
            return


def is_valid(row, col):
    """
    Checks if the move is within the board's bounds and the cell is empty.
    """

    if not (0 <= row < 3 and 0 <= col < 3):
        return False, "Move out of bounds. Use rows and columns between 0 and 2."

    if board[row][col] != "":
        return False, "This cell is not empty. Choose a different one."

    return True, ""


def handle_messages(player):
    """
    Handles incoming messages from a connected player during the game. Receives the move data with
    format 'row,col,topic' and verifies if it is the player's turn. If the move is valid, it sends
    it to the opponent and updates the turn. Out-of-turn moves are ignored.
    """

    global current_turn

    try:
        while True:  # Continuously listening to player messages
            msg = player.recv(1024).decode()
            print(f"Received: '{msg}'")

            # Extract move details from the message
            try:
                row_str, col_str, topic = msg.split(",")
                row = int(row_str)
                col = int(col_str)

                # Check turn
                if topic != current_turn and topic in ["X", "O"]:
                    print(f"Ignored move out of turn from player {topic}.")
                    player.send("It is not your turn".encode())
                    continue

                # Check if the move is valid
                ok, reason = is_valid(row, col)

                if not ok:
                    print(f"Invalid move: {reason}")
                    player.send(f"Invalid move: {reason}".encode())
                    continue

            # In case of incorrect format, an exception is thrown
            # and has to be handled instead of using regular logic
            except Exception:
                print(f"Invalid move: Incorrect format")
                player.send("Invalid move, the format is not correct".encode())
                continue

            # Move registration
            print("Valid move")
            board[row][col] = topic
            print_board()

            # Select the correct topic to send the message
            opponent_topic = "O" if topic == "X" else "X"
            opponent = topics.get(opponent_topic)
            opponent.send(f"{row},{col},{topic}".encode())

            # Update turn
            current_turn = opponent_topic
            player.send("Waiting for the opponent...".encode())

    # Possible errors while handling messages (e.g.: disconnection)
    except Exception as e:
        print(f"Error handling message from player {topic}: {e}")
    finally:
        release_topic(player)
        player.close()


def register_player(player):
    """
    Receives a player's chosen topic ('X' or 'O') through its socket connection (player) and assigns
    said topic if valid and available, otherwise an error text is sent and the process is repeated.
    """

    try:
        while True:  # Verification of valid topic
            topic = player.recv(1024).decode()

            if topic not in topics:  # Only 'X' and 'O' are valid topics
                player.send("Invalid player, please choose 'X' or 'O'.".encode())
                continue

            elif topics[topic] is not None:  # Only one player per topic
                player.send(f"Player {topic} already chosen.".encode())
                continue

            # Subscribe the player to the topic if the verification was correct
            player.send(current_turn.encode())
            topics[topic] = player
            print(f"Player {topic} connected")
            break

    # Possible errors while registering a player (e.g.: disconnection)
    except Exception as e:
        print(f"Error registering player {topic}: {e}")
        release_topic(player)
        player.close()


if __name__ == "__main__":

    # TCP socket creation and binding to localhost:9000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    print(f"Waiting for players on {HOST}:{PORT}")
    try:
        while True:
            # Player connection and registration with their chosen topic
            player, _ = s.accept()
            register_player(player)

            # Separate thread to handle messages from the players
            threading.Thread(target=handle_messages, args=(player,)).start()

    except KeyboardInterrupt:
        print("\nGame ended by the broker.")
        for player in topics.values():
            if player:
                player.close()
        s.close()
        print("Connection closed.\n")
