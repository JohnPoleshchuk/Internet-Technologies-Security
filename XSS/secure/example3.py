from fastapi import Form
import html
import bleach  # pip install bleach

# Настройка bleach для безопасного HTML
ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
}

@app.post("/comments/safe")
async def create_comment_safe(author: str = Form(...), content: str = Form(...)):
    """Безопасное создание комментария с санитизацией"""
    # БЕЗОПАСНО: экранирование имени и очистка контента
    safe_author = html.escape(author[:50])  # Ограничение длины
    
    # Очистка HTML с помощью bleach (разрешаем только безопасные теги)
    safe_content = bleach.clean(
        content, 
        tags=ALLOWED_TAGS, 
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    comment = Comment(
        id=str(uuid.uuid4()),
        author=safe_author,
        content=safe_content
    )
    comments_db.append(comment)
    return {"message": "Комментарий добавлен"}

@app.get("/comments/safe", response_class=HTMLResponse)
async def list_comments_safe():
    """Безопасное отображение комментариев"""
    return templates.TemplateResponse(
        "comments.html",
        {"comments": comments_db}  # Данные уже безопасны
    )

# comments.html (шаблон):
"""
<html>
<head>
    <title>Комментарии</title>
</head>
<body>
    <h1>Комментарии</h1>
    <ul>
    {% for comment in comments %}
        <li>
            <strong>{{ comment.author }}</strong> сказал:
            <div>{{ comment.content | safe }}</div>
        </li>
    {% endfor %}
    </ul>
    <form action="/comments/safe" method="post">
        Имя: <input type="text" name="author" maxlength="50"><br>
        Комментарий: <textarea name="content"></textarea><br>
        <button type="submit">Отправить</button>
    </form>
</body>
</html>
"""