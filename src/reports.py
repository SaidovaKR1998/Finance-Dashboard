import functools
import os
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd


def report_to_file(default_filename: str = None):
    """
    Декоратор для сохранения результатов отчета в файл

    Args:
        default_filename: Шаблон имени файла по умолчанию
                         Может содержать {timestamp} и {func_name}
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Получаем результат работы функции
            result = func(*args, **kwargs)

            # Определяем имя файла
            filename = kwargs.get('report_filename')
            if filename is None:
                if default_filename is None:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{func.__name__}_report_{timestamp}.txt"
                else:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = default_filename.format(
                        timestamp=timestamp,
                        func_name=func.__name__
                    )

            # Создаем директорию для отчетов, если ее нет
            os.makedirs('reports', exist_ok=True)
            filepath = os.path.join('reports', filename)

            # Сохраняем результат в файл
            with open(filepath, 'w', encoding='utf-8') as f:
                if isinstance(result, pd.DataFrame):
                    f.write(result.to_string())
                else:
                    f.write(str(result))

            return result

        return wrapper

    # Если декоратор вызван с параметром
    if callable(default_filename):
        func = default_filename
        default_filename = None
        return decorator(func)

    return decorator


@report_to_file(default_filename="{func_name}_{timestamp}.txt")
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None,
                         **kwargs) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние 3 месяца

    Args:
        transactions: Датафрейм с транзакциями
        category: Название категории для фильтрации
        date: Дата, от которой отсчитываем 3 месяца (формат YYYY-MM-DD)
        **kwargs: Дополнительные аргументы (включая report_filename)

    Returns:
        pd.DataFrame: Отфильтрованный датафрейм с транзакциями
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    # Преобразуем дату в datetime
    end_date = pd.to_datetime(date)
    start_date = end_date - timedelta(days=90)

    # Фильтруем транзакции
    filtered = transactions[
        (transactions['Категория'] == category) &
        (pd.to_datetime(transactions['Дата операции']) >= start_date) &
        (pd.to_datetime(transactions['Дата операции']) <= end_date)
        ]

    return filtered.sort_values('Дата операции', ascending=False)


# Пример данных
data = {
    'Дата операции': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05'],
    'Категория': ['Еда', 'Транспорт', 'Еда', 'Еда'],
    'Сумма операции': [500, 200, 300, 400]
}
df = pd.DataFrame(data)

# Базовый вариант с именем файла по умолчанию
result1 = spending_by_category(df, 'Еда')
# С указанием имя файла
result2 = spending_by_category(df, 'Еда', report_filename='food_report.txt')
# С указанием даты
result3 = spending_by_category(df, 'Еда', date='2023-03-31', report_filename='q1_food.txt')
# P.S Когда я вызываю функцию без параметра date, она использует текущую дату
# (2025-06-10) и ищет транзакции за период с 2025-03-12 по 2025-06-10 (90 дней назад от текущей даты).
# Тестовые данные за 2023 год не попадают в этот диапазон, поэтому возвращается пустой DataFram
