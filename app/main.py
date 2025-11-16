import tkinter as tk
from tkinter import ttk, messagebox
from queries import JournalQueries
from auth import AuthManager

class LoginWindow:
    def __init__(self, root, auth_manager):
        self.root = root
        self.root.title("Авторизация - Журнал успеваемости")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.auth_manager = auth_manager
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Авторизация", font=('Arial', 16, 'bold')).pack(pady=20)
        
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=20)
        
        ttk.Label(input_frame, text="Логин:").grid(row=0, column=0, padx=5, pady=10, sticky='e')
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(input_frame, textvariable=self.username_var, width=20)
        username_entry.grid(row=0, column=1, padx=5, pady=10)
        
        ttk.Label(input_frame, text="Пароль:").grid(row=1, column=0, padx=5, pady=10, sticky='e')
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(input_frame, textvariable=self.password_var, width=20, show='*')
        password_entry.grid(row=1, column=1, padx=5, pady=10)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Войти", command=self.login).pack(pady=4)
        ttk.Button(button_frame, text="Выйти", command=self.root.quit).pack(pady=10)
        
        ttk.Label(main_frame, text="По умолчанию: admin / admin123", 
                 font=('Arial', 9), foreground='gray').pack(pady=10)
        
        username_entry.focus()
    
    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return
        
        if self.auth_manager.login(username, password):
            self.root.destroy()
            app_root = tk.Tk()
            app = JournalApp(app_root, self.auth_manager)
            app_root.mainloop()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

