import os
import sys
import unittest
import warnings
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd

from src import utils

# Добавляем путь к src в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFinanceUtils(unittest.TestCase):
    """Тесты для utils.py"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.test_transactions = pd.DataFrame([
            {
                "Дата операции": "01.12.2023 10:00:00",
                "Номер карты": "****1234",
                "Сумма платежа": -1000,
                "Статус": "OK",
                "Категория": "Кафе",
                "Описание": "Starbucks",
                "Кэшбэк": 10.0
            },
            {
                "Дата операции": "15.12.2023 15:30:00",
                "Номер карты": "****5678",
                "Сумма платежа": -5000,
                "Статус": "OK",
                "Категория": "Магазин",
                "Описание": "Amazon",
                "Кэшбэк": 50.0
            },
            {
                "Дата операции": "20.12.2023 20:00:00",
                "Номер карты": "****1234",
                "Сумма платежа": -2000,
                "Статус": "FAILED",
                "Категория": "Такси",
                "Описание": "Uber",
                "Кэшбэк": 0.0
            }
        ])
        self.test_transactions["Дата операции"] = pd.to_datetime(
            self.test_transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S"
        )

        # Подавляем SettingWithCopyWarning
        warnings.simplefilter(action="ignore", category=pd.errors.SettingWithCopyWarning)

    def test_get_greeting(self):
        """Тест функции get_greeting"""
        self.assertEqual(utils.get_greeting("2023-12-15 08:00:00"), "Доброе утро")
        self.assertEqual(utils.get_greeting("2023-12-15 13:00:00"), "Добрый день")
        self.assertEqual(utils.get_greeting("2023-12-15 20:00:00"), "Добрый вечер")
        self.assertEqual(utils.get_greeting("2023-12-15 02:00:00"), "Доброй ночи")

    @patch('logging.error')
    def test_load_transactions_from_excel_file_not_found(self, mock_logging):
        """Тест обработки отсутствующего файла"""
        with self.assertRaises(FileNotFoundError):
            utils.load_transactions_from_excel("nonexistent_file.xlsx")
        mock_logging.assert_called()

    @patch('pandas.read_excel')
    def test_load_transactions_from_excel_success(self, mock_read_excel):
        """Тест успешной загрузки транзакций"""
        mock_read_excel.return_value = self.test_transactions
        result = utils.load_transactions_from_excel("test.xlsx")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)

    def test_get_cards_data(self):
        """Тест расчета данных по картам"""
        start_date = datetime(2023, 12, 1)
        end_date = datetime(2023, 12, 31)
        result = utils.get_cards_data(self.test_transactions, start_date, end_date)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["last_digits"], "1234")
        self.assertEqual(result[0]["total_spent"], 1000)
        self.assertEqual(result[1]["total_spent"], 5000)

    def test_get_top_transactions(self):
        """Тест поиска топовых транзакций"""
        start_date = datetime(2023, 12, 1)
        end_date = datetime(2023, 12, 31)
        result = utils.get_top_transactions(self.test_transactions, start_date, end_date)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["amount"], 5000)
        self.assertEqual(result[0]["category"], "Магазин")

    @patch('requests.get')
    def test_get_currency_rates_success(self, mock_get):
        """Тест получения курсов валют (мок)"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "rates": {"EUR": 0.92, "GBP": 0.79},
            "base": "USD"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = utils.get_currency_rates(["USD", "EUR", "GBP"])
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["currency"], "USD")
        self.assertEqual(result[0]["rate"], 1.0)
        self.assertEqual(result[1]["rate"], 0.92)

    def test_get_currency_rates_empty(self):
        """Тест пустого запроса валют"""
        result = utils.get_currency_rates([])
        self.assertEqual(len(result), 0)

    @patch('yfinance.Ticker')
    def test_get_stock_prices_success(self, mock_ticker):
        """Тест получения цен акций (мок)"""
        mock_data = MagicMock()
        mock_data.history.return_value = pd.DataFrame({
            "Close": [150.0]
        }, index=[0])

        mock_ticker.return_value = mock_data

        result = utils.get_stock_prices(["AAPL"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["stock"], "AAPL")
        self.assertEqual(result[0]["price"], 150.0)

    @patch('logging.warning')
    def test_load_user_settings_default(self, mock_warning):
        """Тест загрузки настроек по умолчанию"""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = utils.load_user_settings()
            self.assertEqual(result["user_currencies"], ["USD", "EUR"])
            self.assertEqual(len(result["user_stocks"]), 5)
            mock_warning.assert_called_with("Файл настроек не найден, используются настройки по умолчанию")


if __name__ == "__main__":
    unittest.main()
