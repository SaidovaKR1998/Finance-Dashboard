# Стандартные библиотеки (в алфавитном порядке)
import json  # работа с JSON
import logging  # логирование
import os  # работа с файловой системой
from datetime import datetime  # работа с датами
from pathlib import Path

# Сторонние библиотеки (в алфавитном порядке)
import pandas as pd  # анализ данных
import requests  # HTTP-запросы
import yfinance as yf  # данные акций
from dotenv import load_dotenv  # загрузка .env

# Загружаем переменные окружения
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Получаем ключи из .env
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
STOCK_API_KEY = os.getenv("STOCK_API_KEY")


def get_greeting(time_str):
    """Возвращает приветствие в зависимости от времени."""
    time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").time()
    hour = time.hour

    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def load_transactions_from_excel(file_path=r"C:\Users\saido\Desktop\Saidova\python_project1\data\operations.xlsx"):
    """Загружает транзакции из Excel-файла."""
    try:
        df = pd.read_excel(file_path)  # Читаем Excel
        # Приводим дату операции к datetime
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        return df
    except FileNotFoundError:
        logging.error(f"Файл {file_path} с транзакциями не найден!")
        raise
    except Exception as e:
        logging.error(f"Ошибка при чтении файла: {str(e)}")
        raise


def get_cards_data(transactions_df, start_date, end_date):
    """Считает траты и кэшбэк по картам."""
    mask = (
            (transactions_df["Дата операции"] >= start_date) &
            (transactions_df["Дата операции"] <= end_date) &
            (transactions_df["Статус"] == "OK")
    )
    filtered_df = transactions_df[mask]  # Фильтруем по дате и статусу

    cards_data = []
    for card, group in filtered_df.groupby("Номер карты"):
        total_spent = group["Сумма платежа"].sum()
        cashback = group["Кэшбэк"].sum()
        cards_data.append({
            "last_digits": str(card).replace("*", "").strip()[-4:],  # Убираем * и берём последние 4 цифры
            "total_spent": abs(total_spent),  # Сумма трат (без минуса)
            "cashback": cashback if not pd.isna(cashback) else 0.0,
        })
    return cards_data


def get_top_transactions(transactions_df, start_date, end_date, limit=5):
    """Находит 5 самых крупных платежей."""
    mask = (
            (transactions_df["Дата операции"] >= start_date) &
            (transactions_df["Дата операции"] <= end_date) &
            (transactions_df["Статус"] == "OK")
    )
    filtered_df = transactions_df[mask]

    # Берем абсолютное значение для сортировки
    filtered_df["abs_amount"] = filtered_df["Сумма платежа"].abs()  # Модуль суммы
    top_transactions = filtered_df.nlargest(limit, "abs_amount")  # Топ-5 по сумме

    result = []
    for _, row in top_transactions.iterrows():
        result.append({
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": abs(row["Сумма платежа"]),
            "category": row["Категория"],
            "description": row["Описание"],
        })
    return result


def get_currency_rates(currencies):
    """Возвращает курсы валют через Frankfurter.app (не требует API-ключа)"""
    if not currencies:
        return []

    try:
        # Используем бесплатный API без ключа
        url = f"https://api.frankfurter.app/latest?from=USD&to={','.join(c for c in currencies if c != 'USD')}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        rates = data.get('rates', {})

        # Добавляем USD если запрошен
        if "USD" in currencies:
            rates["USD"] = 1.0

        return [{"currency": c, "rate": rates[c]} for c in currencies if c in rates]

    except Exception as e:
        logging.error(f"Currency API error: {str(e)}")
        return []


def get_stock_prices(stocks):
    """Возвращает цены акций через Yahoo Finance (не требует API-ключа)"""
    if not stocks:
        return []

    results = []
    for symbol in stocks:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")

            if not data.empty:
                price = data['Close'].iloc[-1]
                results.append({
                    "stock": symbol,
                    "price": round(float(price), 2)
                })
            else:
                logging.warning(f"No data found for {symbol}")

        except Exception as e:
            logging.error(f"Error fetching {symbol}: {str(e)}")

    return results


def load_user_settings():
    """Загружает настройки пользователя из data/user_settings.json."""
    try:
        # Определяем путь к файлу в папке data
        base_dir = Path(__file__).parent.parent  # Поднимаемся на уровень выше из src
        settings_path = base_dir / "data" / "user_settings.json"

        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        logging.warning("Файл настроек не найден, используются настройки по умолчанию")
        return {
            "user_currencies": ["USD", "EUR"],
            "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
        }
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка чтения JSON в файле настроек: {str(e)}")
        return {
            "user_currencies": ["USD", "EUR"],
            "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
        }
