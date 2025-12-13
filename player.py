import zmq
import sys
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
            if len(parts) == 2:
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
            print(f"It's your turn, {self.topic}!")

    def start(self):

        print("You start!" if self.topic == "X" else "Waiting for opponent...")

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

        while self.playing:
            try:
                msg = input("> ").strip()
                self.pub.send_multipart([self.topic.encode(), msg.encode()])

            # Handle ctrl+C or manual interruption to close the game
            except (KeyboardInterrupt, EOFError):
                break

            # Handle other exceptions
            except Exception as e:
                print(f"Error publishing message: {e}")
                break

    def receive(self):

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

        if winner == "Draw":
            print("\n\t\t### IT'S A DRAW ###")
        else:
            print(f"\n\t\t### THE WINNER IS {winner} ###")

        self.playing = False
        self.pub.close()
        self.sub.close()
        self.context.term()

        print("\nGame ended.")
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
