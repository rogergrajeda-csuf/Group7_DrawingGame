import tkinter as tk
from game_session import GameSession


def main():
    root = tk.Tk()
    GameSession(root)
    root.mainloop()


if __name__ == "__main__":
    main()