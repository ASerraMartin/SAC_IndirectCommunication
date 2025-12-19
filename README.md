# SAC_IndirectCommunication

*A publisher-subscriber distributed system to play Tic-Tac-Toe between two players, implemented with ZeroMQ sockets.*

Assignment for **Sistemes Actuals de Computació**.

---

## INTRODUCTION

This repository contains the implementation of a distributed indirect communication system based on the publish-subscribe (or *pub-sub*) model, designed to allow the intercommunication between two players, without a centralized broker in this case.

The project simulates a simple Tic-Tac-Toe (*tres en raya*) game, where all communication between players is handled through the _ZeroMQ_ library sockets using the pub-sub pattern, rather than direct peer-to-peer exchanges, APIs, or other previously studied systems.

This practice follows as a continuation of the previous practices: `SAC_Sockets` (direct socket communication) and `SAC_RESTFUL` (HTTP-based consensus), this time focusing on **indirect communication mechanisms** within distributed systems.

> To run the code, the ZeroMQ library is required: ```pip install zeromq```

---

## SYSTEM STRUCTURE

The system consists of two main components:

1. **Players (X and O):**  
   Each player acts simultaneously as a publisher and subscriber. Player X binds to port `9001` and subscribes to port `9002`, while Player O does the opposite. This cross-subscription pattern ensures that each player receives the opponent's messages without requiring a central broker.

2. **Monitor (Optional):**  
   A passive observer that subscribes to both players' topics and displays the game state in a graphical interface built with `tkinter`. The monitor does not participate in the game logic, it only visualizes moves in real time.

Each player runs in its own process (`player.py`) and communicates with the opponent through ZeroMQ pub-sub sockets. There is **no centralized broker**, instead players connect to each other's publishing endpoints, but communicate indirectly in the sense that they simply send messages, that are (indirectly) received by anyone listening (i.e. subscribed to their topic), with the players not necesarilly being targeted directly by the sender to receive their messages.

Additionally, a GUI developed via `tkinter` (preinstalled with Python) provides real-time visualization of the game state when running the monitor, if desired.

---

### COMMUNICATION FLOW

1. Each player binds a PUB socket to their assigned port and connects a SUB socket to the opponent's port.
2. Players subscribe to relevant topics: opponent's symbol (`X` or `O`), `ok` (move acknowledgment), `error`, `end`, `state_request`, and `state_response`.
3. When a player starts, it automatically requests the current game state from the opponent using `state_request`. If the opponent is already playing, it responds with `state_response` containing the current board state and turn. If no response is received within 0.5 seconds, the player displays an empty board by default and continues.
4. When a player makes a move, they publish it to their own topic.
5. The opponent receives the move, validates it, updates their local game state, and sends an `ok` acknowledgment.
6. If the move is invalid, an `error` message is sent back instead.
7. The process continues until a player wins or the board is full, at which point an `end` message is published.

**State Synchronization:**

The system includes a state synchronization mechanism that allows players to recover the current game state when connecting. This is particularly useful if a player disconnects and reconnects, since it allows to rejoin and restore the game state. The synchronization uses these two topics:
- `state_request`: Sent by a player to request the current game state
- `state_response`: Contains the serialized game state (board and current turn) in JSON format

This ensures that both players maintain a consistent view of the game board, enabling proper turn management and game state verification, even in the case of a rejoin.

---

## DEPLOYMENT

### With GUI Monitor

Run the `run_gui.bat` file to start the monitor with the graphical interface and two players:

```bash
@echo off
start cmd /k python monitor.py
timeout /t 1 >nul
start cmd /k python player.py
start cmd /k python player.py
```

### Players Only (No GUI)

Run the `run.bat` file that executes:

```bash
@echo off
start cmd /k python player.py
start cmd /k python player.py
```

### Manually

Open two terminals and execute
```bash
python player.py
```

Each player will be prompted to choose their symbol (`X` or `O`). Player X always starts first.

---

## DESIGN DECISIONS AND SCALABILITY/ERROR TOLERANCE CONSIDERATIONS

The architectural choices made in this project reflect a balance between simplicity, reliability, and the educational goals of demonstrating indirect communication patterns. Several key decisions shape the system's behavior and limitations:

**Architectural Design:**

By using ZeroMQ pub-sub pattern, the implementation provides a brokerless approach, where players connect to each other without an intermediary, eliminating the single point of failure inherent in broker-based designs. However, this still means that if one player disconnects, the entire game session is compromised. A trade-off that reflects the game's inherently coupled nature.

The topic-based message categorization (`X`, `O`, `ok`, `error`, `end`, `state_request`, `state_response`) provides structured communication and enables proper message routing. This design allows a clear separation of actions: game moves, acknowledgments, error handling, state synchronization, and termination signals are all handled through distinct channels, making the system more maintainable and easier to debug.

**Scalability Considerations:**

The system has been intentionally designed with simplicity over scalability in mind. Being a Tic-Tac-Toe game, the architecture is fixed to exactly two players, each publishing and subscribing to complementary topics. Scaling beyond two players would require significant architectural changes, including dynamic topic management, player registration mechanisms, and more complex game state synchronization.

**Error Tolerance:**

Input validation is implemented at multiple levels: format checking, boundary validation, turn order enforcement, and cell availability verification. All invalid inputs result in appropriate error messages being sent back to the player, ensuring robust error handling. 

The system includes state synchronization capabilities that allow players to recover the game state when connecting. When a player starts, it automatically requests the current state from the opponent. If the opponent is already playing, it responds with the complete board state, allowing the new player to continue the game from where it was left. This provides a basic form of fault tolerance for player reconnection scenarios.

However, this kind of architecture and implementation still lacks mechanisms for handling network failures, message loss, or complete player disconnections during an active game session.

**User Experience:**

A complementary graphical interface (`interface.py`) with a passive monitor (`monitor.py`) provides real-time visualization of the game state, enhancing the user experience without interfering with the core communication logic. The monitor operates as a pure observer, demonstrating how pub-sub systems can support multiple subscribers without affecting the primary communication flow.

---

## CONCLUSIONS

The resulting system successfully demonstrates the pub-sub communication pattern in a practical context. The brokerless ZeroMQ architecture allows messaging between players while maintaining the decoupled and indirect nature that characterizes publish-subscribe systems. This approach showcases how distributed systems can achieve communication without direct coupling between components.

The implementation provides several notable advantages. The absence of a central broker eliminates a single point of failure, improving the system's resilience compared to traditional broker-based architectures. The clean separation between game logic (handled in `game.py`) and communication mechanisms (managed through ZeroMQ sockets) enhances maintainability and allows each component to evolve independently. 

The state synchronization mechanism ensures that players can recover the game state when connecting, providing a basic form of fault tolerance. When a player starts, it automatically requests the current state from the opponent, and if available, synchronizes its local game state accordingly. This allows players to maintain a consistent view of the game board throughout the session. Furthermore, the system achieves real-time synchronization between players during gameplay, ensuring both maintain consistent game state through the pub-sub messaging pattern.

However, the system also faces inherent limitations that come from the nature of the application. The architecture is fixed to exactly two players due to the game's fundamental structure, making horizontal scaling impossible without a complex escalation and redesign. The system requires both players to be running simultaneously for communication to function, creating a tight coupling that limits fault tolerance.

Despite these limitations, the project effectively achieves its goal of demonstrating indirect communication patterns. However, the given example based on a simple Tic-Tac-Toe game, did not offer much room for complexity, as the 
interaction between players was highly structured and followed a linear sequence. This constrained the communication flow, limiting the opportunity to showcase more dynamic or asynchronous messaging scenarios typical of distributed systems, 
as it could have been done with a system similar to the lottery one from the first practice. 

All in all, the project serves as a solid foundation for understanding the principles and trade-offs involved in indirect communication mechanisms, demonstrating both the strengths and limitations of pub-sub architectures in a concrete, accessible context.

---

## AUTHOR

**Adrià Serra Martín**
