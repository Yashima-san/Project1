import sqlite3
import tkinter as tk
from tkinter import messagebox, Listbox, StringVar, Entry, Button
import tkinter.ttk as ttk


class TodoApp:
    def __init__(self, root, user_id):
        self.root = root
        self.root.title("Список дел")
        self.user_id = user_id  # используем user_id

        self.task_var = StringVar()
        self.task_listbox = Listbox(root, width=50, height=10)
        self.task_listbox.pack()

        self.task_entry = Entry(root, textvariable=self.task_var)
        self.task_entry.pack()

        self.add_task_button = Button(root, text="Добавить задачу", command=self.add_task)
        self.add_task_button.pack()

        self.remove_task_button = Button(root, text="Удалить задачу", command=self.remove_task)
        self.remove_task_button.pack()

        self.load_tasks()

    def load_tasks(self):
        conn = sqlite3.connect('todo.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (self.user_id,))
        tasks = cursor.fetchall()
        self.task_listbox.delete(0, tk.END)  # Очистка списка перед загрузкой
        for task in tasks:
            self.task_listbox.insert(tk.END, task[2])  # задача находится на третьей позиции
        conn.close()

    def add_task(self):
        task = self.task_var.get()
        if task:
            conn = sqlite3.connect('todo.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tasks (user_id, task, completed) VALUES (?, ?, ?)', (self.user_id, task, 0))
            conn.commit()
            conn.close()
            self.task_listbox.insert(tk.END, task)
            self.task_var.set("")
        else:
            messagebox.showwarning("Предупреждение", "Вы должны ввести задачу.")

    def remove_task(self):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            task_text = self.task_listbox.get(selected_task_index)
            conn = sqlite3.connect('todo.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE user_id = ? AND task = ?', (self.user_id, task_text))
            conn.commit()
            conn.close()
            self.task_listbox.delete(selected_task_index)
        else:
            messagebox.showwarning("Предупреждение", "Вы должны выбрать задачу.")


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
            # После успешной авторизации можно перейти к основному приложению
            user_id = user[0]  # получаем id пользователя
            self.root.destroy()
            todo = TodoApp(tk.Tk(), user_id)  # передаем user_id
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
