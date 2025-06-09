import json
from datetime import datetime

from src.utils import (get_cards_data, get_currency_rates, get_greeting,
                       get_stock_prices, get_top_transactions,
                       load_transactions_from_excel, load_user_settings)


def generate_main_page_response(date_time_str):
    """Генерирует JSON-ответ для главной страницы."""
    try:
        settings = load_user_settings()  # Загружает настройки
        transactions_df = load_transactions_from_excel()  # Загружает операции

        date = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        start_date = date.replace(day=1, hour=0, minute=0, second=0)  # Первое число месяца
        end_date = date  # Текущая дата

        return {
            "greeting": get_greeting(date_time_str),
            "cards": get_cards_data(transactions_df, start_date, end_date),
            "top_transactions": get_top_transactions(transactions_df, start_date, end_date),
            "currency_rates": get_currency_rates(settings.get("user_currencies", [])),
            "stock_prices": get_stock_prices(settings.get("user_stocks", []))
        }
    except Exception as e:
        return {"error": str(e)}  # Если ошибка - возвращает её


if __name__ == "__main__":
    # Пример использования
    test_date = "2023-12-15 14:30:00"  # Тестовая дата
    response = generate_main_page_response(test_date)  # Получаем данные
    print(json.dumps(response, indent=2, ensure_ascii=False))  # Красивый вывод
