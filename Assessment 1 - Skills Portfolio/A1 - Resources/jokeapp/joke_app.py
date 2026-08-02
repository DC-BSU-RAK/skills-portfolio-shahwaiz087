"""
Alexa, Tell Me a Joke
---------------------
A Tkinter GUI application that reads jokes from resources/randomJokes.txt
and presents them to the user one at a time: setup first, then punchline
on request.

Each line in randomJokes.txt is expected to contain a setup and a
punchline separated by a question mark, e.g.:

    Why did the chicken cross the road?To get to the other side.

Lines may optionally start with "- " (a leading dash and space), which
this program will strip automatically.
"""

import os
import random
import tkinter as tk
from tkinter import messagebox

# Path to the jokes file, relative to this script so it works regardless
# of the current working directory.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JOKES_FILE = os.path.join(SCRIPT_DIR, "resources", "randomJokes.txt")


def load_jokes(filepath):
    """Read the jokes file and return a list of (setup, punchline) tuples."""
    jokes = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                # Strip a leading "- " bullet if present.
                if line.startswith("- "):
                    line = line[2:].strip()
                if "?" not in line:
                    continue
                setup, punchline = line.split("?", 1)
                setup = setup.strip() + "?"
                punchline = punchline.strip()
                if setup and punchline:
                    jokes.append((setup, punchline))
    except FileNotFoundError:
        messagebox.showerror(
            "File Not Found",
            f"Could not find the jokes file at:\n{filepath}",
        )
    return jokes


class JokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alexa, Tell Me a Joke")
        self.root.geometry("520x340")
        self.root.resizable(False, False)
        self.root.configure(bg="#2b2d42")

        self.jokes = load_jokes(JOKES_FILE)
        self.current_joke = None

        # --- Widgets ---
        title_label = tk.Label(
            root,
            text="🎙️ Alexa Joke Assistant",
            font=("Helvetica", 18, "bold"),
            bg="#2b2d42",
            fg="#edf2f4",
        )
        title_label.pack(pady=(20, 10))

        self.setup_label = tk.Label(
            root,
            text="Press the button below for a joke!",
            font=("Helvetica", 13),
            wraplength=460,
            justify="center",
            bg="#2b2d42",
            fg="#8d99ae",
        )
        self.setup_label.pack(pady=(10, 5), padx=20)

        self.punchline_label = tk.Label(
            root,
            text="",
            font=("Helvetica", 13, "italic"),
            wraplength=460,
            justify="center",
            bg="#2b2d42",
            fg="#ef233c",
        )
        self.punchline_label.pack(pady=(5, 15), padx=20)

        button_frame = tk.Frame(root, bg="#2b2d42")
        button_frame.pack(pady=10)

        self.tell_joke_btn = tk.Button(
            button_frame,
            text="Alexa tell me a Joke",
            font=("Helvetica", 11, "bold"),
            bg="#8d99ae",
            fg="#2b2d42",
            width=22,
            command=self.tell_joke,
        )
        self.tell_joke_btn.grid(row=0, column=0, padx=6, pady=6)

        self.punchline_btn = tk.Button(
            button_frame,
            text="Show Punchline",
            font=("Helvetica", 11, "bold"),
            bg="#8d99ae",
            fg="#2b2d42",
            width=22,
            state=tk.DISABLED,
            command=self.show_punchline,
        )
        self.punchline_btn.grid(row=0, column=1, padx=6, pady=6)

        self.next_joke_btn = tk.Button(
            button_frame,
            text="Next Joke",
            font=("Helvetica", 11, "bold"),
            bg="#8d99ae",
            fg="#2b2d42",
            width=22,
            state=tk.DISABLED,
            command=self.tell_joke,
        )
        self.next_joke_btn.grid(row=1, column=0, padx=6, pady=6)

        self.quit_btn = tk.Button(
            button_frame,
            text="Quit",
            font=("Helvetica", 11, "bold"),
            bg="#ef233c",
            fg="#edf2f4",
            width=22,
            command=self.quit_app,
        )
        self.quit_btn.grid(row=1, column=1, padx=6, pady=6)

    def tell_joke(self):
        if not self.jokes:
            self.setup_label.config(text="No jokes found. Check randomJokes.txt.")
            return

        self.current_joke = random.choice(self.jokes)
        setup, _ = self.current_joke

        self.setup_label.config(text=setup)
        self.punchline_label.config(text="")

        self.punchline_btn.config(state=tk.NORMAL)
        self.next_joke_btn.config(state=tk.NORMAL)

    def show_punchline(self):
        if self.current_joke:
            _, punchline = self.current_joke
            self.punchline_label.config(text=punchline)

    def quit_app(self):
        self.root.destroy()


def main():
    root = tk.Tk()
    app = JokeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
