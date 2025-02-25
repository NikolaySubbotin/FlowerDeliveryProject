
 🌸 FlowerDeliveryProject

📌 Описание проекта

FlowerDeliveryProject — это веб-приложение для заказа доставки цветов, интегрированное с Telegram-ботом, который помогает обрабатывать заказы и уведомлять пользователей о статусе их доставки.

🔹 Функционал:

Веб-сайт:

Регистрация и авторизация пользователей.

Просмотр каталога цветов и добавление в корзину.

Оформление заказа с указанием данных для доставки.

Просмотр истории заказов и повторное оформление.

Админ-панель для управления заказами.

Telegram-бот:

Получение информации о заказах через базу данных.

Уведомления о статусе заказа.

Возможность обновления статуса заказа.

🛠️ Установка и запуск

📥 1. Клонирование репозитория

 git clone https://github.com/NikolaySubbotin/FlowerDeliveryProject.git
 cd FlowerDeliveryProject

🖥️ 2. Настройка виртуального окружения

python -m venv .venv
source .venv/bin/activate  # Для Linux/Mac
.venv\Scripts\activate    # Для Windows

📦 3. Установка зависимостей

pip install -r requirements.txt

⚙️ 4. Настройка базы данных

python manage.py makemigrations
python manage.py migrate

🔑 5. Создание суперпользователя

python manage.py createsuperuser

🚀 6. Запуск сервера

python manage.py runserver

Сайт будет доступен по адресу: http://127.0.0.1:8000/

🤖 Запуск Telegram-бота

Укажите TOKEN и путь к базе данных в flower_bot/config.py:

TELEGRAM_TOKEN = "your-bot-token"
DB_PATH = "C:/zerocoder/FlowerDeliveryProject/shop_flowers/db.sqlite3"

Запустите бота:

python flower_bot/bot.py

🏗️ Структура проекта

FlowerDeliveryProject/
│── shop_flowers/        # Основное Django-приложение
│   ├── main/            # Главная страница, авторизация
│   ├── flowers/         # Каталог цветов
│   ├── shop/            # Корзина и заказы
│   ├── templates/       # HTML-шаблоны
│── flower_bot/          # Telegram-бот
│   ├── bot.py           # Основная логика бота
│   ├── queries.py       # SQL-запросы к БД
│   ├── config.py        # Конфигурация
│── db.sqlite3           # База данных
│── requirements.txt     # Зависимости проекта
│── manage.py            # Управление Django

🛠️ Тестирование

🔍 Запуск тестов Django (для сайта)

python manage.py test shop

🔍 Запуск тестов для Telegram-бота

cd flower_bot
python -m unittest tests

⚡ Дополнительно

Проект использует Django, SQLite, Aiogram (для бота).

Бот работает только с базой данных, без прямой интеграции с сайтом.

Код проекта структурирован для удобства расширения.

🔥 Спасибо за использование FlowerDeliveryProject!
