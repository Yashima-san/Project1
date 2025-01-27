import sqlite3
import tkinter as tk
from tkinter import messagebox, Listbox, StringVar, Button, ttk


class TodoApp:
    def __init__(self, root, user_id):
        self.root = root
        self.root.title("Список дел")
        self.root.geometry("650x430")
        self.user_id = user_id

        # Заголовки
        self.title_label = ttk.Label(self.root, text="Невыполненные задачи", font=("Arial", 14))
        self.title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.title_label1 = ttk.Label(self.root, text="Выполненные задачи", font=("Arial", 14))
        self.title_label1.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.task_listbox = Listbox(root, width=50, height=10)
        self.task_listbox.grid(row=1, column=0, padx=10, pady=10)
        self.task_listbox.bind('<Double-Button-1>', self.open_task)

        self.completed_listbox = Listbox(root, width=50, height=10)
        self.completed_listbox.grid(row=1, column=1, padx=10, pady=10)

        # Заменяем Entry на Text для ввода задач
        self.task_entry = tk.Text(root, height=5, width=30)
        self.task_entry.grid(row=2, column=0, padx=10, pady=10, columnspan=2)

        self.add_task_button = Button(root, text="Добавить задачу", command=self.add_task)
        self.add_task_button.grid(row=3, column=0, padx=10, pady=5)

        self.remove_task_button = Button(root, text="Удалить задачу", command=self.remove_task)
        self.remove_task_button.grid(row=3, column=1, padx=10, pady=5)

        self.complete_task_button = Button(root, text="Завершить задачу", command=self.complete_task)
        self.complete_task_button.grid(row=4, column=0, padx=10, pady=5)

        self.undo_button = Button(root, text="Отмена", command=self.undo_task)
        self.undo_button.grid(row=4, column=1, padx=10, pady=5)

        self.load_tasks()

    def load_tasks(self):
        conn = sqlite3.connect('todo.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE user_id = ? AND completed = 0', (self.user_id,))
        tasks = cursor.fetchall()
        self.task_listbox.delete(0, tk.END)
        for task in tasks:
            self.task_listbox.insert(tk.END, task[2])

        cursor.execute('SELECT * FROM tasks WHERE user_id = ? AND completed = 1', (self.user_id,))
        tasks = cursor.fetchall()
        self.completed_listbox.delete(0, tk.END)
        for task in tasks:
            self.completed_listbox.insert(tk.END, task[2])

        conn.close()

    def add_task(self):
        task = self.task_entry.get("1.0", tk.END).strip()  # Получаем текст из Text
        if task:
            conn = sqlite3.connect('todo.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tasks (user_id, task, completed) VALUES (?, ?, ?)', (self.user_id, task, 0))
            conn.commit()
            conn.close()
            self.task_listbox.insert(tk.END, task)
            self.task_entry.delete("1.0", tk.END)  # Очищаем поле ввода
            self.load_tasks()
        else:
            messagebox.showwarning("Предупреждение", "Вы должны ввести задачу.")

    def remove_task(self):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            task_text = self.task_listbox.get(selected_task_index)
            conn = sqlite3.connect('todo.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE user_id = ? AND task = ? AND completed = 0', (self.user_id, task_text))
            conn.commit()
            conn.close()
            self.task_listbox.delete(selected_task_index)
            self.load_tasks()
        else:
            selected_task_index = self.completed_listbox.curselection()
            if selected_task_index:
                task_text = self.completed_listbox.get(selected_task_index)
                conn = sqlite3.connect('todo.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM tasks WHERE user_id = ? AND task = ? AND completed = 1', (self.user_id, task_text))
                conn.commit()
                conn.close()
                self.completed_listbox.delete(selected_task_index)
                self.load_tasks()
            else:
                messagebox.showwarning("Предупреждение", "Вы должны выбрать задачу.")

    def complete_task(self):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            task_text = self.task_listbox.get(selected_task_index)
            conn = sqlite3.connect('todo.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE tasks SET completed = 1 WHERE user_id = ? AND task = ?', (self.user_id, task_text))
            conn.commit()
            conn.close()
            self.load_tasks()
        else:
            messagebox.showwarning("Предупреждение", "Вы должны выбрать задачу.")

    def undo_task(self):
        selected_task_index = self.completed_listbox.curselection()
        if selected_task_index:
            task_text = self.completed_listbox.get(selected_task_index)
            conn = sqlite3.connect('todo.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE tasks SET completed = 0 WHERE user_id = ? AND task = ?', (self.user_id, task_text))
            conn.commit()
            conn.close()
            self.load_tasks()
        else:
            messagebox.showwarning("Предупреждение", "Вы должны выбрать задачу.")

    def open_task(self, event):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            task_text = self.task_listbox.get(selected_task_index)
            self.open_task_dialog(task_text)

    def open_task_dialog(self, task_text):
        # Создаем новое окно для редактирования задачи
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование задачи")
        dialog.geometry("400x300")

        task_text_widget = tk.Text(dialog, height=10)
        task_text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        task_text_widget.insert(tk.END, task_text)  # Заполняем текстом задачи

        edit_button = Button(dialog, text="Сохранить изменения", command=lambda: self.save_changes(task_text_widget, dialog, task_text))
        edit_button.pack(pady=5)

    def save_changes(self, task_text_widget, dialog, old_task_text):
        new_task_text = task_text_widget.get("1.0", tk.END).strip()
        if new_task_text:
            conn = sqlite3.connect('todo.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE tasks SET task = ?, completed = 0 WHERE user_id = ? AND task = ?', (new_task_text, self.user_id, old_task_text))
            conn.commit()
            conn.close()
            self.load_tasks()
            dialog.destroy()  # Закрываем диалог
        else:
            messagebox.showwarning("Предупреждение", "Вы должны ввести новую задачу.")

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Вход в систему")
        self.root.geometry("300x300")

        # Заголовок
        self.title_label = ttk.Label(self.root, text="Вход в систему", font=("Arial", 18))
        self.title_label.pack(pady=20)

        # Поля ввода
        self.username_var = StringVar()
        self.password_var = StringVar()

        ttk.Label(self.root, text="Логин:").pack()
        self.username_entry = ttk.Entry(self.root, textvariable=self.username_var)
        self.username_entry.pack()

        ttk.Label(self.root, text="Пароль:").pack()
        self.password_entry = ttk.Entry(self.root, textvariable=self.password_var, show="*")
        self.password_entry.pack()

        # Кнопка входа
        self.login_button = ttk.Button(self.root, text="Войти", command=self.login)
        self.login_button.pack(pady=10)

        # Кнопка регистрации
        self.register_button = ttk.Button(self.root, text="Регистрация", command=self.register)
        self.register_button.pack()

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        conn = sqlite3.connect('todo.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id = user[0]
            self.root.destroy()
            todo = TodoApp(tk.Tk(), user_id)
            todo.root.mainloop()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def register(self):
        self.reg_username_var = StringVar()
        self.reg_password_var = StringVar()

        # Создаем новое окно для регистрации
        self.register_window = tk.Toplevel(self.root)
        self.register_window.title("Регистрация")
        self.register_window.geometry("300x300")

        # Заголовок
        self.title_label = ttk.Label(self.register_window, text="Регистрация", font=("Arial", 18))
        self.title_label.pack(pady=20)

        # Поля ввода
        ttk.Label(self.register_window, text="Имя пользователя:").pack()
        self.reg_username_entry = ttk.Entry(self.register_window, textvariable=self.reg_username_var)
        self.reg_username_entry.pack()

        ttk.Label(self.register_window, text="Пароль:").pack()
        self.reg_password_entry = ttk.Entry(self.register_window, textvariable=self.reg_password_var, show="*")
        self.reg_password_entry.pack()

        # Кнопка регистрации
        self.reg_button = ttk.Button(self.register_window, text="Зарегистрироваться", command=self.register_user)
        self.reg_button.pack(pady=10)

    def register_user(self):
        username = self.reg_username_var.get()
        password = self.reg_password_var.get()

        try:
            conn = sqlite3.connect('todo.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Вы успешно зарегистрированы!")
            self.register_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует.")

def create_db():
    conn = sqlite3.connect('todo.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            task TEXT NOT NULL,
            completed BOOLEAN NOT NULL CHECK (completed IN (0, 1))
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')

        conn.commit()
    except sqlite3.OperationalError as e:
        print("OperationalError:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    create_db()  # создаем базу данных и таблицы
    login_window = LoginWindow(tk.Tk())
    login_window.root.mainloop()