class JournalApp:
    def __init__(self, root, auth_manager):
        self.root = root
        self.root.title("Журнал успеваемости")
        self.root.geometry("1200x700")
        
        self.auth_manager = auth_manager
        self.queries = JournalQueries()
        self.current_student_id = None
        self.current_student_info = None
        
        self.setup_menu()
        self.setup_ui()
        self.load_students()
        self.load_subjects()
    
    def setup_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выход", command=self.logout)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.students_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.students_frame, text="Студенты")
        self.setup_students_tab()
        
        self.grades_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.grades_frame, text="Оценки")
        self.setup_grades_tab()
        
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Статистика")
        self.setup_stats_tab()
    
    def setup_students_tab(self):
        control_frame = ttk.Frame(self.students_frame)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(control_frame, text="Добавить студента", 
                  command=self.add_student_dialog).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Удалить студента", 
                  command=self.delete_student).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Обновить", 
                  command=self.load_students).pack(side='left', padx=5)
        
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side='right', padx=5)
        ttk.Label(search_frame, text="Поиск:").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side='left', padx=5)
        ttk.Button(search_frame, text="Найти", 
                  command=self.search_students).pack(side='left')
        
        columns = ("ID", "Фамилия", "Имя", "Группа", "Дата создания")
        self.students_tree = ttk.Treeview(self.students_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(self.students_frame, orient="vertical", command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=scrollbar.set)
        
        self.students_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        self.students_tree.bind('<Double-1>', self.on_student_select)
    
    def setup_grades_tab(self):
        left_frame = ttk.Frame(self.grades_frame)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        ttk.Label(left_frame, text="Список студентов", font=('Arial', 12, 'bold')).pack(pady=5)
        
        columns = ("ID", "Фамилия", "Имя", "Группа")
        self.grades_students_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.grades_students_tree.heading(col, text=col)
            self.grades_students_tree.column(col, width=100)
        
        students_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.grades_students_tree.yview)
        self.grades_students_tree.configure(yscrollcommand=students_scrollbar.set)
        
        self.grades_students_tree.pack(side='left', fill='y', pady=10)
        students_scrollbar.pack(side='right', fill='y', pady=10)
        
        self.grades_students_tree.bind('<<TreeviewSelect>>', self.on_grades_student_select)
        
        right_frame = ttk.Frame(self.grades_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill='x', pady=5)
        
        ttk.Label(info_frame, text="Информация о студенте:", font=('Arial', 11, 'bold')).pack(anchor='w')
        self.student_info_label = ttk.Label(info_frame, text="Выберите студента из списка слева", font=('Arial', 10))
        self.student_info_label.pack(anchor='w', pady=2)
        
        self.avg_label = ttk.Label(info_frame, text="Средний балл: -", font=('Arial', 10))
        self.avg_label.pack(anchor='w', pady=2)
        
        grade_control = ttk.Frame(right_frame)
        grade_control.pack(fill='x', pady=10)
        
        ttk.Label(grade_control, text="Добавить оценку:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=5)
        
        control_subframe = ttk.Frame(grade_control)
        control_subframe.pack(fill='x', pady=5)
        
        ttk.Label(control_subframe, text="Предмет:").pack(side='left', padx=(0, 5))
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(control_subframe, textvariable=self.subject_var, state='readonly', width=15)
        self.subject_combo.pack(side='left', padx=5)
        
        ttk.Label(control_subframe, text="Оценка:").pack(side='left', padx=(20,5))
        self.grade_var = tk.StringVar()
        grade_combo = ttk.Combobox(control_subframe, textvariable=self.grade_var, 
                                  values=['2', '3', '4', '5'], width=5, state='readonly')
        grade_combo.pack(side='left', padx=5)
        
        ttk.Button(control_subframe, text="Добавить оценку", 
                  command=self.add_grade).pack(side='left', padx=20)
        
        ttk.Label(right_frame, text="Оценки студента:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=5)
        
        columns = ("ID", "Предмет", "Оценка", "Дата")
        self.grades_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.grades_tree.heading(col, text=col)
            self.grades_tree.column(col, width=100)
        
        grades_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.grades_tree.yview)
        self.grades_tree.configure(yscrollcommand=grades_scrollbar.set)
        
        self.grades_tree.pack(side='left', fill='both', expand=True, pady=5)
        grades_scrollbar.pack(side='right', fill='y', pady=5)
    
    def setup_stats_tab(self):
        top_frame = ttk.Frame(self.stats_frame)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="Топ студентов по среднему баллу", 
                 font=('Arial', 12, 'bold')).pack()
        
        columns = ("Место", "Студент", "Группа", "Средний балл")
        self.stats_tree = ttk.Treeview(top_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=100)
        
        self.stats_tree.pack(fill='x', pady=10)
        
        ttk.Button(top_frame, text="Обновить статистику", 
                  command=self.load_statistics).pack(pady=5)
        
        bottom_frame = ttk.Frame(self.stats_frame)
        bottom_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(bottom_frame, text="Статистика по предметам", 
                 font=('Arial', 12, 'bold')).pack()
        
        subject_stats_frame = ttk.Frame(bottom_frame)
        subject_stats_frame.pack(fill='x', pady=10)
        
        ttk.Label(subject_stats_frame, text="Выберите предмет:").pack(side='left')
        self.stats_subject_var = tk.StringVar()
        self.stats_subject_combo = ttk.Combobox(subject_stats_frame, 
                                               textvariable=self.stats_subject_var, 
                                               state='readonly', width=20)
        self.stats_subject_combo.pack(side='left', padx=5)
        ttk.Button(subject_stats_frame, text="Показать статистику", 
                  command=self.show_subject_stats).pack(side='left', padx=5)
        
        self.stats_text = tk.Text(bottom_frame, height=8, width=50)
        stats_scrollbar = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side='left', fill='both', expand=True, pady=5)
        stats_scrollbar.pack(side='right', fill='y', pady=5)
    
    def load_students(self):
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)

        for item in self.grades_students_tree.get_children():
            self.grades_students_tree.delete(item)
        
        students = self.queries.get_all_students()
        for student in students:

            self.students_tree.insert("", "end", values=(
                student.id,
                student.last_name,
                student.first_name,
                student.group_name,
                student.created_at.strftime('%Y-%m-%d')
            ))
            
            self.grades_students_tree.insert("", "end", values=(
                student.id,
                student.last_name,
                student.first_name,
                student.group_name
            ))
    
    def load_subjects(self):
        subjects = self.queries.get_all_subjects()
        subject_names = [subject.name for subject in subjects]
        self.subject_combo['values'] = subject_names
        self.stats_subject_combo['values'] = subject_names
        if subject_names:
            self.subject_combo.current(0)
            self.stats_subject_combo.current(0)
    
    def on_student_select(self, event):
        selection = self.students_tree.selection()
        if selection:
            item = self.students_tree.item(selection[0])
            student_id = item['values'][0]
            self.notebook.select(1)
            self.select_student_in_grades_tree(student_id)
    
    def on_grades_student_select(self, event):
        selection = self.grades_students_tree.selection()
        if selection:
            item = self.grades_students_tree.item(selection[0])
            student_id = item['values'][0]
            self.current_student_id = student_id
            self.show_student_grades(student_id)
    
    def select_student_in_grades_tree(self, student_id):
        for item in self.grades_students_tree.get_children():
            values = self.grades_students_tree.item(item)['values']
            if values and values[0] == student_id:
                self.grades_students_tree.selection_set(item)
                self.grades_students_tree.focus(item)
                self.current_student_id = student_id
                self.show_student_grades(student_id)
                break
    
    def show_student_grades(self, student_id):
        for item in self.grades_tree.get_children():
            self.grades_tree.delete(item)
        
        student = self.queries.get_student_by_id(student_id)
        
        if student:
            self.current_student_info = student
            self.student_info_label.config(
                text=f"{student.last_name} {student.first_name} ({student.group_name})"
            )
            
            grades = self.queries.get_student_grades(student_id)
            for grade in grades:
                self.grades_tree.insert("", "end", values=(
                    grade['id'],
                    grade['subject'],
                    grade['grade'],
                    grade['date'].strftime('%Y-%m-%d')
                ))
            
            avg_grade = self.queries.get_student_average(student_id)
            self.avg_label.config(text=f"Средний балл: {avg_grade}")
        else:
            self.student_info_label.config(text="Студент не найден")
            self.avg_label.config(text="Средний балл: -")
    
    def add_student_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить студента")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Имя:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        first_name_entry = ttk.Entry(dialog, width=20)
        first_name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Фамилия:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        last_name_entry = ttk.Entry(dialog, width=20)
        last_name_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Группа:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        group_entry = ttk.Entry(dialog, width=20)
        group_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def save():
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            group = group_entry.get().strip()
            
            if first_name and last_name and group:
                try:
                    self.queries.add_student(first_name, last_name, group)
                    self.load_students()
                    dialog.destroy()
                    messagebox.showinfo("Успех", "Студент добавлен успешно!")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при добавлении: {e}")
            else:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(row=3, column=0, columnspan=2, pady=20)
        first_name_entry.focus()
    
    def delete_student(self):
        selection = self.students_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите студента для удаления")
            return
        
        item = self.students_tree.item(selection[0])
        student_id = item['values'][0]
        student_name = f"{item['values'][1]} {item['values'][2]}"
        
        if messagebox.askyesno("Подтверждение", 
                             f"Вы уверены, что хотите удалить студента {student_name}?"):
            try:
                success = self.queries.delete_student(student_id)
                if success:
                    self.load_students()
                    messagebox.showinfo("Успех", "Студент удален успешно!")
                else:
                    messagebox.showerror("Ошибка", "Студент не найден")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении: {e}")
    
    def add_grade(self):
        if not self.current_student_id:
            messagebox.showwarning("Внимание", "Сначала выберите студента из списка")
            return
        
        subject_name = self.subject_var.get()
        grade_value = self.grade_var.get()
        
        if not subject_name or not grade_value:
            messagebox.showwarning("Внимание", "Выберите предмет и оценку")
            return
        
        try:
            subject = self.queries.get_subject_by_name(subject_name)
            
            if subject:
                self.queries.add_grade(self.current_student_id, subject.id, int(grade_value))
                self.show_student_grades(self.current_student_id)
                messagebox.showinfo("Успех", "Оценка добавлена успешно!")
                
                self.grade_var.set('')
            else:
                messagebox.showerror("Ошибка", "Предмет не найден")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении оценки: {e}")
    
    def search_students(self):
        search_term = self.search_var.get().strip()
        if not search_term:
            self.load_students()
            return
        
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        students = self.queries.search_students(search_term)
        for student in students:
            self.students_tree.insert("", "end", values=(
                student.id,
                student.last_name,
                student.first_name,
                student.group_name,
                student.created_at.strftime('%Y-%m-%d')
            ))
    
    def load_statistics(self):
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        
        top_students = self.queries.get_top_students(10)
        for i, student in enumerate(top_students, 1):
            self.stats_tree.insert("", "end", values=(
                i,
                student['name'],
                student['group'],
                student['average_grade']
            ))
    
    def show_subject_stats(self):
        subject_name = self.stats_subject_var.get()
        if not subject_name:
            messagebox.showwarning("Внимание", "Выберите предмет")
            return
        
        subject = self.queries.get_subject_by_name(subject_name)
        
        if subject:
            stats = self.queries.get_subject_statistics(subject.id)
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"Статистика по предмету: {subject_name}\n")
            self.stats_text.insert(tk.END, "=" * 40 + "\n\n")
            self.stats_text.insert(tk.END, f"Всего оценок: {stats['total_grades']}\n")
            self.stats_text.insert(tk.END, f"Средний балл: {stats['average_grade']}\n")
            self.stats_text.insert(tk.END, f"Минимальная оценка: {stats['min_grade']}\n")
            self.stats_text.insert(tk.END, f"Максимальная оценка: {stats['max_grade']}\n")
    
    def logout(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите выйти?"):
            self.auth_manager.logout()
            self.root.destroy()
            login_root = tk.Tk()
            LoginWindow(login_root, self.auth_manager)
            login_root.mainloop()
    
    def show_about(self):
        messagebox.showinfo("О программе", 
                          "Журнал успеваемости\n\n"
                          "Версия 1.0\n"
                          "Система управления успеваемостью студентов")

if __name__ == "__main__":
    from database import init_db
    from auth import AuthManager

    try:
        init_db()
        print("База данных успешно инициализирована")
    except Exception as e:
        print(f"Ошибка инициализации базы данных: {e}")

    auth_manager = AuthManager()
    auth_manager.create_admin_user()

    login_root = tk.Tk()
    LoginWindow(login_root, auth_manager)
    login_root.mainloop()