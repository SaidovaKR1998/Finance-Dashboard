import json
import re
import unittest
from typing import Dict, List, Optional
from unittest.mock import patch

import pandas as pd

# Импортируем тестируемые функции
from src.services import (create_phone_filter, filter_transactions,
                          get_mobile_transactions_json, is_mobile_transaction,
                          load_transactions_from_excel, process_transactions,
                          select_fields)

# Определяем тип Transaction как в основном модуле
Transaction = Dict[str, Optional[str]]


class TestTransactionFunctions(unittest.TestCase):
    def setUp(self):
        self.sample_transactions = [
            {'Описание': 'Покупка +7(999)123-45-67', 'Дата операции': '2023-01-01', 'Сумма операции': 100},
            {'Описание': 'Оплата 89991234567', 'Дата операции': '2023-01-02', 'Сумма операции': 200},
            {'Описание': 'Перевод 8 999 123 45 67', 'Дата операции': '2023-01-03', 'Сумма операции': 300},
            {'Описание': 'Без номера', 'Дата операции': '2023-01-04', 'Сумма операции': 400},
        ]

        self.sample_excel_data = pd.DataFrame(self.sample_transactions)
        self.phone_pattern = r'(\+7|8)[\s\(]?\d{3}[\)\s]?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}'

    @patch('pandas.read_excel')
    def test_load_transactions_from_excel(self, mock_read_excel):
        mock_read_excel.return_value = self.sample_excel_data
        result = load_transactions_from_excel('dummy.xlsx')
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0]['Описание'], 'Покупка +7(999)123-45-67')

    def test_is_mobile_transaction(self):
        pattern = re.compile(self.phone_pattern)
        self.assertTrue(is_mobile_transaction(self.sample_transactions[0], pattern))
        self.assertTrue(is_mobile_transaction(self.sample_transactions[1], pattern))
        self.assertTrue(is_mobile_transaction(self.sample_transactions[2], pattern))
        self.assertFalse(is_mobile_transaction(self.sample_transactions[3], pattern))

    def test_create_phone_filter(self):
        phone_filter = create_phone_filter(self.phone_pattern)
        self.assertTrue(phone_filter(self.sample_transactions[0]))
        self.assertFalse(phone_filter({'Описание': 'Без номера'}))

    def test_filter_transactions(self):
        phone_filter = create_phone_filter(self.phone_pattern)
        filtered = filter_transactions(self.sample_transactions, phone_filter)
        self.assertEqual(len(filtered), 3)

    def normalize_phone_numbers(transactions: List[Transaction]) -> List[Transaction]:
        """Нормализация номеров телефонов (приводит все номера к формату +7XXX...)"""

        def format_phone(desc: str) -> str:
            # Ищем номера в различных форматах
            phone_pattern = re.compile(
                r'(\+7|8)[\s\(]?(\d{3})[\)\s]?\s?(\d{3})[-\s]?(\d{2})[-\s]?(\d{2})'
            )
            # Заменяем все номера на +7XXX...
            return phone_pattern.sub(
                lambda m: f"+7{m.group(2)}{m.group(3)}{m.group(4)}{m.group(5)}",
                str(desc)
            )

        return [
            {**t, 'Описание': format_phone(t.get('Описание', ''))}
            for t in transactions
        ]

    def test_select_fields(self):
        selected = select_fields(self.sample_transactions)
        expected_fields = {'Дата операции', 'Описание', 'Сумма операции',
                           'Валюта операции', 'Категория', 'MCC'}
        for t in selected:
            self.assertTrue(set(t.keys()).issubset(expected_fields))

    @patch('pandas.read_excel')
    def test_process_transactions(self, mock_read_excel):
        mock_read_excel.return_value = self.sample_excel_data
        result = process_transactions('dummy.xlsx')
        self.assertTrue(any('+79991234567' in t['Описание'] for t in result))
        self.assertEqual(len(result), 3)

    @patch('pandas.read_excel')
    def test_get_mobile_transactions_json(self, mock_read_excel):
        mock_read_excel.return_value = self.sample_excel_data
        json_result = get_mobile_transactions_json('dummy.xlsx')
        result = json.loads(json_result)
        self.assertEqual(len(result), 3)
        self.assertTrue(all('Описание' in t for t in result))


if __name__ == '__main__':
    unittest.main()
