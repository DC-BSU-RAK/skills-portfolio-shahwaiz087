"""
Student Manager
----------------
A Tkinter GUI application for managing student coursework/exam records
stored in a comma-separated text file (studentMarks.txt).

File format:
    Line 1          : integer -> number of students
    Line 2 onwards  : StudentCode,Student Name,CW1,CW2,CW3,ExamMark

"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "resources", "studentMarks.txt")

MAX_COURSEWORK = 20      # each of the 3 coursework items is out of 20
MAX_EXAM = 100            # exam is out of 100
MAX_TOTAL = MAX_COURSEWORK * 3 + MAX_EXAM   # 160


# ----------------------------------------------------------------------
#  Data model
# ----------------------------------------------------------------------
class Student:
    """Represents a single student record."""

    def __init__(self, code, name, cw1, cw2, cw3, exam):
        self.code = int(code)
        self.name = name.strip()
        self.coursework = [int(cw1), int(cw2), int(cw3)]
        self.exam = int(exam)

    # -- derived values -------------------------------------------------
    @property
    def coursework_total(self):
        return sum(self.coursework)

    @property
    def total(self):
        return self.coursework_total + self.exam

    @property
    def percentage(self):
        return (self.total / MAX_TOTAL) * 100

    @property
    def grade(self):
        p = self.percentage
        if p >= 70:
            return "A"
        elif p >= 60:
            return "B"
        elif p >= 50:
            return "C"
        elif p >= 40:
            return "D"
        else:
            return "F"

    # -- serialisation ----------------------------------------------------
    def to_line(self):
        return (f"{self.code},{self.name},"
                f"{self.coursework[0]},{self.coursework[1]},{self.coursework[2]},"
                f"{self.exam}")

    def formatted(self):
        """Return a nicely formatted multi-line summary of this student."""
        return (
            f"Student Name        : {self.name}\n"
            f"Student Number      : {self.code}\n"
            f"Coursework Total    : {self.coursework_total} / {MAX_COURSEWORK * 3}\n"
            f"Exam Mark           : {self.exam} / {MAX_EXAM}\n"
            f"Overall Percentage  : {self.percentage:.2f}%\n"
            f"Grade               : {self.grade}\n"
            + "-" * 50 + "\n"
        )


# ----------------------------------------------------------------------
#  Data manager (handles loading/saving/editing the text file)
# ----------------------------------------------------------------------
class StudentManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.students = []
        self.load()

    def load(self):
        self.students = []
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, "r") as f:
            lines = [line.strip() for line in f if line.strip() != ""]
        if not lines:
            return
        try:
            count = int(lines[0])
        except ValueError:
            count = len(lines) - 1
        for line in lines[1:1 + count]:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 6:
                continue
            code, name, cw1, cw2, cw3, exam = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
            self.students.append(Student(code, name, cw1, cw2, cw3, exam))

    def save(self):
        with open(self.filepath, "w") as f:
            f.write(f"{len(self.students)}\n")
            for s in self.students:
                f.write(s.to_line() + "\n")

    # -- queries ----------------------------------------------------------
    def find(self, name=None, code=None):
        """Return list of students matching a (partial, case-insensitive)
        name and/or an exact student code."""
        results = []
        for s in self.students:
            code_match = (code is None) or (str(s.code) == str(code).strip())
            name_match = (not name) or (name.strip().lower() in s.name.lower())
            if code is not None and name:
                if code_match and name_match:
                    results.append(s)
            elif code is not None:
                if code_match:
                    results.append(s)
            elif name:
                if name_match:
                    results.append(s)
        return results

    def highest(self):
        return max(self.students, key=lambda s: s.total) if self.students else None

    def lowest(self):
        return min(self.students, key=lambda s: s.total) if self.students else None

    def average_percentage(self):
        if not self.students:
            return 0.0
        return sum(s.percentage for s in self.students) / len(self.students)

    def next_free_code_hint(self):
        return "e.g. any unused number between 1000 and 9999"

    def code_exists(self, code):
        return any(s.code == int(code) for s in self.students)

    def add_student(self, student):
        self.students.append(student)
        self.save()

    def delete_student(self, student):
        self.students.remove(student)
        self.save()

    def sort(self, key="percentage", descending=False):
        keys = {
            "percentage": lambda s: s.percentage,
            "name": lambda s: s.name.lower(),
            "code": lambda s: s.code,
        }
        self.students.sort(key=keys.get(key, keys["percentage"]), reverse=descending)


# ----------------------------------------------------------------------
#  Small reusable dialog: pick a student from a list (by name/code search)
# ----------------------------------------------------------------------
class StudentPicker(tk.Toplevel):
    """Modal dialog that lets the user search for and pick one student."""

    def __init__(self, master, manager: StudentManager, title="Select a Student"):
        super().__init__(master)
        self.title(title)
        self.manager = manager
        self.result = None
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        frm = ttk.Frame(self, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Search by name and/or student code:").grid(
            row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(frm, text="Name contains:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.name_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.name_var, width=25).grid(
            row=1, column=1, pady=(6, 0))

        ttk.Label(frm, text="Student code:").grid(row=2, column=0, sticky="w")
        self.code_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.code_var, width=25).grid(row=2, column=1)

        ttk.Button(frm, text="Search", command=self.do_search).grid(
            row=3, column=0, columnspan=2, pady=6)

        self.listbox = tk.Listbox(frm, width=45, height=10)
        self.listbox.grid(row=4, column=0, columnspan=2, pady=(0, 6))
        self.listbox.bind("<Double-Button-1>", lambda e: self.confirm())

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=5, column=0, columnspan=2)
        ttk.Button(btn_frame, text="Select", command=self.confirm).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=4)

        self._matches = []
        self.do_search()
        self.wait_window(self)

    def do_search(self):
        name = self.name_var.get().strip() or None
        code = self.code_var.get().strip() or None
        self._matches = self.manager.find(name=name, code=code)
        self.listbox.delete(0, tk.END)
        for s in self._matches:
            self.listbox.insert(tk.END, f"{s.code} - {s.name}")

    def confirm(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("No selection", "Please select a student from the list.", parent=self)
            return
        self.result = self._matches[sel[0]]
        self.destroy()


# ----------------------------------------------------------------------
#  Dialog for adding / editing a student's data
# ----------------------------------------------------------------------
class StudentForm(tk.Toplevel):
    """Modal form used both for adding a new student and editing one field
    at a time is avoided here in favour of a full-record edit form, which is
    simpler and less error-prone for the user."""

    def __init__(self, master, manager: StudentManager, student: Student = None):
        super().__init__(master)
        self.manager = manager
        self.editing = student is not None
        self.original_code = student.code if student else None
        self.title("Edit Student" if self.editing else "Add Student")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        frm = ttk.Frame(self, padding=10)
        frm.grid(row=0, column=0)

        labels = ["Student Code (1000-9999):", "Student Name:",
                  "Coursework 1 (0-20):", "Coursework 2 (0-20):",
                  "Coursework 3 (0-20):", "Exam Mark (0-100):"]
        self.vars = [tk.StringVar() for _ in labels]

        if student:
            self.vars[0].set(str(student.code))
            self.vars[1].set(student.name)
            self.vars[2].set(str(student.coursework[0]))
            self.vars[3].set(str(student.coursework[1]))
            self.vars[4].set(str(student.coursework[2]))
            self.vars[5].set(str(student.exam))

        for i, label in enumerate(labels):
            ttk.Label(frm, text=label).grid(row=i, column=0, sticky="w", pady=3)
            entry = ttk.Entry(frm, textvariable=self.vars[i], width=25)
            entry.grid(row=i, column=1, pady=3)
            if self.editing and i == 0:
                entry.configure(state="disabled")  # don't allow changing the code as primary key

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btn_frame, text="Save", command=self.save).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=4)

        self.wait_window(self)

    def _validate(self):
        try:
            code = int(self.vars[0].get())
            name = self.vars[1].get().strip()
            cw = [int(self.vars[2].get()), int(self.vars[3].get()), int(self.vars[4].get())]
            exam = int(self.vars[5].get())
        except ValueError:
            messagebox.showerror("Invalid input", "All marks and the code must be whole numbers.", parent=self)
            return None

        if not (1000 <= code <= 9999):
            messagebox.showerror("Invalid input", "Student code must be between 1000 and 9999.", parent=self)
            return None
        if not name:
            messagebox.showerror("Invalid input", "Student name cannot be empty.", parent=self)
            return None
        if any(not (0 <= m <= MAX_COURSEWORK) for m in cw):
            messagebox.showerror("Invalid input", f"Each coursework mark must be between 0 and {MAX_COURSEWORK}.", parent=self)
            return None
        if not (0 <= exam <= MAX_EXAM):
            messagebox.showerror("Invalid input", f"Exam mark must be between 0 and {MAX_EXAM}.", parent=self)
            return None
        if not self.editing and self.manager.code_exists(code):
            messagebox.showerror("Duplicate code", "A student with this code already exists.", parent=self)
            return None

        return Student(code, name, cw[0], cw[1], cw[2], exam)

    def save(self):
        new_student = self._validate()
        if new_student is None:
            return
        if self.editing:
            # replace in place, preserving original code
            for i, s in enumerate(self.manager.students):
                if s.code == self.original_code:
                    new_student.code = self.original_code
                    self.manager.students[i] = new_student
                    break
            self.manager.save()
            messagebox.showinfo("Saved", "Student record updated.", parent=self)
        else:
            self.manager.add_student(new_student)
            messagebox.showinfo("Saved", "Student added.", parent=self)
        self.destroy()


# ----------------------------------------------------------------------
#  Main application window
# ----------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Manager")
        self.geometry("900x600")
        self.minsize(760, 480)

        self.manager = StudentManager(DATA_FILE)

        self._build_layout()

    # ------------------------------------------------------------------
    def _build_layout(self):
        container = ttk.Frame(self, padding=10)
        container.pack(fill="both", expand=True)

        # ---- left hand menu -------------------------------------------------
        menu_frame = ttk.LabelFrame(container, text="Menu", padding=10)
        menu_frame.pack(side="left", fill="y", padx=(0, 10))

        buttons = [
            ("1. View all student records", self.view_all),
            ("2. View individual student record", self.view_individual),
            ("3. Show highest total score", self.show_highest),
            ("4. Show lowest total score", self.show_lowest),
            ("5. Sort student records", self.sort_records),
            ("6. Add a student record", self.add_record),
            ("7. Delete a student record", self.delete_record),
            ("8. Update a student's record", self.update_record),
        ]
        for text, cmd in buttons:
            b = ttk.Button(menu_frame, text=text, command=cmd, width=30)
            b.pack(fill="x", pady=3)

        ttk.Separator(menu_frame).pack(fill="x", pady=8)
        ttk.Button(menu_frame, text="Reload from file", command=self.reload_data).pack(fill="x", pady=3)
        ttk.Button(menu_frame, text="Quit", command=self.destroy).pack(fill="x", pady=3)

        # ---- right hand output area -------------------------------------------------
        out_frame = ttk.LabelFrame(container, text="Output", padding=10)
        out_frame.pack(side="right", fill="both", expand=True)

        self.output = ScrolledText(out_frame, wrap="word", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True)
        self.output.configure(state="disabled")

        self.status = tk.StringVar(value=f"Loaded {len(self.manager.students)} students from {DATA_FILE}")
        ttk.Label(self, textvariable=self.status, anchor="w", relief="sunken").pack(fill="x", side="bottom")

    # ------------------------------------------------------------------
    def _write(self, text, clear=True):
        self.output.configure(state="normal")
        if clear:
            self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)
        self.output.configure(state="disabled")

    def _set_status(self, text):
        self.status.set(text)

    # ------------------------------------------------------------------
    #  Menu item 1
    # ------------------------------------------------------------------
    def view_all(self):
        if not self.manager.students:
            self._write("No student records found.\n")
            return
        text = ""
        for s in self.manager.students:
            text += s.formatted() + "\n"
        text += (f"Number of students : {len(self.manager.students)}\n"
                 f"Average percentage : {self.manager.average_percentage():.2f}%\n")
        self._write(text)
        self._set_status("Displayed all student records.")

    # ------------------------------------------------------------------
    #  Menu item 2
    # ------------------------------------------------------------------
    def view_individual(self):
        if not self.manager.students:
            messagebox.showinfo("No data", "There are no student records loaded.")
            return
        picker = StudentPicker(self, self.manager, title="View Individual Student")
        if picker.result:
            self._write(picker.result.formatted())
            self._set_status(f"Displayed record for {picker.result.name}.")

    # ------------------------------------------------------------------
    #  Menu item 3
    # ------------------------------------------------------------------
    def show_highest(self):
        s = self.manager.highest()
        if s is None:
            self._write("No student records found.\n")
            return
        self._write("Student with the HIGHEST total score:\n\n" + s.formatted())
        self._set_status("Displayed highest scoring student.")

    # ------------------------------------------------------------------
    #  Menu item 4
    # ------------------------------------------------------------------
    def show_lowest(self):
        s = self.manager.lowest()
        if s is None:
            self._write("No student records found.\n")
            return
        self._write("Student with the LOWEST total score:\n\n" + s.formatted())
        self._set_status("Displayed lowest scoring student.")

    # ------------------------------------------------------------------
    #  Menu item 5 - Sort
    # ------------------------------------------------------------------
    def sort_records(self):
        if not self.manager.students:
            messagebox.showinfo("No data", "There are no student records loaded.")
            return

        win = tk.Toplevel(self)
        win.title("Sort Student Records")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        frm = ttk.Frame(win, padding=10)
        frm.grid(row=0, column=0)

        ttk.Label(frm, text="Sort by:").grid(row=0, column=0, sticky="w")
        key_var = tk.StringVar(value="percentage")
        for i, (label, val) in enumerate([("Overall percentage", "percentage"),
                                           ("Student name", "name"),
                                           ("Student code", "code")]):
            ttk.Radiobutton(frm, text=label, variable=key_var, value=val).grid(
                row=1 + i, column=0, sticky="w")

        ttk.Label(frm, text="Order:").grid(row=0, column=1, sticky="w", padx=(20, 0))
        order_var = tk.StringVar(value="asc")
        ttk.Radiobutton(frm, text="Ascending", variable=order_var, value="asc").grid(
            row=1, column=1, sticky="w", padx=(20, 0))
        ttk.Radiobutton(frm, text="Descending", variable=order_var, value="desc").grid(
            row=2, column=1, sticky="w", padx=(20, 0))

        def do_sort():
            self.manager.sort(key=key_var.get(), descending=(order_var.get() == "desc"))
            win.destroy()
            self.view_all()
            self._set_status(f"Sorted records by {key_var.get()} "
                              f"({'descending' if order_var.get() == 'desc' else 'ascending'}).")

        ttk.Button(frm, text="Sort", command=do_sort).grid(row=4, column=0, columnspan=2, pady=(10, 0))

        win.wait_window(win)

    # ------------------------------------------------------------------
    #  Menu item 6 - Add
    # ------------------------------------------------------------------
    def add_record(self):
        StudentForm(self, self.manager)
        self._set_status(f"Add student dialog closed. Total students: {len(self.manager.students)}")
        self.view_all()

    # ------------------------------------------------------------------
    #  Menu item 7 - Delete
    # ------------------------------------------------------------------
    def delete_record(self):
        if not self.manager.students:
            messagebox.showinfo("No data", "There are no student records loaded.")
            return
        picker = StudentPicker(self, self.manager, title="Delete a Student")
        if picker.result:
            s = picker.result
            confirm = messagebox.askyesno(
                "Confirm delete",
                f"Are you sure you want to delete the record for:\n\n{s.name} ({s.code})?")
            if confirm:
                self.manager.delete_student(s)
                self._set_status(f"Deleted {s.name} ({s.code}). Total students: {len(self.manager.students)}")
                self.view_all()

    # ------------------------------------------------------------------
    #  Menu item 8 - Update
    # ------------------------------------------------------------------
    def update_record(self):
        if not self.manager.students:
            messagebox.showinfo("No data", "There are no student records loaded.")
            return
        picker = StudentPicker(self, self.manager, title="Select Student to Update")
        if picker.result:
            StudentForm(self, self.manager, student=picker.result)
            self._set_status(f"Updated record for {picker.result.name} ({picker.result.code}).")
            self.view_all()

    # ------------------------------------------------------------------
    def reload_data(self):
        self.manager.load()
        self._write(f"Reloaded {len(self.manager.students)} student records from file.\n")
        self._set_status("Data reloaded from file.")


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
