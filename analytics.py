"""
Модуль аналитики для анализа данных.
Содержит функции для статистического анализа и подготовки отчётов.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from models import Employee, Project, Task


class WorkAnalytics:
    """Класс для аналитики рабочих данных."""

    def __init__(self, employees: List[Employee], projects: List[Project]):
        self._employees = employees
        self._projects = projects

    def get_employees_summary(self) -> pd.DataFrame:
        """
        Возвращает сводную таблицу по сотрудникам.
        
        Returns:
            DataFrame с данными о сотрудниках.
        """
        data = []
        for emp in self._employees:
            data.append({
                'ID': emp.get_id(),
                'Имя': emp.get_name(),
                'Должность': emp.get_position(),
                'Зарплата': emp.get_salary(),
                'Часы': emp.get_hours_worked(),
                'К выплате': emp.calculate_pay()
            })
        return pd.DataFrame(data)

    def get_projects_summary(self) -> pd.DataFrame:
        """
        Возвращает сводную таблицу по проектам.
        
        Returns:
            DataFrame с данными о проектах.
        """
        data = []
        for proj in self._projects:
            tasks = proj.get_tasks()
            completed = sum(1 for t in tasks if t.is_completed())
            data.append({
                'ID': proj.get_id(),
                'Название': proj.get_title(),
                'Всего задач': len(tasks),
                'Завершено': completed,
                'Прогресс %': proj.project_progress()
            })
        return pd.DataFrame(data)

    def get_total_salary_expenses(self) -> float:
        """Возвращает общую сумму к выплате всем сотрудникам."""
        total = 0
        for emp in self._employees:
            total += emp.calculate_pay()
        return total

    def get_total_hours_worked(self) -> float:
        """Возвращает общее количество отработанных часов."""
        total = 0
        for emp in self._employees:
            total += emp.get_hours_worked()
        return total

    def get_average_salary(self) -> float:
        """Возвращает среднюю зарплату."""
        if not self._employees:
            return 0.0
        total = sum(emp.get_salary() for emp in self._employees)
        return total / len(self._employees)

    def get_overall_progress(self) -> float:
        """Возвращает общий прогресс по всем проектам."""
        if not self._projects:
            return 0.0
        total_tasks = 0
        completed_tasks = 0
        for proj in self._projects:
            tasks = proj.get_tasks()
            total_tasks += len(tasks)
            completed_tasks += sum(1 for t in tasks if t.is_completed())
        
        if total_tasks == 0:
            return 0.0
        return (completed_tasks / total_tasks) * 100

    def get_employees_by_hours(self, descending: bool = True) -> List[Employee]:
        """Возвращает сотрудников, отсортированных по часам."""
        return sorted(
            self._employees,
            key=lambda e: e.get_hours_worked(),
            reverse=descending
        )

    def get_projects_by_progress(self, descending: bool = True) -> List[Project]:
        """Возвращает проекты, отсортированные по прогрессу."""
        return sorted(
            self._projects,
            key=lambda p: p.project_progress(),
            reverse=descending
        )

    def generate_report(self) -> Dict[str, Any]:
        """
        Генерирует полный отчёт.
        
        Returns:
            Словарь с аналитическими данными.
        """
        return {
            'total_employees': len(self._employees),
            'total_projects': len(self._projects),
            'total_salary_expenses': self.get_total_salary_expenses(),
            'total_hours_worked': self.get_total_hours_worked(),
            'average_salary': self.get_average_salary(),
            'overall_progress': self.get_overall_progress(),
            'employees_summary': self.get_employees_summary().to_dict('records'),
            'projects_summary': self.get_projects_summary().to_dict('records')
        }


def analyze_csv_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Анализирует данные из CSV файла.
    
    Args:
        df: DataFrame с данными.
        
    Returns:
        Словарь с результатами анализа.
    """
    analysis = {
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_stats': {}
    }
    
    # Статистика для числовых столбцов
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        analysis['numeric_stats'][col] = {
            'mean': df[col].mean(),
            'median': df[col].median(),
            'min': df[col].min(),
            'max': df[col].max(),
            'std': df[col].std()
        }
    
    return analysis


def get_task_statistics(projects: List[Project]) -> Dict[str, Any]:
    """
    Возвращает статистику по задачам.
    
    Args:
        projects: Список проектов.
        
    Returns:
        Словарь со статистикой.
    """
    total_tasks = 0
    completed_tasks = 0
    in_progress_tasks = 0
    assigned_tasks = 0
    unassigned_tasks = 0
    
    for project in projects:
        for task in project.get_tasks():
            total_tasks += 1
            if task.is_completed():
                completed_tasks += 1
            else:
                in_progress_tasks += 1
            
            if task.get_assigned_employee():
                assigned_tasks += 1
            else:
                unassigned_tasks += 1
    
    return {
        'total': total_tasks,
        'completed': completed_tasks,
        'in_progress': in_progress_tasks,
        'assigned': assigned_tasks,
        'unassigned': unassigned_tasks,
        'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        'assignment_rate': (assigned_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }