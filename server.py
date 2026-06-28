import os
import sqlite3
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

DATABASE = 'portfolio.db'

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Создание таблицы для хранения заявок
with get_db_connection() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        consent INTEGER NOT NULL
    )''')

# Обработчик для получения заявок
@app.route('/api/request', methods=['POST'])
def create_request():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    consent = data.get('consent')

    if not all([name, email, message, consent is not None]):
        return jsonify({'error': 'Все поля обязательны для заполнения.'}), 400

    with get_db_connection() as conn:
        conn.execute('INSERT INTO requests (name, email, message, consent) VALUES (?, ?, ?, ?)', (name, email, message, consent))

    # Отправка уведомления в Telegram
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    telegram_url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    telegram_message = f'Новая заявка от: {name}\nEmail: {email}\nСообщение: {message}'
    requests.post(telegram_url, data={'chat_id': telegram_chat_id, 'text': telegram_message})

    return jsonify({'message': 'Заявка успешно отправлена.'}), 201

if __name__ == '__main__':
    app.run(debug=True)