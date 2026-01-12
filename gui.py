"""
Модуль графического интерфейса.
Содержит класс Application для работы с Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from models import Employee, Task, Project
from storage import DatabaseManager
from utils import extract_emails, read_csv_to_df, format_currency
from analytics import WorkAnalytics, analyze_csv_data


class Application(tk.Tk):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()

        self.title("Учет рабочего времени и задач")
        self.geometry("1200x700")

        self._db = DatabaseManager()

        self._projects_map = {}
        self._employees_map = {}
        self._current_tab = "employees"

        self._create_layout()
        self._refresh_all()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """Обработчик закрытия окна."""
        self._db.close()
        self.destroy()

    def _create_layout(self):
        """Создаёт основной макет приложения."""
        # Главное окно
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Навигация
        self._left_frame = ttk.LabelFrame(main_frame, text="Навигация", width=150)
        self._left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self._left_frame.pack_propagate(False)

        # Контент
        self._center_frame = ttk.LabelFrame(main_frame, text="Данные", width=550)
        self._center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Элементы ввода
        self._right_frame = ttk.LabelFrame(main_frame, text="Управление", width=400)
        self._right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self._right_frame.pack_propagate(False)

        self._create_navigation()

        self._create_employees_view()
        self._create_projects_view()
        self._create_tasks_view()
        self._create_tools_view()

        self._show_tab("employees")

    def _create_navigation(self):
        """Создаёт панель навигации."""
        ttk.Button(self._left_frame, text="Сотрудники", width=18,
                   command=lambda: self._show_tab("employees")).pack(pady=10, padx=5)
        ttk.Button(self._left_frame, text="Проекты", width=18,
                   command=lambda: self._show_tab("projects")).pack(pady=10, padx=5)
        ttk.Button(self._left_frame, text="Задачи", width=18,
                   command=lambda: self._show_tab("tasks")).pack(pady=10, padx=5)
        ttk.Button(self._left_frame, text="Инструменты", width=18,
                   command=lambda: self._show_tab("tools")).pack(pady=10, padx=5)
        ttk.Button(self._left_frame, text="Аналитика", width=18,
                   command=self._show_analytics).pack(pady=10, padx=5)

        # Фрейм для кнопок CSV внизу левого блока
        self._csv_buttons_frame = ttk.Frame(self._left_frame)
        self._csv_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self._csv_clear_btn = None
        self._csv_reload_btn = None
        self._csv_loaded = False

    def _show_tab(self, tab_name):
        """Переключает активную вкладку."""
        self._current_tab = tab_name

        for widget in self._center_frame.winfo_children():
            widget.pack_forget()
        for widget in self._right_frame.winfo_children():
            widget.pack_forget()

        if tab_name == "employees":
            self._emp_center.pack(fill=tk.BOTH, expand=True)
            self._emp_right.pack(fill=tk.BOTH, expand=True)
            self._center_frame.config(text="Список сотрудников")
            self._right_frame.config(text="Управление сотрудниками")
        elif tab_name == "projects":
            self._proj_center.pack(fill=tk.BOTH, expand=True)
            self._proj_right.pack(fill=tk.BOTH, expand=True)
            self._center_frame.config(text="Список проектов")
            self._right_frame.config(text="Управление проектами")
        elif tab_name == "tasks":
            self._task_center.pack(fill=tk.BOTH, expand=True)
            self._task_right.pack(fill=tk.BOTH, expand=True)
            self._center_frame.config(text="Список задач")
            self._right_frame.config(text="Управление задачами")
        elif tab_name == "tools":
            self._tools_center.pack(fill=tk.BOTH, expand=True)
            self._tools_right.pack(fill=tk.BOTH, expand=True)
            self._center_frame.config(text="Результаты")
            self._right_frame.config(text="Инструменты")

    def _show_analytics(self):
        """Показывает окно аналитики."""
        employees = self._db.get_all_employees()
        projects = self._db.get_all_projects()
        
        analytics = WorkAnalytics(employees, projects)
        report = analytics.generate_report()
        
        # Создаём новое окно
        analytics_window = tk.Toplevel(self)
        analytics_window.title("Аналитика")
        analytics_window.geometry("500x400")
        
        text = tk.Text(analytics_window, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        
        content = "=== АНАЛИТИЧЕСКИЙ ОТЧЁТ ===\n\n"
        content += f"Всего сотрудников: {report['total_employees']}\n"
        content += f"Всего проектов: {report['total_projects']}\n"
        content += f"Общая сумма к выплате: {format_currency(report['total_salary_expenses'])}\n"
        content += f"Всего отработано часов: {report['total_hours_worked']:.1f}\n"
        content += f"Средняя зарплата: {format_currency(report['average_salary'])}\n"
        content += f"Общий прогресс: {report['overall_progress']:.1f}%\n"
        
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)

    # ==================== Вкладка сотрудники ====================

    def _create_employees_view(self):
        """Создаёт интерфейс вкладки сотрудников."""
        self._emp_center = ttk.Frame(self._center_frame)

        columns = ("ID", "Имя", "Должность", "Зарплата", "Часы", "К выплате")
        self._emp_tree = ttk.Treeview(self._emp_center, columns=columns, show="headings")

        for col in columns:
            self._emp_tree.heading(col, text=col)
            self._emp_tree.column(col, width=90)

        self._emp_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._emp_tree.bind("<<TreeviewSelect>>", self._on_employee_select)

        self._emp_right = ttk.Frame(self._right_frame)

        form_frame = ttk.LabelFrame(self._emp_right, text="Данные сотрудника")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self._emp_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self._emp_name_var, width=25).grid(
            row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Должность:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self._emp_position_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self._emp_position_var, width=25).grid(
            row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Зарплата:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self._emp_salary_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self._emp_salary_var, width=25).grid(
            row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Добавить часы:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self._emp_hours_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self._emp_hours_var, width=25).grid(
            row=3, column=1, padx=5, pady=5)

        # Кнопки
        btn_frame = ttk.LabelFrame(self._emp_right, text="Действия")
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="Добавить сотрудника", width=25,
                   command=self._add_employee).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Обновить данные", width=25,
                   command=self._update_employee).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Удалить сотрудника", width=25,
                   command=self._delete_employee).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Добавить часы", width=25,
                   command=self._add_hours_to_employee).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Рассчитать зарплату", width=25,
                   command=self._calculate_employee_pay).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Очистить форму", width=25,
                   command=self._clear_employee_form).pack(pady=3, padx=5)

    def _refresh_employees(self):
        """Обновляет список сотрудников."""
        for item in self._emp_tree.get_children():
            self._emp_tree.delete(item)

        employees = self._db.get_all_employees()
        for emp in employees:
            pay = emp.calculate_pay()
            self._emp_tree.insert("", tk.END, values=(
                emp.get_id(), emp.get_name(), emp.get_position(),
                round(emp.get_salary(), 2), round(emp.get_hours_worked(), 2),
                round(pay, 2)
            ))

    def _on_employee_select(self, _):
        """Обработчик выбора сотрудника."""
        selected = self._emp_tree.selection()
        if selected:
            values = self._emp_tree.item(selected[0])["values"]
            self._emp_name_var.set(values[1])
            self._emp_position_var.set(values[2])
            self._emp_salary_var.set(values[3])

    def _add_employee(self):
        """Добавляет нового сотрудника."""
        try:
            name = self._emp_name_var.get().strip()
            if not name:
                raise ValueError("Введите имя сотрудника")

            salary_str = self._emp_salary_var.get()
            if salary_str:
                salary = float(salary_str)
            else:
                salary = 0

            employee = Employee(
                name=name,
                position=self._emp_position_var.get().strip(),
                salary=salary
            )
            self._db.add_employee(employee)
            self._refresh_all()
            self._clear_employee_form()
            messagebox.showinfo("Успех", "Сотрудник добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def _update_employee(self):
        """Обновляет данные сотрудника."""
        selected = self._emp_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите сотрудника")
            return

        try:
            emp_id = self._emp_tree.item(selected[0])["values"][0]
            employee = self._db.get_employee_by_id(emp_id)

            employee.set_name(self._emp_name_var.get().strip())
            employee.set_position(self._emp_position_var.get().strip())

            salary_str = self._emp_salary_var.get()
            if salary_str:
                employee.set_salary(float(salary_str))
            else:
                employee.set_salary(0)

            self._db.update_employee(employee)
            self._refresh_all()
            messagebox.showinfo("Успех", "Данные обновлены")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def _delete_employee(self):
        """Удаляет сотрудника."""
        selected = self._emp_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите сотрудника")
            return

        if messagebox.askyesno("Подтверждение", "Удалить сотрудника?"):
            emp_id = self._emp_tree.item(selected[0])["values"][0]
            self._db.delete_employee(emp_id)
            self._refresh_all()
            self._clear_employee_form()

    def _add_hours_to_employee(self):
        """Добавляет часы сотруднику."""
        selected = self._emp_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите сотрудника")
            return

        try:
            hours_str = self._emp_hours_var.get()
            if hours_str:
                hours = float(hours_str)
            else:
                hours = 0

            if hours <= 0:
                raise ValueError("Введите положительное количество часов")

            emp_id = self._emp_tree.item(selected[0])["values"][0]
            employee = self._db.get_employee_by_id(emp_id)
            employee.add_hours(hours)
            self._db.update_employee(employee)
            self._refresh_employees()
            self._emp_hours_var.set("")
            messagebox.showinfo("Успех", f"Добавлено {hours} часов")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def _calculate_employee_pay(self):
        """Рассчитывает зарплату сотрудника."""
        selected = self._emp_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите сотрудника")
            return

        emp_id = self._emp_tree.item(selected[0])["values"][0]
        employee = self._db.get_employee_by_id(emp_id)
        pay = employee.calculate_pay()
        hourly_rate = employee.get_salary() / 176

        message = f"Сотрудник: {employee.get_name()}\n"
        message += f"Месячная ставка: {format_currency(employee.get_salary())}\n"
        message += f"Часовая ставка: {format_currency(hourly_rate)}\n"
        message += f"Отработано часов: {employee.get_hours_worked():.2f}\n"
        message += f"К выплате: {format_currency(pay)}"

        messagebox.showinfo("Расчет зарплаты", message)

    def _clear_employee_form(self):
        """Очищает форму сотрудника."""
        self._emp_name_var.set("")
        self._emp_position_var.set("")
        self._emp_salary_var.set("")
        self._emp_hours_var.set("")

    # ==================== Вкладка проекты ====================

    def _create_projects_view(self):
        """Создаёт интерфейс вкладки проектов."""
        self._proj_center = ttk.Frame(self._center_frame)

        columns = ("ID", "Название", "Задач", "Завершено", "Прогресс")
        self._proj_tree = ttk.Treeview(self._proj_center, columns=columns, show="headings")

        for col in columns:
            self._proj_tree.heading(col, text=col)
            self._proj_tree.column(col, width=100)

        self._proj_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._proj_tree.bind("<<TreeviewSelect>>", self._on_project_select)

        self._proj_right = ttk.Frame(self._right_frame)

        form_frame = ttk.LabelFrame(self._proj_right, text="Данные проекта")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self._proj_title_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self._proj_title_var, width=25).grid(
            row=0, column=1, padx=5, pady=5)

        btn_frame = ttk.LabelFrame(self._proj_right, text="Действия")
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="Добавить проект", width=25,
                   command=self._add_project).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Обновить проект", width=25,
                   command=self._update_project).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Удалить проект", width=25,
                   command=self._delete_project).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Показать прогресс", width=25,
                   command=self._show_project_progress).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Очистить форму", width=25,
                   command=self._clear_project_form).pack(pady=3, padx=5)

    def _refresh_projects(self):
        """Обновляет список проектов."""
        for item in self._proj_tree.get_children():
            self._proj_tree.delete(item)

        projects = self._db.get_all_projects()
        for proj in projects:
            tasks = proj.get_tasks()
            completed = sum(1 for t in tasks if t.get_status() == "Завершено")
            progress = proj.project_progress()
            self._proj_tree.insert("", tk.END, values=(
                proj.get_id(), proj.get_title(), len(tasks), completed,
                f"{progress:.1f}%"
            ))

    def _on_project_select(self, _):
        """Обработчик выбора проекта."""
        selected = self._proj_tree.selection()
        if selected:
            values = self._proj_tree.item(selected[0])["values"]
            self._proj_title_var.set(values[1])

    def _add_project(self):
        """Добавляет новый проект."""
        try:
            title = self._proj_title_var.get().strip()
            if not title:
                raise ValueError("Введите название проекта")

            project = Project(title=title)
            self._db.add_project(project)
            self._refresh_all()
            self._proj_title_var.set("")
            messagebox.showinfo("Успех", "Проект добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def _update_project(self):
        """Обновляет проект."""
        selected = self._proj_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите проект")
            return

        try:
            proj_id = self._proj_tree.item(selected[0])["values"][0]
            title = self._proj_title_var.get().strip()
            if not title:
                raise ValueError("Введите название проекта")

            project = Project(title=title, project_id=proj_id)
            self._db.update_project(project)
            self._refresh_projects()
            messagebox.showinfo("Успех", "Проект обновлен")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def _delete_project(self):
        """Удаляет проект."""
        selected = self._proj_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите проект")
            return

        if messagebox.askyesno("Подтверждение", "Удалить проект и все его задачи?"):
            proj_id = self._proj_tree.item(selected[0])["values"][0]
            self._db.delete_project(proj_id)
            self._refresh_all()
            self._proj_title_var.set("")

    def _show_project_progress(self):
        """Показывает прогресс проекта."""
        selected = self._proj_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите проект")
            return

        values = self._proj_tree.item(selected[0])["values"]
        message = f"Проект: {values[1]}\n"
        message += f"Всего задач: {values[2]}\n"
        message += f"Завершено: {values[3]}\n"
        message += f"Прогресс: {values[4]}"

        messagebox.showinfo("Прогресс проекта", message)

    def _clear_project_form(self):
        """Очищает форму проекта."""
        self._proj_title_var.set("")

    # ==================== Вкладка задачи ====================

    def _create_tasks_view(self):
        """Создаёт интерфейс вкладки задач."""
        self._task_center = ttk.Frame(self._center_frame)

        columns = ("ID", "Название", "Описание", "Статус", "Сотрудник", "Проект")
        self._task_tree = ttk.Treeview(self._task_center, columns=columns, show="headings")

        for col in columns:
            self._task_tree.heading(col, text=col)
            self._task_tree.column(col, width=90)

        self._task_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._task_tree.bind("<<TreeviewSelect>>", self._on_task_select)

        self._task_right = ttk.Frame(self._right_frame)

        form_frame = ttk.LabelFrame(self._task_right, text="Данные задачи")
        form_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self._task_title_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self._task_title_var, width=25).grid(
            row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self._task_desc_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self._task_desc_var, width=25).grid(
            row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Проект:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self._task_project_var = tk.StringVar()
        self._task_project_combo = ttk.Combobox(form_frame, textvariable=self._task_project_var,
                                                width=22, state="readonly")
        self._task_project_combo.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Сотрудник:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self._task_employee_var = tk.StringVar()
        self._task_employee_combo = ttk.Combobox(form_frame, textvariable=self._task_employee_var,
                                                 width=22, state="readonly")
        self._task_employee_combo.grid(row=3, column=1, padx=5, pady=5)

        btn_frame = ttk.LabelFrame(self._task_right, text="Действия")
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="Добавить задачу", width=25,
                   command=self._add_task).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Назначить сотрудника", width=25,
                   command=self._assign_employee).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Завершить задачу", width=25,
                   command=self._complete_task).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Удалить задачу", width=25,
                   command=self._delete_task).pack(pady=3, padx=5)
        ttk.Button(btn_frame, text="Очистить форму", width=25,
                   command=self._clear_task_form).pack(pady=3, padx=5)

    def _refresh_tasks(self):
        """Обновляет список задач."""
        for item in self._task_tree.get_children():
            self._task_tree.delete(item)

        projects = self._db.get_all_projects()
        self._projects_map = {}
        project_values = []
        for p in projects:
            key = f"{p.get_id()}: {p.get_title()}"
            self._projects_map[key] = p.get_id()
            project_values.append(key)
        self._task_project_combo["values"] = project_values

        employees = self._db.get_all_employees()
        self._employees_map = {}
        employee_values = [""]
        for e in employees:
            key = f"{e.get_id()}: {e.get_name()}"
            self._employees_map[key] = e.get_id()
            employee_values.append(key)
        self._task_employee_combo["values"] = employee_values

        for project in projects:
            tasks = self._db.get_tasks_by_project(project.get_id())
            for task in tasks:
                employee = task.get_assigned_employee()
                emp_name = employee.get_name() if employee else "-"
                self._task_tree.insert("", tk.END, values=(
                    task.get_id(), task.get_title(), task.get_description(),
                    task.get_status(), emp_name, project.get_title()
                ))

    def _on_task_select(self, _):
        """Обработчик выбора задачи."""
        selected = self._task_tree.selection()
        if selected:
            values = self._task_tree.item(selected[0])["values"]
            self._task_title_var.set(values[1])
            self._task_desc_var.set(values[2])

    def _add_task(self):
        """Добавляет новую задачу."""
        try:
            title = self._task_title_var.get().strip()
            if not title:
                raise ValueError("Введите название задачи")

            project_key = self._task_project_var.get()
            if not project_key:
                raise ValueError("Выберите проект")

            project_id = self._projects_map[project_key]

            employee = None
            emp_key = self._task_employee_var.get()
            if emp_key:
                emp_id = self._employees_map[emp_key]
                employee = self._db.get_employee_by_id(emp_id)

            task = Task(
                title=title,
                description=self._task_desc_var.get().strip(),
                assigned_employee=employee,
                project_id=project_id
            )
            self._db.add_task(task)
            self._refresh_all()
            self._clear_task_form()
            messagebox.showinfo("Успех", "Задача добавлена")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def _assign_employee(self):
        """Назначает сотрудника на задачу."""
        selected = self._task_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу")
            return

        emp_key = self._task_employee_var.get()
        if not emp_key:
            messagebox.showwarning("Внимание", "Выберите сотрудника")
            return

        task_id = self._task_tree.item(selected[0])["values"][0]
        emp_id = self._employees_map[emp_key]

        projects = self._db.get_all_projects()
        for project in projects:
            tasks = self._db.get_tasks_by_project(project.get_id())
            for task in tasks:
                if task.get_id() == task_id:
                    employee = self._db.get_employee_by_id(emp_id)
                    task.assign_employee(employee)
                    self._db.update_task(task)
                    self._refresh_all()
                    messagebox.showinfo("Успех", f"Задача назначена сотруднику {employee.get_name()}")
                    return

    def _complete_task(self):
        """Завершает задачу."""
        selected = self._task_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу")
            return

        task_id = self._task_tree.item(selected[0])["values"][0]

        projects = self._db.get_all_projects()
        for project in projects:
            tasks = self._db.get_tasks_by_project(project.get_id())
            for task in tasks:
                if task.get_id() == task_id:
                    task.mark_complete()
                    self._db.update_task(task)
                    self._refresh_all()
                    messagebox.showinfo("Успех", "Задача завершена")
                    return

    def _delete_task(self):
        """Удаляет задачу."""
        selected = self._task_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу")
            return

        if messagebox.askyesno("Подтверждение", "Удалить задачу?"):
            task_id = self._task_tree.item(selected[0])["values"][0]
            self._db.delete_task(task_id)
            self._refresh_all()
            self._clear_task_form()

    def _clear_task_form(self):
        """Очищает форму задачи."""
        self._task_title_var.set("")
        self._task_desc_var.set("")
        self._task_project_var.set("")
        self._task_employee_var.set("")

    # ==================== Вкладка инструменты ====================

    def _create_tools_view(self):
        """Создаёт интерфейс вкладки инструментов."""
        self._tools_center = ttk.Frame(self._center_frame)

        email_result_frame = ttk.LabelFrame(self._tools_center, text="Найденные email-адреса")
        email_result_frame.pack(fill=tk.X, padx=5, pady=5)

        self._email_result = tk.Text(email_result_frame, height=5, width=60, state=tk.DISABLED)
        self._email_result.pack(padx=5, pady=5)

        csv_frame = ttk.LabelFrame(self._tools_center, text="Данные из CSV файла")
        csv_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._csv_info_label = ttk.Label(csv_frame, text="Файл не загружен")
        self._csv_info_label.pack(anchor=tk.W, padx=5, pady=2)

        self._csv_tree = ttk.Treeview(csv_frame, show="headings")
        self._csv_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._tools_right = ttk.Frame(self._right_frame)

        email_frame = ttk.LabelFrame(self._tools_right, text="Поиск email-адресов")
        email_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(email_frame, text="Введите текст:").pack(anchor=tk.W, padx=5, pady=2)
        self._email_text = tk.Text(email_frame, height=6, width=35)
        self._email_text.pack(padx=5, pady=5)

        ttk.Button(email_frame, text="Найти email", width=25,
                   command=self._extract_emails).pack(pady=5)

        csv_btn_frame = ttk.LabelFrame(self._tools_right, text="Работа с CSV")
        csv_btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(csv_btn_frame, text="Открыть CSV файл", width=25,
                   command=self._open_csv).pack(pady=10, padx=5)

    def _extract_emails(self):
        """Извлекает email-адреса из текста."""
        text = self._email_text.get("1.0", tk.END)
        emails = extract_emails(text)

        self._email_result.config(state=tk.NORMAL)
        self._email_result.delete("1.0", tk.END)
        if emails:
            result = "Email из текста:\n"
            for email in emails:
                result += email + "\n"
            self._email_result.insert("1.0", result)
        else:
            self._email_result.insert("1.0", "Email-адреса не найдены")
        self._email_result.config(state=tk.DISABLED)

    def _open_csv(self):
        """Открывает и отображает CSV файл."""
        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            df = read_csv_to_df(file_path)

            for item in self._csv_tree.get_children():
                self._csv_tree.delete(item)

            columns = list(df.columns)
            self._csv_tree["columns"] = columns
            for col in columns:
                self._csv_tree.heading(col, text=col)
                self._csv_tree.column(col, width=100)

            for index in range(len(df)):
                row = df.iloc[index]
                values = list(row)
                self._csv_tree.insert("", tk.END, values=values)

            info_text = f"Загружено: {len(df)} строк, {len(columns)} столбцов"
            self._csv_info_label.config(text=info_text)

            # Ищем email в данных CSV
            all_emails = []
            for index in range(len(df)):
                row = df.iloc[index]
                for value in row:
                    text_value = str(value)
                    found_emails = extract_emails(text_value)
                    for email in found_emails:
                        if email not in all_emails:
                            all_emails.append(email)

            self._email_result.config(state=tk.NORMAL)
            self._email_result.delete("1.0", tk.END)
            if all_emails:
                result = "Email из CSV файла:\n"
                for email in all_emails:
                    result += email + "\n"
                self._email_result.insert("1.0", result)
            else:
                self._email_result.insert("1.0", "Email-адреса в CSV файле не найдены")
            self._email_result.config(state=tk.DISABLED)

            self._show_csv_buttons()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{str(e)}")

    def _show_csv_buttons(self):
        """Показывает кнопки управления CSV."""
        if self._csv_loaded:
            return

        self._csv_loaded = True

        ttk.Separator(self._csv_buttons_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        ttk.Label(self._csv_buttons_frame, text="CSV файл:").pack(pady=2)

        self._csv_clear_btn = ttk.Button(self._csv_buttons_frame, text="Очистить", width=18,
                                         command=self._clear_csv)
        self._csv_clear_btn.pack(pady=3, padx=5)

        self._csv_reload_btn = ttk.Button(self._csv_buttons_frame, text="Другой файл", width=18,
                                          command=self._open_csv)
        self._csv_reload_btn.pack(pady=3, padx=5)

    def _clear_csv(self):
        """Очищает данные CSV."""
        for item in self._csv_tree.get_children():
            self._csv_tree.delete(item)

        self._csv_tree["columns"] = []
        self._csv_info_label.config(text="Файл не загружен")

        self._email_result.config(state=tk.NORMAL)
        self._email_result.delete("1.0", tk.END)
        self._email_result.config(state=tk.DISABLED)

        self._hide_csv_buttons()

    def _hide_csv_buttons(self):
        """Скрывает кнопки управления CSV."""
        for widget in self._csv_buttons_frame.winfo_children():
            widget.destroy()

        self._csv_clear_btn = None
        self._csv_reload_btn = None
        self._csv_loaded = False

    # ==================== Общие методы ====================

    def _refresh_all(self):
        """Обновляет все списки."""
        self._refresh_employees()
        self._refresh_projects()
        self._refresh_tasks()