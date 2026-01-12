"""
Модуль для работы с базой данных.
Содержит класс DatabaseManager для CRUD операций.
"""

import sqlite3
from models import Employee, Task, Project


class DatabaseManager:
    """Менеджер базы данных для хранения сотрудников, проектов и задач."""

    def __init__(self, db_name="work_tracker.db"):
        self._db_name = db_name
        self._connection = None
        self._init_database()

    def _get_connection(self):
        """Возвращает соединение с базой данных."""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_name)
        return self._connection

    def _init_database(self):
        """Инициализирует структуру базы данных."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Таблица сотрудников
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT,
                salary REAL DEFAULT 0,
                hours_worked REAL DEFAULT 0
            )
        ''')

        # Таблица проектов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
            )
        ''')

        # Таблица задач
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'В процессе',
                employee_id INTEGER,
                project_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')

        conn.commit()

    def close(self):
        """Закрывает соединение с базой данных."""
        if self._connection:
            self._connection.close()
            self._connection = None

    # ==================== Операции с сотрудниками ====================

    def add_employee(self, employee):
        """Добавляет нового сотрудника в базу данных."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO employees (name, position, salary, hours_worked)
            VALUES (?, ?, ?, ?)
        ''', (employee.get_name(), employee.get_position(),
              employee.get_salary(), employee.get_hours_worked()))
        conn.commit()
        return cursor.lastrowid

    def update_employee(self, employee):
        """Обновляет данные сотрудника."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE employees 
            SET name=?, position=?, salary=?, hours_worked=?
            WHERE id=?
        ''', (employee.get_name(), employee.get_position(), employee.get_salary(),
              employee.get_hours_worked(), employee.get_id()))
        conn.commit()

    def delete_employee(self, employee_id):
        """Удаляет сотрудника из базы данных."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET employee_id=NULL WHERE employee_id=?',
                       (employee_id,))
        cursor.execute('DELETE FROM employees WHERE id=?', (employee_id,))
        conn.commit()

    def get_all_employees(self):
        """Возвращает список всех сотрудников."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, position, salary, hours_worked FROM employees')
        employees = []
        for row in cursor.fetchall():
            emp = Employee(
                employee_id=row[0],
                name=row[1],
                position=row[2],
                salary=row[3],
                hours_worked=row[4]
            )
            employees.append(emp)
        return employees

    def get_employee_by_id(self, employee_id):
        """Возвращает сотрудника по ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name, position, salary, hours_worked FROM employees WHERE id=?',
            (employee_id,)
        )
        row = cursor.fetchone()
        if row:
            return Employee(
                employee_id=row[0],
                name=row[1],
                position=row[2],
                salary=row[3],
                hours_worked=row[4]
            )
        return None

    # ==================== Операции с проектами ====================

    def add_project(self, project):
        """Добавляет новый проект."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO projects (title) VALUES (?)', (project.get_title(),))
        conn.commit()
        return cursor.lastrowid

    def update_project(self, project):
        """Обновляет данные проекта."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE projects SET title=? WHERE id=?',
                       (project.get_title(), project.get_id()))
        conn.commit()

    def delete_project(self, project_id):
        """Удаляет проект и связанные задачи."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE project_id=?', (project_id,))
        cursor.execute('DELETE FROM projects WHERE id=?', (project_id,))
        conn.commit()

    def get_all_projects(self):
        """Возвращает список всех проектов с задачами."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, title FROM projects')
        projects = []
        for row in cursor.fetchall():
            project = Project(project_id=row[0], title=row[1])
            tasks = self.get_tasks_by_project(project.get_id())
            project.set_tasks(tasks)
            projects.append(project)
        return projects

    def get_project_by_id(self, project_id):
        """Возвращает проект по ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, title FROM projects WHERE id=?', (project_id,))
        row = cursor.fetchone()
        if row:
            project = Project(project_id=row[0], title=row[1])
            tasks = self.get_tasks_by_project(project.get_id())
            project.set_tasks(tasks)
            return project
        return None

    # ==================== Операции с задачами ====================

    def add_task(self, task):
        """Добавляет новую задачу."""
        conn = self._get_connection()
        cursor = conn.cursor()
        employee = task.get_assigned_employee()
        if employee:
            employee_id = employee.get_id()
        else:
            employee_id = None
        cursor.execute('''
            INSERT INTO tasks (title, description, status, employee_id, project_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (task.get_title(), task.get_description(), task.get_status(),
              employee_id, task.get_project_id()))
        conn.commit()
        return cursor.lastrowid

    def update_task(self, task):
        """Обновляет данные задачи."""
        conn = self._get_connection()
        cursor = conn.cursor()
        employee = task.get_assigned_employee()
        if employee:
            employee_id = employee.get_id()
        else:
            employee_id = None
        cursor.execute('''
            UPDATE tasks 
            SET title=?, description=?, status=?, employee_id=?, project_id=?
            WHERE id=?
        ''', (task.get_title(), task.get_description(), task.get_status(), employee_id,
              task.get_project_id(), task.get_id()))
        conn.commit()

    def delete_task(self, task_id):
        """Удаляет задачу."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id=?', (task_id,))
        conn.commit()

    def get_tasks_by_project(self, project_id):
        """Возвращает все задачи проекта."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, description, status, employee_id, project_id 
            FROM tasks WHERE project_id=?
        ''', (project_id,))
        tasks = []
        for row in cursor.fetchall():
            if row[4]:
                employee = self.get_employee_by_id(row[4])
            else:
                employee = None
            task = Task(
                task_id=row[0],
                title=row[1],
                description=row[2],
                status=row[3],
                assigned_employee=employee,
                project_id=row[5]
            )
            tasks.append(task)
        return tasks

    def get_all_tasks(self):
        """Возвращает все задачи."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, description, status, employee_id, project_id 
            FROM tasks
        ''')
        tasks = []
        for row in cursor.fetchall():
            if row[4]:
                employee = self.get_employee_by_id(row[4])
            else:
                employee = None
            task = Task(
                task_id=row[0],
                title=row[1],
                description=row[2],
                status=row[3],
                assigned_employee=employee,
                project_id=row[5]
            )
            tasks.append(task)
        return tasks