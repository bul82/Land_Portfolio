#!/usr/bin/env python3
import http.server
import json
import os
import smtplib
import email.message
import urllib.parse
import urllib.request
import ssl
import sqlite3

PORT = 5050
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portfolio_feedback.db')

# Load environment variables manually from .env if it exists
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()

load_env()

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.yandex.ru')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '465'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', EMAIL_HOST_USER)
SELLER_EMAIL = os.environ.get('SELLER_EMAIL', 'bul82@yandex.ru')

def init_db():
    """Initializes SQLite database for storing leads."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT NOT NULL,
        message TEXT,
        source TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def send_telegram_notification(source, name, contact, message):
    """Sends a formatted notification to Telegram."""
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not bot_token or not chat_id:
        print("Telegram configuration is missing in .env")
        return

    # Map source keys to beautiful Russian names
    source_names = {
        'portfolio': 'Портфолио (BUL82)',
        'grooming': 'Груминг (Шерстяной Лоск)',
        'lawyer': 'Земельный Юрист',
        'mika': 'AI-ассистент Мика'
    }
    source_name = source_names.get(source, source)

    tg_text = (
        f"🔔 *Новая заявка!*\n"
        f"📍 *Источник:* {source_name}\n"
        f"👤 *Имя:* {name}\n"
        f"📞 *Контакт:* {contact}\n"
        f"📝 *Сообщение:* {message}"
    )

    tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        'chat_id': chat_id,
        'text': tg_text,
        'parse_mode': 'Markdown'
    }).encode('utf-8')

    req = urllib.request.Request(
        tg_url, 
        data=payload, 
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            pass
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")

class FeedbackHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format%args}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/feedback':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                content_type = self.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    data = json.loads(post_data.decode('utf-8'))
                else:
                    parsed = urllib.parse.parse_qs(post_data.decode('utf-8'))
                    data = {k: v[0] for k, v in parsed.items()}
                
                name = data.get('name', '').strip()
                contact = data.get('contact', '').strip()
                source = data.get('source', 'portfolio').strip()
                
                # Extract message
                message = data.get('message', '').strip()
                if not message:
                    types = data.get('types', '')
                    if isinstance(types, list):
                        types = ", ".join(types)
                    elif not types:
                        types = data.get('type', '')
                        if isinstance(types, list):
                            types = ", ".join(types)
                    if types:
                        message = f"Выбранные типы: {types}"

                if not name or not contact:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': False, 'error': 'Name and Contact are required.'}).encode('utf-8'))
                    return

                # 1. Save to SQLite
                conn = sqlite3.connect(DB_FILE)
                conn.execute(
                    'INSERT INTO leads (name, contact, message, source) VALUES (?, ?, ?, ?)',
                    (name, contact, message, source)
                )
                conn.commit()
                conn.close()

                # 2. Send Telegram Notification
                send_telegram_notification(source, name, contact, message)

                # 3. Send Email Notification (optional backup)
                if EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
                    try:
                        subject = f"Заявка с сайта [{source}] от {name}"
                        body_text = f"Имя: {name}\nКонтакт: {contact}\nИсточник: {source}\n\nСообщение:\n{message}"

                        msg = email.message.EmailMessage()
                        msg['Subject'] = subject
                        msg['From'] = EMAIL_FROM
                        msg['To'] = SELLER_EMAIL
                        msg.set_content(body_text)

                        ssl_context = ssl.create_default_context()
                        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=ssl_context, timeout=10) as server:
                            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
                            server.send_message(msg)
                    except Exception as email_err:
                        print(f"Email delivery failed: {email_err}")

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'message': 'Lead processed successfully'}).encode('utf-8'))

            except Exception as e:
                print(f"Error handling feedback: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run():
    init_db()
    server_address = ('127.0.0.1', PORT)
    httpd = http.server.HTTPServer(server_address, FeedbackHandler)
    print(f"Central Feedback API server running on port {PORT}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()

