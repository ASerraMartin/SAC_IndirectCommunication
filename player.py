import socket
import threading

HOST = "localhost"
PORT = 9000


def wait_for_move(socket):
    while True:
        msg = socket.recv(1024).decode()
        print(f"\nOpponent move: {msg}")
        # TODO change format


def start(topic):

    # TCP socket creation and connection to the broker
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.send(topic.encode("utf-8"))

    print(f"You are player {topic}")

    # Additional thread to simultaneously play and hear responses
    threading.Thread(target=wait_for_move, args=(s,)).start()

    while True:
        move = input("Enter your move (row,col): ").strip()
        try:
            # Input cleaning
            # TODO only verify input inside broker (fancier)
            row, col = map(int, move.split(","))
            if 1 <= row <= 3 and 1 <= col <= 3:
                s.send(f"{topic},{row},{col}".encode("utf-8"))
            else:
                print("Row and column must be between 1 and 3.")
        except ValueError:
            print("Invalid format. Please only enter 'row,col' (e.g.: 2,3).")


if __name__ == "__main__":
    while True:
        # Input cleaning and topic (type of player) selection
        topic = input("Choose 'X' or 'O': ").strip().upper()
        if topic in ["X", "O"]:
            start(topic)
            break
        else:
            print("Invalid player, please choose 'X' or 'O'.")
