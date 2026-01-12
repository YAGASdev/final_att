"""
Модуль с классами моделей данных.
Содержит классы Employee, Task, Project.
"""


class Employee:
    """Класс для представления сотрудника."""

    def __init__(self, name, position, salary, hours_worked=0, employee_id=None):
        self._id = employee_id
        self._name = name
        self._position = position
        self._salary = salary
        self._hours_worked = hours_worked

    # Геттеры
    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_position(self):
        return self._position

    def get_salary(self):
        return self._salary

    def get_hours_worked(self):
        return self._hours_worked

    # Сеттеры
    def set_id(self, value):
        self._id = value

    def set_name(self, value):
        if not value.strip():
            raise ValueError("Имя не может быть пустым")
        self._name = value

    def set_position(self, value):
        self._position = value

    def set_salary(self, value):
        if value < 0:
            raise ValueError("Зарплата не может быть отрицательной")
        self._salary = value

    def add_hours(self, hours):
        if hours < 0:
            raise ValueError("Часы не могут быть отрицательными")
        self._hours_worked = self._hours_worked + hours

    def calculate_pay(self):
        """Рассчитывает оплату на основе отработанных часов."""
        hourly_rate = self._salary / 176
        return self._hours_worked * hourly_rate

    def to_dict(self):
        """Преобразует объект в словарь."""
        return {
            'id': self._id,
            'name': self._name,
            'position': self._position,
            'salary': self._salary,
            'hours_worked': self._hours_worked
        }

    def __str__(self):
        return self._name + " (" + self._position + ")"

    def __repr__(self):
        return f"Employee(name='{self._name}', position='{self._position}')"


class Task:
    """Класс для представления задачи."""
    
    STATUSES = ("В процессе", "Завершено")

    def __init__(self, title, description, status="В процессе",
                 assigned_employee=None, task_id=None, project_id=None):
        self._id = task_id
        self._title = title
        self._description = description
        self._status = status
        self._assigned_employee = assigned_employee
        self._project_id = project_id

    # Геттеры
    def get_id(self):
        return self._id

    def get_title(self):
        return self._title

    def get_description(self):
        return self._description

    def get_status(self):
        return self._status

    def get_assigned_employee(self):
        return self._assigned_employee

    def get_project_id(self):
        return self._project_id

    # Сеттеры
    def set_id(self, value):
        self._id = value

    def set_title(self, value):
        if not value.strip():
            raise ValueError("Название задачи не может быть пустым")
        self._title = value

    def set_description(self, value):
        self._description = value

    def set_project_id(self, value):
        self._project_id = value

    def assign_employee(self, employee):
        self._assigned_employee = employee

    def mark_complete(self):
        self._status = "Завершено"

    def is_completed(self):
        return self._status == "Завершено"

    def to_dict(self):
        """Преобразует объект в словарь."""
        return {
            'id': self._id,
            'title': self._title,
            'description': self._description,
            'status': self._status,
            'project_id': self._project_id,
            'employee_id': self._assigned_employee.get_id() if self._assigned_employee else None
        }

    def __str__(self):
        return self._title + " [" + self._status + "]"

    def __repr__(self):
        return f"Task(title='{self._title}', status='{self._status}')"


class Project:
    """Класс для представления проекта."""

    def __init__(self, title, project_id=None):
        self._id = project_id
        self._title = title
        self._tasks = []

    # Геттеры
    def get_id(self):
        return self._id

    def get_title(self):
        return self._title

    def get_tasks(self):
        return list(self._tasks)

    # Сеттеры
    def set_id(self, value):
        self._id = value

    def set_title(self, value):
        if not value.strip():
            raise ValueError("Название проекта не может быть пустым")
        self._title = value

    def set_tasks(self, tasks):
        self._tasks = tasks

    def add_task(self, task):
        self._tasks.append(task)

    def remove_task(self, task):
        if task in self._tasks:
            self._tasks.remove(task)

    def project_progress(self):
        """Вычисляет прогресс проекта в процентах."""
        if len(self._tasks) == 0:
            return 0.0
        completed = 0
        for task in self._tasks:
            if task.get_status() == "Завершено":
                completed = completed + 1
        return (completed / len(self._tasks)) * 100

    def get_completed_tasks_count(self):
        """Возвращает количество завершённых задач."""
        count = 0
        for task in self._tasks:
            if task.is_completed():
                count += 1
        return count

    def to_dict(self):
        """Преобразует объект в словарь."""
        return {
            'id': self._id,
            'title': self._title,
            'tasks_count': len(self._tasks),
            'progress': self.project_progress()
        }

    def __str__(self):
        progress = self.project_progress()
        return self._title + " (" + str(round(progress, 1)) + "% завершено)"

    def __repr__(self):
        return f"Project(title='{self._title}')"