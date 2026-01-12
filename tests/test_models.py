"""
Модуль с юнит-тестами для моделей данных.
"""

import unittest
import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Employee, Task, Project
from utils import extract_emails, validate_email, format_currency, safe_float


class TestEmployee(unittest.TestCase):
    """Тесты для класса Employee."""

    def setUp(self):
        """Подготовка данных для тестов."""
        self.employee = Employee(
            name="Иван Иванов",
            position="Разработчик",
            salary=100000,
            hours_worked=0,
            employee_id=1
        )

    def test_employee_creation(self):
        """Тест создания сотрудника."""
        self.assertEqual(self.employee.get_name(), "Иван Иванов")
        self.assertEqual(self.employee.get_position(), "Разработчик")
        self.assertEqual(self.employee.get_salary(), 100000)
        self.assertEqual(self.employee.get_hours_worked(), 0)
        self.assertEqual(self.employee.get_id(), 1)

    def test_set_name_valid(self):
        """Тест установки валидного имени."""
        self.employee.set_name("Петр Петров")
        self.assertEqual(self.employee.get_name(), "Петр Петров")

    def test_set_name_empty_raises_error(self):
        """Тест: пустое имя вызывает ошибку."""
        with self.assertRaises(ValueError):
            self.employee.set_name("")

    def test_set_name_whitespace_raises_error(self):
        """Тест: имя из пробелов вызывает ошибку."""
        with self.assertRaises(ValueError):
            self.employee.set_name("   ")

    def test_set_salary_valid(self):
        """Тест установки валидной зарплаты."""
        self.employee.set_salary(150000)
        self.assertEqual(self.employee.get_salary(), 150000)

    def test_set_salary_negative_raises_error(self):
        """Тест: отрицательная зарплата вызывает ошибку."""
        with self.assertRaises(ValueError):
            self.employee.set_salary(-1000)

    def test_add_hours_valid(self):
        """Тест добавления валидных часов."""
        self.employee.add_hours(8)
        self.assertEqual(self.employee.get_hours_worked(), 8)
        self.employee.add_hours(4)
        self.assertEqual(self.employee.get_hours_worked(), 12)

    def test_add_hours_negative_raises_error(self):
        """Тест: отрицательные часы вызывают ошибку."""
        with self.assertRaises(ValueError):
            self.employee.add_hours(-5)

    def test_calculate_pay(self):
        """Тест расчёта оплаты."""
        self.employee.add_hours(176)
        pay = self.employee.calculate_pay()
        self.assertEqual(pay, 100000)

    def test_calculate_pay_partial(self):
        """Тест расчёта частичной оплаты."""
        self.employee.add_hours(88)
        pay = self.employee.calculate_pay()
        self.assertEqual(pay, 50000)

    def test_calculate_pay_zero_hours(self):
        """Тест расчёта оплаты при нуле часов."""
        pay = self.employee.calculate_pay()
        self.assertEqual(pay, 0)

    def test_to_dict(self):
        """Тест преобразования в словарь."""
        result = self.employee.to_dict()
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['name'], "Иван Иванов")
        self.assertEqual(result['position'], "Разработчик")
        self.assertEqual(result['salary'], 100000)
        self.assertEqual(result['hours_worked'], 0)

    def test_str_representation(self):
        """Тест строкового представления."""
        result = str(self.employee)
        self.assertIn("Иван Иванов", result)
        self.assertIn("Разработчик", result)


class TestTask(unittest.TestCase):
    """Тесты для класса Task."""

    def setUp(self):
        """Подготовка данных для тестов."""
        self.task = Task(
            title="Разработка модуля",
            description="Описание задачи",
            status="В процессе",
            task_id=1,
            project_id=1
        )

    def test_task_creation(self):
        """Тест создания задачи."""
        self.assertEqual(self.task.get_title(), "Разработка модуля")
        self.assertEqual(self.task.get_description(), "Описание задачи")
        self.assertEqual(self.task.get_status(), "В процессе")
        self.assertEqual(self.task.get_id(), 1)
        self.assertEqual(self.task.get_project_id(), 1)

    def test_set_title_valid(self):
        """Тест установки валидного названия."""
        self.task.set_title("Новое название")
        self.assertEqual(self.task.get_title(), "Новое название")

    def test_set_title_empty_raises_error(self):
        """Тест: пустое название вызывает ошибку."""
        with self.assertRaises(ValueError):
            self.task.set_title("")

    def test_mark_complete(self):
        """Тест завершения задачи."""
        self.assertEqual(self.task.get_status(), "В процессе")
        self.task.mark_complete()
        self.assertEqual(self.task.get_status(), "Завершено")

    def test_is_completed(self):
        """Тест проверки завершённости."""
        self.assertFalse(self.task.is_completed())
        self.task.mark_complete()
        self.assertTrue(self.task.is_completed())

    def test_assign_employee(self):
        """Тест назначения сотрудника."""
        employee = Employee(name="Тест", position="Тест", salary=50000)
        self.task.assign_employee(employee)
        self.assertEqual(self.task.get_assigned_employee(), employee)

    def test_default_status(self):
        """Тест статуса по умолчанию."""
        task = Task(title="Тест", description="")
        self.assertEqual(task.get_status(), "В процессе")

    def test_to_dict(self):
        """Тест преобразования в словарь."""
        result = self.task.to_dict()
        self.assertEqual(result['title'], "Разработка модуля")
        self.assertEqual(result['status'], "В процессе")

    def test_str_representation(self):
        """Тест строкового представления."""
        result = str(self.task)
        self.assertIn("Разработка модуля", result)
        self.assertIn("В процессе", result)


