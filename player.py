import socket
import threading

HOST = "localhost"
PORT = 9000


def wait_for_move(s):
    """
    Continuously listens for messages from the broker, including opponent moves and status updates.
    If a move message is received, it parses and displays the move. Other messages are printed as
    general updates. It handles disconnections and malformed messages.
    """

    try:
        while True:
            msg = s.recv(1024).decode()

            # Only parse messages that look like moves
            parts = msg.split(",")
            if len(parts) == 3 and parts[2] in ("X", "O"):
                row = int(parts[0])
                col = int(parts[1])
                opp_topic = parts[2]
                print(f"\n\n\t- Opponent {opp_topic} played: Row {row}, Column {col} -")
                print("\n> ", end="")
            else:
                if msg == "Opponent's turn":
                    print(f"\n\t\t- {msg} -\n> ", end="")
                else:
                    print(f"{msg}\n> ", end="")

    except Exception as e:
        print(f"\nError receiving move: {e}")


def start(s, topic):
    """
    Starts the player's game loop. Sends moves to the broker and listens for responses. It launches
    a background thread to receive opponent moves while the player enters theirs. In case it is not
    the player's turn, it waits until the broker allows it to continue.
    """

    print(f"\nYou are player {topic.upper()}, enter your move (row,col)")

    # Thread to listen for opponent moves
    threading.Thread(target=wait_for_move, args=(s,), daemon=True).start()

    try:
        while True:

            # Message construction and forwarding to broker
            move = input("> ").strip()
            move = f"{move},{topic}"
            s.send(move.encode())

    except Exception as e:
        print(f"Error sending move: {e}")


if __name__ == "__main__":

    # TCP socket creation and connection to broker on localhost:9000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    try:
        while True:
            # Attempt to register a player with a topic ('X' or 'O')
            topic = input("\n\tChoose 'X' or 'O': ").strip().upper()

            if topic:  # Only send if the message has content
                s.send(topic.encode())

                msg = s.recv(1024).decode()
                if msg in ["X", "O"]:
                    current_turn = msg
                    start(s, topic)  # Successful registration
                    break
                else:
                    print(msg)  # Unsuccessful registration, retry

    except KeyboardInterrupt:
        print("\nGame ended by the player.")
        s.close()
        print("Connection closed.\n")
