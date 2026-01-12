"""
Главный файл приложения.
Точка входа для запуска программы учёта рабочего времени и задач.
"""

from gui import Application


def main():
    """Запускает приложение."""
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()