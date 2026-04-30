import tkinter as tk
from tkinter import messagebox, colorchooser

from player import Player
from turn_manager import TurnManager
from prompt import Prompt


class GameSession:
    def __init__(self, root):
        self.root = root
        self.root.title("Guess The Drawing Game")
        self.root.geometry("1100x760")
        self.root.resizable(False, False)

        # UI theme
        self.bg = "#FFF7ED"
        self.card = "#FFFFFF"
        self.primary = "#F97316"
        self.primary_dark = "#EA580C"
        self.secondary = "#FFE4E6"
        self.accent = "#D21619"
        self.text = "#3F2E2E"
        self.muted = "#7C6F64"
        self.danger = "#EF4444"
        self.success = "#22C55E"
        self.border = "#FED7AA"

        self.root.configure(bg=self.bg)

        # Game state
        self.players = []
        self.turn_manager = None
        self.target_score = 0
        self.round_number = 1

        self.current_drawer = None
        self.current_prompt = None
        self.guessers = []
        self.current_guesser_index = 0

        # Drawing state
        self.drawing_lines = []
        self.last_x = None
        self.last_y = None
        self.brush_color = "#111827"
        self.brush_size = tk.IntVar(value=5)

        # Timer state
        self.timer_job = None
        self.time_left = 30
        self.timer_label = None
        self.drawing_time_limit = 30
        self.guess_time_limit = 30

        self.show_setup_screen()

    # -----------------------
    # TIMER HELPERS
    # -----------------------

    def cancel_timer(self):
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    def start_timer(self, seconds, timeout_callback):
        self.cancel_timer()
        self.time_left = seconds

        def update_timer():
            if self.timer_label is not None:
                self.timer_label.config(text=f"Time Left: {self.time_left}s")

            if self.time_left <= 0:
                self.cancel_timer()
                timeout_callback()
                return

            self.time_left -= 1
            self.timer_job = self.root.after(1000, update_timer)

        update_timer()

    # -----------------------
    # UI HELPERS
    # -----------------------

    def clear_window(self):
        self.cancel_timer()

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg=self.bg)
        self.timer_label = None

    def make_title(self, parent, title, subtitle=None):
        tk.Label(
            parent,
            text=title,
            font=("Segoe UI", 28, "bold"),
            bg=self.bg,
            fg=self.accent
        ).pack(pady=(18, 4))

        if subtitle:
            tk.Label(
                parent,
                text=subtitle,
                font=("Segoe UI", 12),
                bg=self.bg,
                fg=self.muted
            ).pack(pady=(0, 14))

    def make_card(self, parent):
        frame = tk.Frame(
            parent,
            bg=self.card,
            highlightbackground=self.border,
            highlightthickness=1
        )
        return frame

    def make_button(self, parent, text, command, variant="primary", width=18):
        if variant == "primary":
            bg = self.primary
            fg = "white"
            active_bg = self.primary_dark
        elif variant == "danger":
            bg = self.danger
            fg = "white"
            active_bg = "#DC2626"
        elif variant == "success":
            bg = self.success
            fg = "white"
            active_bg = "#059669"
        else:
            bg = self.secondary
            fg = self.text
            active_bg = "#FBCFE8"

        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 11, "bold"),
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            width=width,
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=8
        )
        return button

    def make_entry(self, parent, show=None):
        return tk.Entry(
            parent,
            font=("Segoe UI", 12),
            bg="#FFF7ED",
            fg=self.text,
            insertbackground=self.text,
            relief=tk.FLAT,
            highlightbackground=self.border,
            highlightcolor=self.primary,
            highlightthickness=1,
            width=28,
            show=show
        )

    def make_label(self, parent, text, size=11, bold=False, color=None, bg=None):
        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            bg=bg if bg else self.card,
            fg=color if color else self.text
        )

    # -----------------------
    # SETUP SCREEN
    # -----------------------

    def show_setup_screen(self):
        self.clear_window()

        self.players = []
        self.turn_manager = None
        self.target_score = 0
        self.round_number = 1
        self.drawing_lines = []

        self.make_title(
            self.root,
            "Guess The Drawing Game",
            "Draw, guess, score points, and rotate turns with your friends."
        )

        card = self.make_card(self.root)
        card.pack(pady=12, padx=80, fill="both", expand=False)

        tk.Label(
            card,
            text="Game Setup",
            font=("Segoe UI", 20, "bold"),
            bg=self.card,
            fg=self.text
        ).pack(pady=(25, 5))

        tk.Label(
            card,
            text="Enter 2 to 4 players. Leave unused player slots blank.",
            font=("Segoe UI", 11),
            bg=self.card,
            fg=self.muted
        ).pack(pady=(0, 20))

        form = tk.Frame(card, bg=self.card)
        form.pack(pady=5)

        self.player_name_entries = []

        for i in range(4):
            self.make_label(form, f"Player {i + 1} Name:", bg=self.card).grid(
                row=i, column=0, padx=12, pady=10, sticky="e"
            )

            entry = self.make_entry(form)
            entry.grid(row=i, column=1, padx=12, pady=10, ipady=7)
            self.player_name_entries.append(entry)

        self.make_label(form, "Target Score:", bg=self.card).grid(
            row=4, column=0, padx=12, pady=14, sticky="e"
        )

        self.target_score_entry = self.make_entry(form)
        self.target_score_entry.grid(row=4, column=1, padx=12, pady=14, ipady=7)

        self.randomize_turns_var = tk.BooleanVar(value=False)

        randomize_checkbox = tk.Checkbutton(
            card,
            text="Randomize turn order",
            variable=self.randomize_turns_var,
            font=("Segoe UI", 11),
            bg=self.card,
            fg=self.text,
            activebackground=self.card,
            selectcolor=self.card,
            cursor="hand2"
        )
        randomize_checkbox.pack(pady=10)

        self.make_button(
            card,
            "Start Game ✨",
            self.start_game_setup,
            variant="primary",
            width=22
        ).pack(pady=(10, 28))

    def start_game_setup(self):
        names = []

        for entry in self.player_name_entries:
            name = entry.get().strip()
            if name:
                names.append(name)

        if len(names) < 2 or len(names) > 4:
            messagebox.showerror("Invalid Players", "Please enter between 2 and 4 player names.")
            return

        if len(set(names)) != len(names):
            messagebox.showerror("Duplicate Names", "Player names must be unique.")
            return

        try:
            target_score = int(self.target_score_entry.get())
            if target_score <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Score", "Target score must be a positive number.")
            return

        self.players = [Player(index, name) for index, name in enumerate(names, start=1)]
        self.target_score = target_score

        self.turn_manager = TurnManager(self.players)
        self.turn_manager.assign_turn_order(self.randomize_turns_var.get())

        self.show_turn_order_screen()

    # -----------------------
    # TURN ORDER SCREEN
    # -----------------------

    def show_turn_order_screen(self):
        self.clear_window()

        self.make_title(
            self.root,
            "Turn Order",
            "This is the order players will rotate as drawer."
        )

        card = self.make_card(self.root)
        card.pack(pady=20, padx=200, fill="both", expand=False)

        for index, name in enumerate(self.turn_manager.get_turn_order_names(), start=1):
            row = tk.Frame(card, bg=self.card)
            row.pack(fill="x", padx=45, pady=8)

            tk.Label(
                row,
                text=f"{index}",
                font=("Segoe UI", 13, "bold"),
                bg=self.primary,
                fg="white",
                width=3,
                pady=5
            ).pack(side="left", padx=(0, 14))

            tk.Label(
                row,
                text=name,
                font=("Segoe UI", 15, "bold"),
                bg=self.card,
                fg=self.text
            ).pack(side="left")

        self.make_button(
            card,
            "Start Round 1 🎨",
            self.show_drawing_screen,
            variant="primary",
            width=22
        ).pack(pady=25)

    # -----------------------
    # PROMPT SCREEN
    # -----------------------

    def show_drawing_screen(self):
        self.clear_window()

        self.drawing_lines = []
        self.last_x = None
        self.last_y = None

        self.current_drawer = self.turn_manager.get_current_drawer()
        self.current_prompt = Prompt()

        self.make_title(
            self.root,
            f"Round {self.round_number}",
            f"Drawer: {self.current_drawer.name} — Enter the secret prompt first."
        )

        prompt_card = self.make_card(self.root)
        prompt_card.pack(pady=30, padx=260, fill="both", expand=False)

        tk.Label(
            prompt_card,
            text="Secret Prompt",
            font=("Segoe UI", 20, "bold"),
            bg=self.card,
            fg=self.text
        ).pack(pady=(25, 5))

        tk.Label(
            prompt_card,
            text="Only the drawer should look at this screen.",
            font=("Segoe UI", 11),
            bg=self.card,
            fg=self.danger
        ).pack(pady=(0, 20))

        form = tk.Frame(prompt_card, bg=self.card)
        form.pack(padx=28, pady=5)

        self.make_label(form, "Hint / Description:", bg=self.card).pack(anchor="w", pady=(0, 5))
        self.description_entry = self.make_entry(form)
        self.description_entry.pack(ipady=7, pady=(0, 14))

        self.make_label(form, "Keyword / Answer:", bg=self.card).pack(anchor="w", pady=(0, 5))

        # Keyword is NOT hidden while drawer types it
        self.keyword_entry = self.make_entry(form)
        self.keyword_entry.pack(ipady=7, pady=(0, 18))

        self.make_button(
            prompt_card,
            "Continue to Drawing 🎨",
            self.submit_prompt_and_start_drawing,
            variant="primary",
            width=24
        ).pack(pady=(8, 25))

    def submit_prompt_and_start_drawing(self):
        description = self.description_entry.get()
        keyword = self.keyword_entry.get()

        try:
            self.current_prompt.set_prompt(description, keyword)
        except ValueError as error:
            messagebox.showerror("Invalid Prompt", str(error))
            return

        self.show_actual_drawing_screen()

    # -----------------------
    # DRAWING SCREEN
    # -----------------------

    def show_actual_drawing_screen(self):
        self.clear_window()

        self.timer_label = tk.Label(
            self.root,
            text="Time Left: 30s",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg,
            fg=self.danger
        )
        self.timer_label.pack(pady=(0, 8))

        main = tk.Frame(self.root, bg=self.bg)
        main.pack(pady=8)

        canvas_card = self.make_card(main)
        canvas_card.grid(row=0, column=0, padx=18, pady=8)

        tk.Label(
            canvas_card,
            text="Drawing Canvas",
            font=("Segoe UI", 14, "bold"),
            bg=self.card,
            fg=self.accent
        ).pack(pady=(15, 8))

        self.canvas = tk.Canvas(
            canvas_card,
            width=640,
            height=430,
            bg="white",
            highlightbackground=self.border,
            highlightthickness=2,
            cursor="pencil"
        )
        self.canvas.pack(padx=20, pady=(0, 12))

        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

        controls = tk.Frame(canvas_card, bg=self.card)
        controls.pack(pady=(0, 18))

        self.make_button(
            controls,
            "Color",
            self.choose_color,
            variant="secondary",
            width=10
        ).grid(row=0, column=0, padx=6)

        tk.Label(
            controls,
            text="Brush:",
            font=("Segoe UI", 10, "bold"),
            bg=self.card,
            fg=self.text
        ).grid(row=0, column=1, padx=(12, 4))

        tk.Scale(
            controls,
            from_=1,
            to=15,
            orient=tk.HORIZONTAL,
            variable=self.brush_size,
            length=130,
            bg=self.card,
            fg=self.text,
            highlightthickness=0
        ).grid(row=0, column=2)

        self.make_button(
            controls,
            "Clear",
            self.clear_drawing,
            variant="danger",
            width=10
        ).grid(row=0, column=3, padx=8)

        self.make_button(
            self.root,
            "Finish Drawing & Start Guessing",
            self.finish_drawing_and_start_guessing,
            variant="primary",
            width=30
        ).pack(pady=12)

        self.start_timer(self.drawing_time_limit, self.drawing_time_expired)

    def finish_drawing_and_start_guessing(self):
        self.cancel_timer()

        self.guessers = [
            player for player in self.players
            if player != self.current_drawer
        ]

        self.current_guesser_index = 0
        self.show_guessing_screen()

    def drawing_time_expired(self):
        self.guessers = [
            player for player in self.players
            if player != self.current_drawer
        ]

        self.current_guesser_index = 0
        self.show_guessing_screen(message="Drawing time is up! Guessing begins now.")

    def start_draw(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def draw(self, event):
        if self.last_x is not None and self.last_y is not None:
            width = self.brush_size.get()

            self.canvas.create_line(
                self.last_x,
                self.last_y,
                event.x,
                event.y,
                fill=self.brush_color,
                width=width,
                capstyle=tk.ROUND,
                smooth=True
            )

            self.drawing_lines.append(
                (self.last_x, self.last_y, event.x, event.y, self.brush_color, width)
            )

            self.last_x = event.x
            self.last_y = event.y

    def stop_draw(self, event):
        self.last_x = None
        self.last_y = None

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Brush Color")
        if color[1] is not None:
            self.brush_color = color[1]

    def clear_drawing(self):
        self.canvas.delete("all")
        self.drawing_lines = []

    # -----------------------
    # GUESSING SCREEN
    # -----------------------

    def show_guessing_screen(self, message=""):
        self.clear_window()

        self.make_title(
            self.root,
            "Guessing Phase",
            "Each guesser gets 30 seconds and one chance."
        )

        if message:
            tk.Label(
                self.root,
                text=message,
                font=("Segoe UI", 11, "bold"),
                bg=self.bg,
                fg=self.danger
            ).pack(pady=(0, 8))

        self.timer_label = tk.Label(
            self.root,
            text="Time Left: 30s",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg,
            fg=self.danger
        )
        self.timer_label.pack(pady=(0, 8))

        main = tk.Frame(self.root, bg=self.bg)
        main.pack(pady=8)

        drawing_card = self.make_card(main)
        drawing_card.grid(row=0, column=0, padx=18)

        tk.Label(
            drawing_card,
            text="Drawing",
            font=("Segoe UI", 16, "bold"),
            bg=self.card,
            fg=self.text
        ).pack(pady=(15, 8))

        drawing_canvas = tk.Canvas(
            drawing_card,
            width=640,
            height=430,
            bg="white",
            highlightbackground=self.border,
            highlightthickness=2
        )
        drawing_canvas.pack(padx=20, pady=(0, 10))

        self.redraw_canvas(drawing_canvas)

        # Shows description/hint when passing to guessers
        tk.Label(
            drawing_card,
            text=f"Hint: {self.current_prompt.description}",
            font=("Segoe UI", 13, "bold"),
            bg=self.card,
            fg=self.accent
        ).pack(pady=(0, 16))

        guess_card = self.make_card(main)
        guess_card.grid(row=0, column=1, padx=18, sticky="n")

        current_guesser = self.guessers[self.current_guesser_index]

        tk.Label(
            guess_card,
            text=f"{current_guesser.name}'s Turn",
            font=("Segoe UI", 18, "bold"),
            bg=self.card,
            fg=self.text
        ).pack(pady=(25, 5))

        tk.Label(
            guess_card,
            text="Enter your guess below.",
            font=("Segoe UI", 11),
            bg=self.card,
            fg=self.muted
        ).pack(pady=(0, 18))

        self.guess_entry = self.make_entry(guess_card)
        self.guess_entry.pack(ipady=8, padx=30, pady=(0, 18))
        self.guess_entry.focus()

        self.make_button(
            guess_card,
            "Submit Guess 💭",
            self.submit_guess,
            variant="primary",
            width=22
        ).pack(pady=(0, 12))

        self.make_button(
            guess_card,
            "View Scoreboard",
            self.show_scoreboard_popup,
            variant="secondary",
            width=20
        ).pack(pady=(0, 25))

        self.start_timer(self.guess_time_limit, self.guess_time_expired)

    def redraw_canvas(self, canvas):
        for x1, y1, x2, y2, color, width in self.drawing_lines:
            canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=color,
                width=width,
                capstyle=tk.ROUND,
                smooth=True
            )

    def submit_guess(self):
        self.cancel_timer()

        current_guesser = self.guessers[self.current_guesser_index]
        guess = self.guess_entry.get().strip()

        if guess == "":
            messagebox.showerror("Invalid Guess", "Guess cannot be blank.")
            self.start_timer(self.guess_time_limit, self.guess_time_expired)
            return

        if self.current_prompt.check_guess(guess):
            current_guesser.add_point()

            messagebox.showinfo(
                "Correct!",
                f"{current_guesser.name} guessed correctly and earned 1 point!"
            )

            self.show_round_results(correct_player=current_guesser)
            return

        self.current_guesser_index += 1

        if self.current_guesser_index >= len(self.guessers):
            self.show_round_results(correct_player=None)
        else:
            self.show_guessing_screen(message="Incorrect guess. Next player may guess.")

    def guess_time_expired(self):
        self.current_guesser_index += 1

        if self.current_guesser_index >= len(self.guessers):
            self.show_round_results(correct_player=None)
        else:
            self.show_guessing_screen(message="Time is up! Next player may guess.")

    # -----------------------
    # RESULTS / WINNER
    # -----------------------

    def show_round_results(self, correct_player):
        self.cancel_timer()
        self.clear_window()

        self.make_title(self.root, "Round Results")

        card = self.make_card(self.root)
        card.pack(padx=180, pady=20, fill="both", expand=False)

        if correct_player is None:
            result_text = "No one guessed correctly."
            result_color = self.danger
        else:
            result_text = f"{correct_player.name} guessed correctly!"
            result_color = self.success

        tk.Label(
            card,
            text=result_text,
            font=("Segoe UI", 20, "bold"),
            bg=self.card,
            fg=result_color
        ).pack(pady=(28, 8))

        tk.Label(
            card,
            text=f"The answer was: {self.current_prompt.reveal_keyword()}",
            font=("Segoe UI", 15, "bold"),
            bg=self.card,
            fg=self.text
        ).pack(pady=(0, 18))

        self.display_scoreboard_on_screen(card)

        winner = self.get_winner()

        if winner:
            self.make_button(
                card,
                "Show Winner 🏆",
                lambda: self.show_winner_screen(winner),
                variant="success",
                width=20
            ).pack(pady=24)
        else:
            self.make_button(
                card,
                "Next Round 🎨",
                self.prepare_next_round,
                variant="primary",
                width=20
            ).pack(pady=24)

    def prepare_next_round(self):
        self.cancel_timer()
        self.turn_manager.move_to_next_drawer()
        self.round_number += 1
        self.show_drawing_screen()

    def get_winner(self):
        for player in self.players:
            if player.score >= self.target_score:
                return player
        return None

    def display_scoreboard_on_screen(self, parent):
        scoreboard = tk.Frame(parent, bg=self.card)
        scoreboard.pack(pady=12)

        tk.Label(
            scoreboard,
            text="Scoreboard",
            font=("Segoe UI", 18, "bold"),
            bg=self.card,
            fg=self.text
        ).pack(pady=(0, 8))

        for player in self.players:
            row = tk.Frame(scoreboard, bg="#FFF7ED", highlightbackground=self.border, highlightthickness=1)
            row.pack(fill="x", padx=20, pady=4)

            tk.Label(
                row,
                text=player.name,
                font=("Segoe UI", 12, "bold"),
                bg="#FFF7ED",
                fg=self.text,
                width=18,
                anchor="w"
            ).pack(side="left", padx=12, pady=8)

            tk.Label(
                row,
                text=f"{player.score} point(s)",
                font=("Segoe UI", 12),
                bg="#FFF7ED",
                fg=self.primary,
                width=12,
                anchor="e"
            ).pack(side="right", padx=12, pady=8)

    def show_scoreboard_popup(self):
        scores = ""

        for player in self.players:
            scores += f"{player.name}: {player.score} point(s)\n"

        messagebox.showinfo("Scoreboard", scores)

    def show_winner_screen(self, winner):
        self.cancel_timer()
        self.clear_window()

        self.make_title(
            self.root,
            "Game Over!",
            "Thanks for playing."
        )

        card = self.make_card(self.root)
        card.pack(padx=180, pady=20, fill="both", expand=False)

        tk.Label(
            card,
            text="🏆",
            font=("Segoe UI", 52),
            bg=self.card,
            fg=self.primary
        ).pack(pady=(25, 0))

        tk.Label(
            card,
            text=f"{winner.name} Wins!",
            font=("Segoe UI", 26, "bold"),
            bg=self.card,
            fg=self.text
        ).pack(pady=(5, 8))

        tk.Label(
            card,
            text=f"Final Score: {winner.score} point(s)",
            font=("Segoe UI", 15),
            bg=self.card,
            fg=self.muted
        ).pack(pady=(0, 16))

        self.display_scoreboard_on_screen(card)

        buttons = tk.Frame(card, bg=self.card)
        buttons.pack(pady=25)

        self.make_button(
            buttons,
            "Play Again ✨",
            self.show_setup_screen,
            variant="primary",
            width=16
        ).grid(row=0, column=0, padx=10)

        self.make_button(
            buttons,
            "Quit",
            self.root.quit,
            variant="danger",
            width=16
        ).grid(row=0, column=1, padx=10)