class TestProject(unittest.TestCase):
    """Тесты для класса Project."""

    def setUp(self):
        """Подготовка данных для тестов."""
        self.project = Project(title="Тестовый проект", project_id=1)

    def test_project_creation(self):
        """Тест создания проекта."""
        self.assertEqual(self.project.get_title(), "Тестовый проект")
        self.assertEqual(self.project.get_id(), 1)
        self.assertEqual(len(self.project.get_tasks()), 0)

    def test_set_title_valid(self):
        """Тест установки валидного названия."""
        self.project.set_title("Новый проект")
        self.assertEqual(self.project.get_title(), "Новый проект")

    def test_set_title_empty_raises_error(self):
        """Тест: пустое название вызывает ошибку."""
        with self.assertRaises(ValueError):
            self.project.set_title("")

    def test_add_task(self):
        """Тест добавления задачи."""
        task = Task(title="Задача 1", description="")
        self.project.add_task(task)
        self.assertEqual(len(self.project.get_tasks()), 1)

    def test_remove_task(self):
        """Тест удаления задачи."""
        task = Task(title="Задача 1", description="")
        self.project.add_task(task)
        self.project.remove_task(task)
        self.assertEqual(len(self.project.get_tasks()), 0)

    def test_project_progress_empty(self):
        """Тест прогресса пустого проекта."""
        progress = self.project.project_progress()
        self.assertEqual(progress, 0.0)

    def test_project_progress_no_completed(self):
        """Тест прогресса без завершённых задач."""
        self.project.add_task(Task(title="Задача 1", description=""))
        self.project.add_task(Task(title="Задача 2", description=""))
        progress = self.project.project_progress()
        self.assertEqual(progress, 0.0)

    def test_project_progress_all_completed(self):
        """Тест прогресса с завершёнными задачами."""
        task1 = Task(title="Задача 1", description="")
        task2 = Task(title="Задача 2", description="")
        task1.mark_complete()
        task2.mark_complete()
        self.project.add_task(task1)
        self.project.add_task(task2)
        progress = self.project.project_progress()
        self.assertEqual(progress, 100.0)

    def test_project_progress_partial(self):
        """Тест частичного прогресса."""
        task1 = Task(title="Задача 1", description="")
        task2 = Task(title="Задача 2", description="")
        task1.mark_complete()
        self.project.add_task(task1)
        self.project.add_task(task2)
        progress = self.project.project_progress()
        self.assertEqual(progress, 50.0)

    def test_get_completed_tasks_count(self):
        """Тест подсчёта завершённых задач."""
        task1 = Task(title="Задача 1", description="")
        task2 = Task(title="Задача 2", description="")
        task1.mark_complete()
        self.project.add_task(task1)
        self.project.add_task(task2)
        count = self.project.get_completed_tasks_count()
        self.assertEqual(count, 1)

    def test_to_dict(self):
        """Тест преобразования в словарь."""
        result = self.project.to_dict()
        self.assertEqual(result['title'], "Тестовый проект")
        self.assertEqual(result['tasks_count'], 0)


class TestUtils(unittest.TestCase):
    """Тесты для вспомогательных функций."""

    def test_extract_emails_single(self):
        """Тест извлечения одного email."""
        text = "Контакт: test@example.com"
        emails = extract_emails(text)
        self.assertEqual(emails, ["test@example.com"])

    def test_extract_emails_multiple(self):
        """Тест извлечения нескольких email."""
        text = "Напишите на user@mail.ru или admin@test.org"
        emails = extract_emails(text)
        self.assertEqual(len(emails), 2)
        self.assertIn("user@mail.ru", emails)
        self.assertIn("admin@test.org", emails)

    def test_extract_emails_none(self):
        """Тест текста без email."""
        text = "Здесь нет email адресов"
        emails = extract_emails(text)
        self.assertEqual(emails, [])

    def test_extract_emails_with_special_chars(self):
        """Тест email со спецсимволами."""
        text = "Email: user.name+tag@example.co.uk"
        emails = extract_emails(text)
        self.assertEqual(len(emails), 1)

    def test_validate_email_valid(self):
        """Тест валидации корректного email."""
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name@mail.ru"))

    def test_validate_email_invalid(self):
        """Тест валидации некорректного email."""
        self.assertFalse(validate_email("invalid"))
        self.assertFalse(validate_email("@example.com"))
        self.assertFalse(validate_email("test@"))

    def test_format_currency(self):
        """Тест форматирования валюты."""
        result = format_currency(1000.50)
        self.assertIn("1", result)
        self.assertIn("000", result)
        self.assertIn("₽", result)

    def test_format_currency_custom_symbol(self):
        """Тест форматирования с другим символом."""
        result = format_currency(100, "$")
        self.assertIn("$", result)

    def test_safe_float_valid(self):
        """Тест безопасного преобразования в float."""
        self.assertEqual(safe_float("123.45"), 123.45)
        self.assertEqual(safe_float("100"), 100.0)

    def test_safe_float_invalid(self):
        """Тест безопасного преобразования невалидных данных."""
        self.assertEqual(safe_float("abc"), 0.0)
        self.assertEqual(safe_float(""), 0.0)
        self.assertEqual(safe_float(None), 0.0)

    def test_safe_float_default(self):
        """Тест безопасного преобразования с дефолтным значением."""
        self.assertEqual(safe_float("abc", -1.0), -1.0)


if __name__ == "__main__":
    unittest.main()