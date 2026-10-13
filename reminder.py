import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import date, datetime
import os

TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.txt")

COLOR_BG      = "#000000"
COLOR_TITLE   = "#FFD700"   # золотой — заголовок
COLOR_PAST    = "#FF4444"   # красный — просрочено
COLOR_TODAY   = "#FF8C00"   # оранжевый — сегодня
COLOR_FUTURE  = "#FFFFFF"   # белый — в будущем
COLOR_COMMENT = "#555555"   # серый — комментарий (не показываем)

FONT_TITLE  = ("Arial", 20, "bold underline")
FONT_TASK   = ("Arial", 13)


def load_tasks():
    tasks = []
    if not os.path.exists(TASKS_FILE):
        return tasks
    with open(TASKS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|", 1)
            if len(parts) != 2:
                continue
            date_str, name = parts[0].strip(), parts[1].strip()
            try:
                task_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                tasks.append((task_date, name))
            except ValueError:
                continue
    tasks.sort(key=lambda t: t[0])
    return tasks


def save_tasks(tasks):
    lines = ["# Файл задач. Формат: YYYY-MM-DD | Название задачи\n",
             "# Строки начинающиеся с # — комментарии, игнорируются\n",
             "\n"]
    for task_date, name in tasks:
        lines.append(f"{task_date.strftime('%Y-%m-%d')} | {name}\n")
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)


def format_task(task_date, name, today):
    delta = (today - task_date).days
    if delta > 0:
        # корректное склонение "день/дня/дней"
        d = delta % 100
        if 11 <= d <= 14:
            word = "дней"
        else:
            d1 = delta % 10
            if d1 == 1:
                word = "день"
            elif 2 <= d1 <= 4:
                word = "дня"
            else:
                word = "дней"
        return f"Прошло {delta} {word} от {name}", COLOR_PAST
    elif delta == 0:
        return f"Прямо сейчас происходит: {name}", COLOR_TODAY
    else:
        delta = abs(delta)
        d = delta % 100
        if 11 <= d <= 14:
            word = "дней"
        else:
            d1 = delta % 10
            if d1 == 1:
                word = "день"
            elif 2 <= d1 <= 4:
                word = "дня"
            else:
                word = "дней"
        return f"Осталось {delta} {word} до: {name}", COLOR_FUTURE


class ReminderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Что мне делать, как мне жить?")
        self.configure(bg=COLOR_BG)
        self.resizable(True, True)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        top = tk.Frame(self, bg=COLOR_BG)
        top.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(top, text="Мои текущие задачи", font=FONT_TITLE,
                 fg=COLOR_TITLE, bg=COLOR_BG).pack(side="left", expand=True)

        btn_frame = tk.Frame(top, bg=COLOR_BG)
        btn_frame.pack(side="right")

        btn_style = dict(bg="#222222", fg="#CCCCCC", relief="flat",
                         font=("Arial", 10), cursor="hand2", padx=8, pady=3)

        tk.Button(btn_frame, text="+ Добавить", command=self.add_task,
                  **btn_style).pack(side="left", padx=4)
        tk.Button(btn_frame, text="− Удалить", command=self.delete_task,
                  **btn_style).pack(side="left", padx=4)
        tk.Button(btn_frame, text="⟳ Обновить", command=self.refresh,
                  **btn_style).pack(side="left", padx=4)

        tk.Frame(self, bg="#333333", height=1).pack(fill="x", padx=10, pady=8)

        # Прокручиваемая область задач
        canvas = tk.Canvas(self, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.task_frame = tk.Frame(canvas, bg=COLOR_BG)
        self.canvas_window = canvas.create_window((0, 0), window=self.task_frame, anchor="nw")

        self.task_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(self.canvas_window, width=e.width))
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.canvas = canvas

        # Статус-бар внизу
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, font=("Arial", 9),
                 fg="#666666", bg=COLOR_BG).pack(pady=(0, 6))

    def refresh(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        tasks = load_tasks()
        today = date.today()

        if not tasks:
            tk.Label(self.task_frame, text="Нет задач. Добавьте первую!",
                     font=FONT_TASK, fg="#555555", bg=COLOR_BG).pack(anchor="w", padx=20, pady=10)
        else:
            for task_date, name in tasks:
                text, color = format_task(task_date, name, today)
                tk.Label(self.task_frame, text=text, font=FONT_TASK,
                         fg=color, bg=COLOR_BG, anchor="w").pack(
                    fill="x", padx=20, pady=2)

        past   = sum(1 for d, _ in tasks if d < today)
        today_ = sum(1 for d, _ in tasks if d == today)
        future = sum(1 for d, _ in tasks if d > today)
        self.status_var.set(
            f"Всего: {len(tasks)}  |  Просрочено: {past}  |  Сегодня: {today_}  |  Предстоит: {future}"
            f"  |  Дата: {today.strftime('%d.%m.%Y')}"
        )

    def add_task(self):
        name = simpledialog.askstring("Новая задача", "Название задачи:", parent=self)
        if not name or not name.strip():
            return
        date_str = simpledialog.askstring(
            "Новая задача", "Дата (ГГГГ-ММ-ДД):", parent=self,
            initialvalue=date.today().strftime("%Y-%m-%d"))
        if not date_str:
            return
        try:
            task_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
            return
        tasks = load_tasks()
        tasks.append((task_date, name.strip()))
        tasks.sort(key=lambda t: t[0])
        save_tasks(tasks)
        self.refresh()

    def delete_task(self):
        tasks = load_tasks()
        if not tasks:
            messagebox.showinfo("Удаление", "Нет задач для удаления.")
            return
        today = date.today()
        items = [format_task(d, n, today)[0] for d, n in tasks]

        win = tk.Toplevel(self)
        win.title("Удалить задачу")
        win.configure(bg=COLOR_BG)
        win.grab_set()

        tk.Label(win, text="Выберите задачу для удаления:",
                 font=("Arial", 11), fg=COLOR_FUTURE, bg=COLOR_BG).pack(padx=15, pady=(12, 4))

        listbox = tk.Listbox(win, font=("Arial", 11), bg="#111111", fg=COLOR_FUTURE,
                             selectbackground="#333366", width=60, height=min(len(items), 15),
                             activestyle="none", borderwidth=0, highlightthickness=0)
        for item in items:
            listbox.insert(tk.END, item)
        listbox.pack(padx=15, pady=6)

        def confirm():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Выберите задачу", "Нужно выбрать задачу.", parent=win)
                return
            idx = sel[0]
            _, name = tasks[idx]
            if messagebox.askyesno("Подтверждение", f'Удалить задачу "{name}"?', parent=win):
                tasks.pop(idx)
                save_tasks(tasks)
                win.destroy()
                self.refresh()

        tk.Button(win, text="Удалить", command=confirm,
                  bg="#660000", fg="white", font=("Arial", 11),
                  relief="flat", padx=12, pady=4).pack(pady=(4, 12))


if __name__ == "__main__":
    app = ReminderApp()
    app.minsize(520, 300)
    app.geometry("680x480")
    app.mainloop()
