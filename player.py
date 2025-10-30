import socket
import threading

HOST = "localhost"
PORT = 9000


def wait_for_move(s):
    """
    Continuously listens for messages from the broker, these being opponent moves and status
    updates. If a move message is received, it parses and displays the move. Other messages are
    printed as updates. It handles regular and win-related disconnections and malformed messages.
    """

    try:
        while True:
            msg = s.recv(1024).decode()

            # Move type messages
            parts = msg.split(",")
            if len(parts) == 3 and parts[2] in ("X", "O"):
                row = int(parts[0])
                col = int(parts[1])
                opp_topic = parts[2]
                # Console format, entirely for visual purposes
                print(f"\n\n\t- Opponent {opp_topic} played: Row {row}, Column {col} -")
                print("\n> ", end="")

            else:
                # Opponent's turn warning
                if msg == "Opponent's turn":
                    print(f"\n\t\t- {msg} -\n> ", end="")

                # Victory message
                elif msg in ("X", "O"):
                    print(f"\n\t\t### THE WINNER IS {msg} ###")
                    s.close()

                # Draw message
                elif msg == "Draw":
                    print("\n\t\t### IT'S A DRAW ###")
                    s.close()

                # Status messages (e.g.: "bad format", "cell not empty")
                else:
                    print(f"{msg}\n> ", end="")

    # Reception exceptions handling, omitting socket closing ones, related to the win and end
    except Exception as e:
        if isinstance(e, OSError):
            pass
        else:
            print(f"\nError receiving move: {e}")


def start(s, topic):
    """
    Starts the game loop for a player, allowing them to continuously input moves and send them to
    the broker to trigger actions in the game. Additionally, it creates a thread to run concurrently
    and listen to the opponent's moves.
    """

    print(f"\nYou are player {topic}, enter your move (row,col)")

    # Thread to listen for opponent moves
    threading.Thread(target=wait_for_move, args=(s,)).start()

    try:  # Continuous message construction and forwarding to broker
        while True:
            move = input("> ").strip()
            move = f"{move},{topic}"
            s.send(move.encode())

    # Possible errors when sending moves (e.g.: broker disconnection)
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
                if msg == "OK":
                    start(s, topic)  # Successful registration
                    break
                else:
                    print(msg)  # Unsuccessful registration, retry

    # Handle ctrl+C or manual interruption to close the game
    except KeyboardInterrupt:
        print("\nGame ended by the player.")
        s.close()
        print("Connection closed.\n")
