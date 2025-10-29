import socket
import threading

HOST = "localhost"
PORT = 9000

# List of players from every type
# TODO test system response with more players and such
clients = {"X": [], "O": []}


# TODO possible identify player by name?
def handle_player(player, addr):

    # Topic check
    # TODO polish verification and delete verification from player
    topic = player.recv(1024).decode("utf-8")
    clients[topic].append(player)
    print(f"Player {addr} subscribed to topic '{topic}'")

    # Message handling
    while True:
        try:
            msg = player.recv(1024)
            if not msg:
                break

            # TODO possibly change subscription format so topics are shared
            # but treated differently by one player and the other, now it is
            # a broadcast to the opposite topic
            target_topic = "O" if topic == "X" else "X"
            for client in clients.get(target_topic, []):
                client.send(msg)
        except Exception as e:
            print(f"Error handling player {addr}: {e}")
            break

    # Connection termination
    player.close()
    clients[topic].remove(player)
    print(f"Player {addr} disconnected")


def start():

    # TCP socket creation and binding to localhost:9000 to wait for players
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Waiting for players on {HOST}:{PORT}")

    # Reception of new players
    while True:
        player, addr = s.accept()

        # New thread to serve every player connected
        threading.Thread(target=handle_player, args=(player, addr)).start()


if __name__ == "__main__":
    start()
