"""
Модуль с вспомогательными функциями.
Содержит функции для работы с текстом, регулярными выражениями и файлами.
"""

import re
import pandas as pd
from typing import List, Optional


def extract_emails(text: str) -> List[str]:
    """
    Извлекает email-адреса из текста.
    
    Args:
        text: Текст для поиска email-адресов.
        
    Returns:
        Список найденных email-адресов.
    """
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)


def extract_phone_numbers(text: str) -> List[str]:
    """
    Извлекает номера телефонов из текста.
    
    Args:
        text: Текст для поиска номеров телефонов.
        
    Returns:
        Список найденных номеров телефонов.
    """
    # Паттерн для российских номеров
    pattern = r'(?:\+7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'
    return re.findall(pattern, text)


def validate_email(email: str) -> bool:
    """
    Проверяет корректность email-адреса.
    
    Args:
        email: Email-адрес для проверки.
        
    Returns:
        True если email корректен, иначе False.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def read_csv_to_df(file_path: str) -> pd.DataFrame:
    """
    Читает CSV файл и возвращает DataFrame с очищенными данными.
    
    Args:
        file_path: Путь к CSV файлу.
        
    Returns:
        DataFrame с данными без пустых значений.
        
    Raises:
        FileNotFoundError: Если файл не найден.
        pd.errors.EmptyDataError: Если файл пустой.
    """
    df = pd.read_csv(file_path)
    df_cleaned = df.dropna()
    return df_cleaned


def read_csv_with_options(file_path: str, 
                          encoding: str = 'utf-8',
                          separator: str = ',',
                          drop_na: bool = True) -> pd.DataFrame:
    """
    Читает CSV файл с дополнительными параметрами.
    
    Args:
        file_path: Путь к CSV файлу.
        encoding: Кодировка файла.
        separator: Разделитель столбцов.
        drop_na: Удалять ли строки с пустыми значениями.
        
    Returns:
        DataFrame с данными.
    """
    df = pd.read_csv(file_path, encoding=encoding, sep=separator)
    if drop_na:
        df = df.dropna()
    return df


def format_currency(amount: float, currency: str = "₽") -> str:
    """
    Форматирует число как валюту.
    
    Args:
        amount: Сумма для форматирования.
        currency: Символ валюты.
        
    Returns:
        Отформатированная строка.
    """
    return f"{amount:,.2f} {currency}".replace(",", " ")


def format_hours(hours: float) -> str:
    """
    Форматирует количество часов.
    
    Args:
        hours: Количество часов.
        
    Returns:
        Отформатированная строка.
    """
    return f"{hours:.1f} ч."


def calculate_percentage(part: float, total: float) -> float:
    """
    Вычисляет процент.
    
    Args:
        part: Часть от целого.
        total: Целое значение.
        
    Returns:
        Процентное соотношение.
    """
    if total == 0:
        return 0.0
    return (part / total) * 100


def safe_float(value: str, default: float = 0.0) -> float:
    """
    Безопасно преобразует строку в float.
    
    Args:
        value: Строка для преобразования.
        default: Значение по умолчанию.
        
    Returns:
        Числовое значение или default.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Обрезает текст до указанной длины.
    
    Args:
        text: Исходный текст.
        max_length: Максимальная длина.
        
    Returns:
        Обрезанный текст с многоточием или исходный текст.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."