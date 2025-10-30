import tkinter as tk

# Window size and proportion
SIZE = 800
MARGIN = 25
SQUARE_SIZE = (SIZE - 2 * MARGIN) // 3

# Colors
BG = "#1D1D1D"
LINE_FG = "#296BBD"
LINE_BG = "#2B2B2B"

# Window initialization
# centered and on top of all other windows
window = tk.Tk()
window.resizable(False, False)
window.title("TIC-TAC-TOE")
window.attributes("-topmost", True)
x_center = window.winfo_screenwidth() // 2 - SIZE // 2
y_center = window.winfo_screenheight() // 2 - SIZE // 2
window.geometry(f"{SIZE}x{SIZE}+{x_center}+{y_center}")

# Canvas and drawing of the game grid
canvas = tk.Canvas(window, width=SIZE, height=SIZE, bg=BG)
for i in range(1, 3):
    x = MARGIN + i * SQUARE_SIZE
    y = MARGIN + i * SQUARE_SIZE
    # Columns
    canvas.create_line(x, MARGIN, x, SIZE - MARGIN, fill=LINE_BG, width=15)
    canvas.create_line(x, MARGIN, x, SIZE - MARGIN, fill=LINE_FG, width=5)
    # Rows
    canvas.create_line(MARGIN, y, SIZE - MARGIN, y, fill=LINE_BG, width=15)
    canvas.create_line(MARGIN, y, SIZE - MARGIN, y, fill=LINE_FG, width=5)

# Add indicators
for row in range(3):
    for col in range(3):
        x = MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2
        y = MARGIN + row * SQUARE_SIZE + SQUARE_SIZE // 2
        canvas.create_text(
            x, y, text=f"{row},{col}", fill=LINE_BG, font=("Consolas", 50, "bold")
        )

canvas.pack()

# Images for the X and O symbols
x_img = tk.PhotoImage(file="graphics/x.png")
o_img = tk.PhotoImage(file="graphics/o.png")


def mark_square(row, col, symbol):
    x = MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2
    y = MARGIN + row * SQUARE_SIZE + SQUARE_SIZE // 2
    img = x_img if symbol == "X" else o_img
    canvas.create_image(x, y, anchor="center", image=img)


def run():
    window.mainloop()
