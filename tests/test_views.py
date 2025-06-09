import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Импорт тестируемой функции
from src.views import generate_main_page_response

# Настройка путей
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestGenerateMainPageResponse(unittest.TestCase):
    @patch('src.views.load_user_settings')
    @patch('src.views.load_transactions_from_excel')
    @patch('src.views.get_greeting')
    @patch('src.views.get_cards_data')
    @patch('src.views.get_top_transactions')
    @patch('src.views.get_currency_rates')
    @patch('src.views.get_stock_prices')
    def test_successful_response(
            self,
            mock_stock_prices,
            mock_currency_rates,
            mock_top_transactions,
            mock_cards_data,
            mock_greeting,
            mock_load_transactions,
            mock_load_settings
    ):
        """Тест успешного формирования ответа."""
        # Настраиваем моки
        mock_load_settings.return_value = {
            "user_currencies": ["USD", "EUR"],
            "user_stocks": ["AAPL", "GOOGL"]
        }
        mock_load_transactions.return_value = MagicMock()
        mock_greeting.return_value = "Добрый день"
        mock_cards_data.return_value = [{"card": "data"}]
        mock_top_transactions.return_value = [{"transaction": "data"}]
        mock_currency_rates.return_value = {"USD": 75.5, "EUR": 85.3}
        mock_stock_prices.return_value = {"AAPL": 150.2, "GOOGL": 2800.1}

        # Вызываем функцию
        date_str = "2023-12-15 14:30:00"
        result = generate_main_page_response(date_str)

        # Проверяем результат
        self.assertEqual(result, {
            "greeting": "Добрый день",
            "cards": [{"card": "data"}],
            "top_transactions": [{"transaction": "data"}],
            "currency_rates": {"USD": 75.5, "EUR": 85.3},
            "stock_prices": {"AAPL": 150.2, "GOOGL": 2800.1}
        })

    def test_invalid_date_format(self):
        """Тест обработки неверного формата даты."""
        with patch('src.views.load_user_settings'):
            result = generate_main_page_response("invalid-date-format")
            self.assertIn("error", result)
            self.assertIn("time data 'invalid-date-format'", result["error"])

    @patch('src.views.load_user_settings')
    def test_error_in_settings_loading(self, mock_load_settings):
        """Тест обработки ошибки при загрузке настроек."""
        mock_load_settings.side_effect = Exception("Settings error")

        result = generate_main_page_response("2023-12-15 14:30:00")
        self.assertEqual(result, {"error": "Settings error"})

    @patch('src.views.load_user_settings')
    @patch('src.views.load_transactions_from_excel')
    def test_error_in_transactions_loading(self, mock_load_transactions, mock_load_settings):
        """Тест обработки ошибки при загрузке транзакций."""
        mock_load_settings.return_value = {}
        mock_load_transactions.side_effect = Exception("Transactions error")

        result = generate_main_page_response("2023-12-15 14:30:00")
        self.assertEqual(result, {"error": "Transactions error"})

    @patch('src.views.load_user_settings')
    @patch('src.views.load_transactions_from_excel')
    @patch('src.views.get_greeting')
    def test_partial_error_in_response_generation(self, mock_greeting, mock_load_transactions, mock_load_settings):
        """Тест частичной ошибки."""
        mock_load_settings.return_value = {}
        mock_load_transactions.return_value = MagicMock()
        mock_greeting.side_effect = Exception("Greeting error")

        result = generate_main_page_response("2023-12-15 14:30:00")
        self.assertEqual(result, {"error": "Greeting error"})

    @patch('src.views.load_user_settings')
    @patch('src.views.load_transactions_from_excel')
    @patch('src.views.get_greeting')
    @patch('src.views.get_cards_data')
    @patch('src.views.get_top_transactions')
    @patch('src.views.get_currency_rates')
    @patch('src.views.get_stock_prices')
    def test_empty_data_response(
            self,
            mock_stock_prices,
            mock_currency_rates,
            mock_top_transactions,
            mock_cards_data,
            mock_greeting,
            mock_load_transactions,
            mock_load_settings
    ):
        """Тест с пустыми данными."""
        mock_load_settings.return_value = {}
        mock_load_transactions.return_value = MagicMock()
        mock_greeting.return_value = "Добрый день"
        mock_cards_data.return_value = []
        mock_top_transactions.return_value = []
        mock_currency_rates.return_value = {}
        mock_stock_prices.return_value = {}

        result = generate_main_page_response("2023-12-15 14:30:00")

        self.assertEqual(result["greeting"], "Добрый день")
        self.assertEqual(result["cards"], [])
        self.assertEqual(result["top_transactions"], [])
        self.assertEqual(result["currency_rates"], {})
        self.assertEqual(result["stock_prices"], {})


if __name__ == '__main__':
    unittest.main()
