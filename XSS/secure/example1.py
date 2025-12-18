from flask import Flask, request, render_template, escape
import html

app = Flask(__name__)

@app.route('/search_safe')
def search_safe():
    query = request.args.get('q', '')
    
    # БЕЗОПАСНО: экранирование специальных HTML-символов
    escaped_query = escape(query)  # Используем html.escape
    
    # Альтернатива: использование шаблонов с автоматическим экранированием
    return render_template('search.html', query=escaped_query)

# search.html:
"""
<html>
<body>
    <h1>Результаты поиска: {{ query }}</h1>
    <p>Вы искали: {{ query }}</p>
</body>
</html>
"""

# Дополнительная защита: Content Security Policy
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response