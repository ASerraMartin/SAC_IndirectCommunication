import zmq
import sys
import time
import threading
from game import Game
from config import X_PORT, O_PORT


class Player:
    def __init__(self, topic):

        self.game = Game()
        self.topic = topic
        self.playing = True
        self.context = zmq.Context()

        # Publishing to the given port
        self.pub = self.context.socket(zmq.PUB)
        self.pub.bind(f"tcp://localhost:{X_PORT if topic == 'X' else O_PORT}")

        # Subscribing to topics on the other port
        self.sub = self.context.socket(zmq.SUB)
        if self.topic == "X":
            self.sub.connect(f"tcp://localhost:{O_PORT}")
            self.sub.subscribe("O")
        else:
            self.sub.connect(f"tcp://localhost:{X_PORT}")
            self.sub.subscribe("X")

        self.sub.subscribe("ok")  # Topic to acknowledge moves
        self.sub.subscribe("error")  # Topic to notify errors
        self.sub.subscribe("end")  # Topic to notify end of game

        print(f"\nYou are player {self.topic}, enter your move (row,col)")

    def process_message(self, topic, payload):
        """
        Processes an incoming message received through the subscriber socket. Depending
        on the topic, it can:

        - (X/O) Update the game board with a correct move.
        - (ok) Validate and acknowledge the opponent's moves.
        - (error) Display an error due to an incorrect move.
        - (end) Handle the end of the game.
        """

        # End of game handling
        if topic == "end":
            self.end_game(payload)
            return

        # Error handling in case of a returned invalid move
        if topic == "error":
            print(f"ERROR: {payload}")
            return

        try:
            # Move processing
            row_str, col_str = payload.split(",")
            row = int(row_str)
            col = int(col_str)

            # Move acknowledgment handling
            if topic == "ok":
                self.game.make_move(row, col, self.topic)
                self.game.print_board()
                return

            # Check turn
            if self.game.current_turn != topic:
                self.pub.send_multipart([b"error", b"It is not your turn"])
                return

            # Check if the move is valid
            ok, reason = self.game.is_valid(topic, row, col)
            if not ok:
                self.pub.send_multipart([b"error", reason.encode()])
                return

        # In case of incorrect format, an exception is thrown
        # and has to be handled instead of using regular logic
        except Exception as e:
            self.pub.send_multipart([b"error", b"The format is not correct, use (row,col)"])
            return

        # Update local state and send acknowledge to update opponent's state
        self.game.make_move(row, col, topic)
        self.pub.send_multipart([b"ok", f"{row},{col}".encode()])

        print(f"\n\n\t- Opponent {topic} played: Row {row}, Column {col} -")
        self.game.print_board()

        # Check if the game has ended
        winner = self.game.check_winner()
        if winner:
            # End own game and notify opponent
            self.pub.send_multipart([b"end", winner.encode()])
            self.end_game(winner)
        else:
            print("> ", end="", flush=True)

    def start(self):
        """
        Starts the player execution and initializes the game main loop. This method
        launches the background threads responsible for sending and receiving messages,
        and keeps the main process alive while the game is active.
        """

        print("You start!" if self.topic == "X" else "Waiting for opponent...")
        self.game.print_board()

        # Threads for publishing and receiving
        pub_thread = threading.Thread(target=self.publish, daemon=True)
        sub_thread = threading.Thread(target=self.receive, daemon=True)

        pub_thread.start()
        sub_thread.start()

        try:
            while self.playing:
                continue

        # Handle ctrl+C or manual interruption to close the game
        except KeyboardInterrupt:
            print("\nGame ended by the player.")
            self.playing = False
            print("Connection closed.\n")

    def publish(self):
        """
        Handles user input and publishes messages to the opponent through the publisher socket. 
        This method continuously reads moves from the standard input, formats them as topic messages, 
        and sends them to be processed by the opponent.
        """

        while self.playing:
            try:
                msg = input("> ").strip()
                self.pub.send_multipart([self.topic.encode(), msg.encode()])
                time.sleep(0.2)  # Small delay to allow correct screen update

            # Handle ctrl+C or manual interruption to close the game
            except (KeyboardInterrupt, EOFError):
                break

            # Handle other exceptions
            except Exception as e:
                print(f"Error publishing message: {e}")
                break

    def receive(self):
        """
        Listens for incoming messages from the subscriber socket. This method continuously receives
        messages from the opponent and processes them to keep the local game state synchronized.
        """

        while self.playing:
            try:
                msg = self.sub.recv_multipart()
                topic, payload = msg
                topic = topic.decode()
                payload = payload.decode()
                self.process_message(topic, payload)

            # Handle other exceptions
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def end_game(self, winner):
        """
        Terminates the game execution in a controlled manner. It stops the running
        loops, closes all the ZeroMQ sockets, and exits the application afterwards.
        """

        if winner == "Draw":
            print("\n\t\t### IT'S A DRAW ###\n")
        else:
            print(f"\n\t\t### THE WINNER IS {winner} ###\n")

        self.playing = False
        self.pub.close()
        self.sub.close()
        self.context.term()
        sys.exit(0)


if __name__ == "__main__":

    player = None
    try:
        while True:
            # Attempt to register a player with a topic ('X' or 'O')
            topic = input("\n\tChoose 'X' or 'O': ").strip().upper()
            if topic in ["X", "O"]:
                try:
                    player = Player(topic)
                    break
                # Handle error if port is in use (the player has already been registered)
                except zmq.ZMQError:
                    print(f"{topic} is already playing, please choose another player.")
            else:
                print("Invalid player, please choose 'X' or 'O'.")

        player.start()

    # Handle ctrl+C or manual interruption to close the game
    except KeyboardInterrupt:
        print("\nGame ended by the player.")
        if player:
            player.playing = False
        print("Connection closed.\n")
