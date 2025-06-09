import os
import unittest

import pandas as pd

from src.reports import spending_by_category


class TestSpendingByCategory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые данные один раз для всех тестов"""
        cls.test_data = pd.DataFrame({
            'Дата операции': ['2023-03-15', '2023-04-20', '2023-05-10', '2023-06-05', '2023-02-01'],
            'Категория': ['Еда', 'Транспорт', 'Еда', 'Еда', 'Развлечения'],
            'Сумма операции': [500, 200, 300, 400, 1000]
        })

        # Создаем все необходимые директории
        os.makedirs('test_reports', exist_ok=True)
        os.makedirs('reports', exist_ok=True)

    def setUp(self):
        """Очищаем директории перед каждым тестом"""
        for dir_path in ['test_reports', 'reports']:
            for file in os.listdir(dir_path):
                os.remove(os.path.join(dir_path, file))

    def test_basic_functionality(self):
        """Тест базовой функциональности"""
        result = spending_by_category(self.test_data, 'Еда', date='2023-06-30')
        self.assertEqual(len(result), 2)
        self.assertEqual(result['Сумма операции'].sum(), 700)  # 300 + 400

    def test_date_filter(self):
        """Тест фильтрации по дате"""
        result = spending_by_category(self.test_data, 'Еда', date='2023-05-31')
        self.assertEqual(len(result), 2)

    def test_empty_result(self):
        """Тест случая, когда нет подходящих транзакций"""
        result = spending_by_category(self.test_data, 'Несуществующая категория', date='2023-06-30')
        self.assertTrue(result.empty)

    def test_default_filename_generation(self):
        """Тест генерации имени файла по умолчанию"""
        spending_by_category(self.test_data, 'Еда', date='2023-06-30')
        files = os.listdir('reports')
        self.assertTrue(any(f.startswith('spending_by_category_') and f.endswith('.txt') for f in files))

    def test_custom_filename(self):
        """Тест указания кастомного имени файла"""
        custom_name = os.path.abspath(os.path.join('test_reports', 'custom_report.txt'))
        os.makedirs(os.path.dirname(custom_name), exist_ok=True)

        spending_by_category(
            self.test_data,
            'Еда',
            date='2023-06-30',
            report_filename=custom_name
        )
        self.assertTrue(os.path.exists(custom_name))


if __name__ == '__main__':
    unittest.main()
