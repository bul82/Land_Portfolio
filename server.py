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

# Создание таблицы, если она не существует
with get_db_connection() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        consent BOOLEAN NOT NULL
    )''')

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    consent = data.get('consent')

    if not all([name, email, message, consent is not None]):
        return jsonify({'error': 'Все поля обязательны для заполнения.'}), 400

    with get_db_connection() as conn:
        conn.execute('INSERT INTO feedback (name, email, message, consent) VALUES (?, ?, ?, ?)',
                     (name, email, message, consent))

    # Отправка уведомления в Telegram
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    telegram_message = f'Новое сообщение от {name}: {message}'
    requests.post(f'https://api.telegram.org/bot{telegram_token}/sendMessage',
                  data={'chat_id': telegram_chat_id, 'text': telegram_message})

    return jsonify({'message': 'Ваше сообщение отправлено!'}), 201

if __name__ == '__main__':
    app.run(debug=True)