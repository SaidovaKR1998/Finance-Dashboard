import json
import re
from functools import partial
from pathlib import Path
from typing import Callable, Dict, List, Optional

import pandas as pd

# Типы для аннотаций
Transaction = Dict[str, Optional[str]]
PhoneFilterFunc = Callable[[Transaction], bool]


def load_transactions_from_excel(filepath: str = None) -> List[Transaction]:
    """Загрузка транзакций из Excel файла с обработкой"""
    # Если путь не указан, используем data/operations.xlsx в корне проекта
    if filepath is None:
        base_dir = Path(__file__).parent.parent  # Поднимаемся на уровень выше из src
        filepath = str(base_dir / "data" / "operations.xlsx")

    try:
        df = pd.read_excel(filepath)
        return df.where(pd.notnull(df), None).to_dict('records')
    except FileNotFoundError:
        raise ValueError(f"Файл не найден по пути: {filepath}")
    except Exception as e:
        raise ValueError(f"Ошибка загрузки файла: {str(e)}")


def is_mobile_transaction(transaction: Transaction, pattern: re.Pattern) -> bool:
    """Проверяет, содержит ли описание транзакции мобильный номер"""
    description = transaction.get('Описание', '')
    return bool(pattern.search(str(description)))


def create_phone_filter(pattern: str) -> PhoneFilterFunc:
    """Фабрика функций для фильтрации по номеру телефона"""
    compiled_pattern = re.compile(pattern)
    return partial(is_mobile_transaction, pattern=compiled_pattern)


def filter_transactions(transactions: List[Transaction],
                        predicate: PhoneFilterFunc) -> List[Transaction]:
    """Фильтрация транзакций с использованием переданного предиката"""
    return list(filter(predicate, transactions))


def normalize_phone_numbers(transactions: List[Transaction]) -> List[Transaction]:
    """Нормализация номеров телефонов в описании"""

    def format_phone(desc: str) -> str:
        phone_pattern = re.compile(
            r'(\+7\s?[\(\s]?\d{3}[\)\s]?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2})'
        )
        return phone_pattern.sub(
            lambda m: re.sub(r'[\s\(\)-]', '', m.group()),
            str(desc)
        )

    return [
        {**t, 'Описание': format_phone(t.get('Описание', ''))}
        for t in transactions
    ]


def select_fields(transactions: List[Transaction]) -> List[Transaction]:
    """Выбор нужных полей для вывода"""
    fields = [
        'Дата операции',
        'Описание',
        'Сумма операции',
        'Валюта операции',
        'Категория',
        'MCC'
    ]
    return [
        {k: v for k, v in t.items() if k in fields}
        for t in transactions
    ]


def process_transactions(filepath: str = None) -> List[Transaction]:
    """Обработка транзакций: загрузка, фильтрация, нормализация"""
    phone_pattern = (
        r'(\+7|8)[\s\(]?\d{3}[\)\s]?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}'
    )

    transactions = load_transactions_from_excel(filepath)
    phone_filter = create_phone_filter(phone_pattern)
    filtered = filter_transactions(transactions, phone_filter)
    normalized = normalize_phone_numbers(filtered)
    return select_fields(normalized)


def get_mobile_transactions_json(filepath: str = None) -> str:
    """Основная функция сервиса - возвращает JSON с мобильными транзакциями"""
    try:
        transactions = process_transactions(filepath)
        return json.dumps(
            transactions,
            ensure_ascii=False,
            indent=2,
            default=str
        )
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    # Пример использования
    print(get_mobile_transactions_json())
