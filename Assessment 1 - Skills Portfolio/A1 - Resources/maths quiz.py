import tkinter as tk
import random

# CONFIG 
TOTAL_QUESTIONS = 10

# THEME 
THEME = {
    "bg": "#0b0b0b",
    "primary": "#ff0033",
    "success": "#00ff99",
    "danger": "#ff4444",
    "text": "#e6e6e6",
    "entry_bg": "#111111",
    "progress_bg": "#1a1a1a",
    "progress_fg": "#ff0033",
}

# GLOBAL STATE 
difficulty = 1
QUESTION_TIME = 15

question_count = 0
score = 0
combo = 0

num1 = num2 = 0
operation = "+"
correct_answer = 0

time_left = QUESTION_TIME
timer_job = None

# ROOT 
root = tk.Tk()
root.title("Math Arena")
root.geometry("680x560")
root.configure(bg=THEME["bg"])

# UTILS 
def font(size):
    return ("Segoe UI", size, "bold")

# FLASH OVERLAY (PERSISTENT) 
overlay = tk.Frame(root)
overlay.place(relwidth=1, relheight=1)
overlay.lower()

flash_label = tk.Label(overlay, font=font(24), fg="black")
flash_label.pack(expand=True)

# CLEAR
def clear():
    global timer_job
    if timer_job:
        root.after_cancel(timer_job)
        timer_job = None

    for w in root.winfo_children():
        if w is not overlay:
            w.destroy()

# PROGRESS BAR 
def progress_bar():
    frame = tk.Frame(root, bg=THEME["bg"])
    frame.pack(fill="x", pady=10)

    canvas = tk.Canvas(frame, height=20, bg=THEME["progress_bg"], bd=0)
    canvas.pack(fill="x", padx=20)

    canvas.update_idletasks()
    width = canvas.winfo_width()
    fill = max(10, int((question_count / TOTAL_QUESTIONS) * width))
    canvas.create_rectangle(0, 0, fill, 20, fill=THEME["progress_fg"], width=0)

# QUESTION LOGIC
def randomInt():
    if difficulty == 1:
        return random.randint(1, 9)
    elif difficulty == 2:
        return random.randint(10, 99)
    else:
        return random.randint(100, 999)

def new_question():
    global num1, num2, operation, correct_answer

    operation = random.choice(["+", "-", "×", "÷"])

    if operation == "÷":
        num2 = random.randint(1, 9)
        correct_answer = random.randint(1, 12)
        num1 = num2 * correct_answer
        return

    num1 = randomInt()
    num2 = randomInt()

    if operation == "+":
        correct_answer = num1 + num2
    elif operation == "-":
        if num2 > num1:
            num1, num2 = num2, num1
        correct_answer = num1 - num2
    else:
        correct_answer = num1 * num2

# TIMER 
def start_timer():
    global time_left, timer_job

    timer_label.config(text=f"{time_left}s")

    if time_left > 0:
        time_left -= 1
        timer_job = root.after(1000, start_timer)
    else:
        submit_answer(timeout=True)

# ANSWER CHECK 
def submit_answer(timeout=False):
    global score, question_count, combo, timer_job

    if timer_job:
        root.after_cancel(timer_job)
        timer_job = None

    correct = False
    if not timeout:
        try:
            correct = int(answer_entry.get()) == correct_answer
        except:
            pass

    if correct:
        combo += 1
        bonus = combo + time_left // 3
        score += bonus
        flash(THEME["success"], f"+{bonus}  COMBO x{combo}")
    else:
        combo = 0
        flash(THEME["danger"], "TIME UP!" if timeout else "WRONG!")

    question_count += 1

    if question_count >= TOTAL_QUESTIONS:
        root.after(800, show_result)
    else:
        root.after(800, show_quiz)

# FLASH EFFECT 
def flash(color, text):
    overlay.config(bg=color)
    flash_label.config(text=text, bg=color)
    overlay.lift()
    root.after(350, overlay.lower)

# QUIZ SCREEN 
def show_quiz():
    global time_left, answer_entry, timer_label

    clear()
    progress_bar()
    new_question()
    time_left = QUESTION_TIME

    tk.Label(
        root,
        text=f"{num1} {operation} {num2} = ?",
        font=font(32),
        bg=THEME["bg"],
        fg=THEME["text"]
    ).pack(pady=30)

    answer_entry = tk.Entry(
        root,
        font=font(20),
        bg=THEME["entry_bg"],
        fg=THEME["text"],
        insertbackground="white",
        justify="center"
    )
    answer_entry.pack(pady=20)
    answer_entry.focus()

    tk.Button(
        root,
        text="SUBMIT",
        font=font(14),
        bg=THEME["primary"],
        fg="white",
        command=submit_answer
    ).pack(pady=10)

    timer_label = tk.Label(
        root,
        font=font(14),
        bg=THEME["bg"],
        fg=THEME["text"]
    )
    timer_label.pack()

    tk.Label(
        root,
        text=f" Combo: {combo}",
        font=font(12),
        bg=THEME["bg"],
        fg=THEME["success"]
    ).pack(pady=5)

    start_timer()

# RESULT SCREEN 
def show_result():
    clear()

    tk.Label(
        root,
        text=" GAME OVER",
        font=font(28),
        bg=THEME["bg"],
        fg=THEME["primary"]
    ).pack(pady=20)

    tk.Label(
        root,
        text=f"Final Score: {score}",
        font=font(22),
        bg=THEME["bg"],
        fg=THEME["text"]
    ).pack(pady=10)

    tk.Button(
        root,
        text="PLAY AGAIN",
        font=font(14),
        bg=THEME["primary"],
        fg="white",
        command=show_difficulty
    ).pack(pady=20)

# DIFFICULTY SELECTION
def set_difficulty(level):
    global difficulty, QUESTION_TIME, score, combo, question_count, time_left

    difficulty = level
    score = combo = question_count = 0
    QUESTION_TIME = 18 if level == 1 else 15 if level == 2 else 10
    time_left = QUESTION_TIME

    show_quiz()

def show_difficulty():
    clear()

    tk.Label(
        root,
        text="SELECT DIFFICULTY",
        font=font(28),
        bg=THEME["bg"],
        fg=THEME["text"]
    ).pack(pady=30)

    tk.Button(root, text="EASY", font=font(16),
              bg=THEME["success"], fg="black",
              command=lambda: set_difficulty(1)).pack(pady=10)

    tk.Button(root, text="MEDIUM", font=font(16),
              bg="#ffaa00", fg="black",
              command=lambda: set_difficulty(2)).pack(pady=10)

    tk.Button(root, text="HARD", font=font(16),
              bg=THEME["danger"], fg="white",
              command=lambda: set_difficulty(3)).pack(pady=10)

# START 
show_difficulty()
root.mainloop()
