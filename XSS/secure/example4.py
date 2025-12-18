from fastapi.middleware.cors import CORSMiddleware
import json

# Добавляем CSP middleware
from fastapi import Response

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

@app.get("/api/user/profile_safe")
async def get_profile_safe(credentials: HTTPBasicCredentials = Depends(security)):
    """Безопасный API endpoint"""
    if credentials.username not in users_db:
        return {"error": "Пользователь не найден"}
    
    user = users_db[credentials.username]
    
    # БЕЗОПАСНО: очистка пользовательского HTML
    safe_custom_html = bleach.clean(
        user.get("custom_html", ""),
        tags=[],  # Не разрешаем никакие теги
        strip=True
    )
    
    return {
        "username": credentials.username,
        "profile": user["profile"],
        "custom_html": safe_custom_html  # Очищенный HTML
    }

@app.get("/profile_safe", response_class=HTMLResponse)
async def profile_page_safe():
    """Безопасная страница профиля"""
    html_content = """
    <html>
    <head>
        <title>Профиль</title>
        <script>
            async function loadProfile() {
                const response = await fetch('/api/user/profile_safe', {
                    headers: {
                        'Authorization': 'Basic ' + btoa('admin:admin123')
                    }
                });
                const data = await response.json();
                
                // БЕЗОПАСНО: textContent для текста, createElement для HTML
                document.getElementById('username').textContent = data.username;
                document.getElementById('profile').textContent = data.profile;
                
                // Для custom_html используем безопасное добавление
                const customDiv = document.getElementById('custom-html');
                if (data.custom_html) {
                    // Используем DOMPurify если нужно разрешить безопасный HTML
                    // customDiv.innerHTML = DOMPurify.sanitize(data.custom_html);
                    customDiv.textContent = data.custom_html;
                }
            }
            
            // Альтернатива с DOMPurify
            function safeHTML(elementId, html) {
                const element = document.getElementById(elementId);
                if (window.DOMPurify) {
                    element.innerHTML = DOMPurify.sanitize(html);
                } else {
                    element.textContent = html;
                }
            }
        </script>
        <!-- Подключаем DOMPurify для безопасного рендеринга HTML -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/2.4.0/purify.min.js"></script>
    </head>
    <body onload="loadProfile()">
        <h1>Мой профиль</h1>
        <div id="profile-info">
            <h2 id="username"></h2>
            <p id="profile"></p>
            <div id="custom-html"></div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)