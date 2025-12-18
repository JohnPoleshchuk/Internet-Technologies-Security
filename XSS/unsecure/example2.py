from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
import html

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# УЯЗВИМЫЙ КОД 1: прямое включение пользовательского ввода в строку
@app.get("/search")
async def search_unsafe(q: str = Query("")):
    """Уязвимый поиск с отраженным XSS"""
    # УЯЗВИМОСТЬ: прямое включение в HTML без экранирования
    html_content = f"""
    <html>
    <head><title>Поиск</title></head>
    <body>
        <h1>Результаты поиска</h1>
        <p>Вы искали: {q}</p>
        <p>Найдено 10 результатов по запросу: {q}</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Пример эксплуатации:
# GET /search?q=<script>alert('XSS')</script>
# GET /search?q=<img src=x onerror=alert(document.cookie)>