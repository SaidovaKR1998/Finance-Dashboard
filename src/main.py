import json
from datetime import datetime

import pandas as pd
from reports import spending_by_category
from services import get_mobile_transactions_json
from utils import (
    get_cards_data,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
    load_transactions_from_excel,
    load_user_settings,
)
from views import generate_main_page_response


def run_all_functionalities():
    """Запускает все основные функции проекта и возвращает результаты"""
    # 1. Загружаем тестовые данные
    transactions_data = {
        'Дата операции': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05'],
        'Категория': ['Еда', 'Транспорт', 'Еда', 'Еда'],
        'Сумма операции': [500, 200, 300, 400]
    }
    df = pd.DataFrame(transactions_data)

    # 2. Запускаем функциональность из reports.py
    reports_result = {
        "spending_by_category_default": spending_by_category(df, 'Еда').to_dict(),
        "spending_by_category_custom": spending_by_category(
            df, 'Еда', date='2023-04-30', report_filename='custom_report.txt'
        ).to_dict()
    }

    # 3. Запускаем функциональность из services.py
    services_result = {
        "mobile_transactions": json.loads(get_mobile_transactions_json())
    }

    # 4. Запускаем функциональность из views.py
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    views_result = generate_main_page_response(current_time)

    # 5. Запускаем отдельные функции из utils.py
    utils_result = {
        "greeting": get_greeting(current_time),
        "currency_rates": get_currency_rates(["USD", "EUR"]),
        "stock_prices": get_stock_prices(["AAPL", "GOOGL"])
    }

    return {
        "reports": reports_result,
        "services": services_result,
        "views": views_result,
        "utils": utils_result
    }


def save_results_to_file(results, filename="all_results.json"):
    """Сохраняет результаты в JSON-файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)


if __name__ == "__main__":
    print("Запуск всех функциональностей проекта...")

    try:
        # Запускаем все функции
        results = run_all_functionalities()

        # Сохраняем результаты в файл
        save_results_to_file(results)

        # Выводим краткую информацию о выполнении
        print("Успешно выполнено:")
        print(f"- Отчеты: {len(results['reports'])} функций")
        print(f"- Сервисы: {len(results['services'])} функций")
        print(f"- Веб-страница: {len(results['views'])} функций")
        print(f"- Вспомогательные функции: {len(results['utils'])} функций")
        print(f"\nПолные результаты сохранены в all_results.json")

    except Exception as e:
        print(f"Ошибка при выполнении: {str(e)}")
