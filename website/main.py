# main.py
from fastapi import FastAPI, Form, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
import html
from typing import Optional
import os

app = FastAPI(title="Уязвимый сайт (для демонстрации)")

# Подключаем шаблоны
templates = Jinja2Templates(directory="templates")

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    
    # Создаем таблицу пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    ''')
    
    # Создаем таблицу сообщений/комментариев
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Добавляем тестовые данные, если таблица пуста
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            [
                ('admin', 'admin123', 'admin@example.com'),
                ('alice', 'password123', 'alice@example.com'),
                ('bob', 'qwerty', 'bob@example.com'),
                ('eve', '123456', 'eve@example.com')
            ]
        )
    
    # Добавляем тестовые сообщения
    cursor.execute("SELECT COUNT(*) FROM messages")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO messages (user_id, content) VALUES (?, ?)",
            [
                (1, 'Привет всем! Это тестовое сообщение.'),
                (2, 'Не забывайте обновлять пароли!'),
                (3, 'Пример XSS-атаки: <script>alert("XSS")</script>'),
                (4, 'Пример комментария с <b>HTML</b> тегами.')
            ]
        )
    
    conn.commit()
    conn.close()

# Инициализируем БД при запуске
init_db()

# Функция для получения подключения к БД
def get_db():
    conn = sqlite3.connect('vulnerable.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница с формой поиска (уязвима к SQL-инъекциям)"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
async def search_users(
    request: Request, 
    query: str = Query("", description="Поиск пользователей")
):
    """
    Страница поиска пользователей с SQL-инъекцией.
    Уязвимость: прямое включение пользовательского ввода в SQL-запрос.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # УЯЗВИМЫЙ КОД: прямое использование пользовательского ввода в SQL-запросе
    sql = f"SELECT * FROM users WHERE username LIKE '%{query}%' OR email LIKE '%{query}%'"
    
    try:
        cursor.execute(sql)
        users = cursor.fetchall()
    except Exception as e:
        users = []
        error = str(e)
    
    conn.close()
    
    return templates.TemplateResponse(
        "search.html", 
        {
            "request": request, 
            "users": users, 
            "query": query,
            "sql_query": sql  # Показываем SQL запрос для демонстрации
        }
    )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа (уязвима к SQL-инъекциям)"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Обработка входа с SQL-инъекцией.
    Уязвимость: прямое включение пользовательского ввода в SQL-запрос.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # УЯЗВИМЫЙ КОД: прямое использование пользовательского ввода в SQL-запросе
    sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    try:
        cursor.execute(sql)
        user = cursor.fetchone()
    except Exception as e:
        user = None
        error = str(e)
    
    conn.close()
    
    if user:
        # В реальном приложении здесь была бы установка сессии
        return templates.TemplateResponse(
            "welcome.html", 
            {
                "request": request, 
                "user": user,
                "sql_query": sql  # Показываем SQL запрос для демонстрации
            }
        )
    else:
        return templates.TemplateResponse(
            "login.html", 
            {
                "request": request, 
                "error": "Неверные учетные данные",
                "username": username,
                "sql_query": sql  # Показываем SQL запрос для демонстрации
            }
        )

@app.get("/comments", response_class=HTMLResponse)
async def comments_page(request: Request):
    """
    Страница комментариев с XSS уязвимостью.
    Уязвимость: вывод пользовательского контента без экранирования.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT messages.*, users.username FROM messages JOIN users ON messages.user_id = users.id ORDER BY timestamp DESC")
    messages = cursor.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse(
        "comments.html", 
        {
            "request": request, 
            "messages": messages
        }
    )

@app.post("/comments")
async def add_comment(
    request: Request,
    content: str = Form(...),
    username: str = Form("guest")
):
    """
    Добавление комментария с XSS уязвимостью.
    Уязвимость: сохранение и вывод пользовательского контента без экранирования.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Находим ID пользователя (или создаем гостя)
    cursor.execute(f"SELECT id FROM users WHERE username = '{username}'")
    user = cursor.fetchone()
    
    if user:
        user_id = user['id']
    else:
        # Если пользователь не найден, используем ID гостя
        user_id = 0
    
    # Сохраняем комментарий БЕЗ очистки HTML
    cursor.execute(
        "INSERT INTO messages (user_id, content) VALUES (?, ?)",
        (user_id, content)
    )
    
    conn.commit()
    conn.close()
    
    return RedirectResponse("/comments", status_code=303)
@app.get("/demo")
async def demo_page(request: Request):
    """Страница с демонстрацией эксплуатации уязвимостей"""
    return templates.TemplateResponse("demo.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
