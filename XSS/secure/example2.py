from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import html

app = FastAPI()

@app.get("/search_safe")
async def search_safe(q: str = Query("")):
    """Безопасный поиск с экранированием HTML"""
    # БЕЗОПАСНО: экранирование всех специальных символов
    escaped_q = html.escape(q)
    
    html_content = f"""
    <html>
    <head>
        <title>Поиск</title>
        <meta http-equiv="Content-Security-Policy" content="default-src 'self'">
    </head>
    <body>
        <h1>Результаты поиска</h1>
        <p>Вы искали: {escaped_q}</p>
        <p>Найдено 10 результатов по запросу: {escaped_q}</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Использование Jinja2 с автоэкранированием
@app.get("/search_safe2")
async def search_safe2(request: Request, q: str = Query("")):
    """Безопасный поиск с использованием шаблонов Jinja2"""
    return templates.TemplateResponse(
        "search.html", 
        {"request": request, "query": q}  # Jinja2 автоматически экранирует
    )

# search.html (шаблон):
"""
<html>
<head>
    <title>Поиск</title>
</head>
<body>
    <h1>Результаты поиска</h1>
    <p>Вы искали: {{ query }}</p>
</body>
</html>
"""