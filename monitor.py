import zmq
import sys
import interface
import threading
from config import X_PORT, O_PORT

# Stores the last move's topic, waiting to be acknowledged
move_to_ack = None


def start_monitor():
    """
    Starts the monitor process that listens to all published messages
    from both players and updates the GUI accordingly.
    """

    context = zmq.Context()
    listener = context.socket(zmq.SUB)

    # Subscribe to all topics
    listener.connect(f"tcp://localhost:{X_PORT}")
    listener.connect(f"tcp://localhost:{O_PORT}")
    listener.subscribe("")
    print("Monitor started. Waiting for moves...")

    while True:
        try:
            msg = listener.recv_multipart()
            topic, payload = msg
            topic = topic.decode()
            payload = payload.decode()

            # Move handling
            if topic in ["X", "O"]:
                print(f"[{topic}] Move: {payload}")
                move_to_ack = topic

            # Move confirmation handling (draw in GUI)
            elif topic == "ok":
                print(f"[{topic}] Move acknowledged: {payload}")
                row_str, col_str = payload.split(",")
                interface.mark_square(int(row_str), int(col_str), move_to_ack)
                move_to_ack = None

            # Error handling
            elif topic == "error":
                print(f"[{topic}] Error reported: {payload}")

            # Game end handling
            elif topic == "end":
                if payload == "Draw":
                    print(f"[{topic}] GAME OVER | Draw")
                else:
                    print(f"[{topic}] GAME OVER | Winner: {payload}")

        # Handle ZeroMQ errors
        except zmq.ZMQError as e:
            print(f"Publisher-subscriber error: {e}")
            break

        # Handle other exceptions
        except Exception as e:
            print(f"Error in the monitor loop: {e}")
            break


if __name__ == "__main__":

    # Monitor runs the GUI and a background thread for the publisher-subscriber
    threading.Thread(target=start_monitor, daemon=True).start()

    try:
        interface.run()

    # Handle ctrl+C or manual interruption to close the game
    except KeyboardInterrupt:
        print("Monitor closing...")
        interface.window.destroy()
        sys.exit(0)
