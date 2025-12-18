from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

# УЯЗВИМЫЙ КОД: прямое включение пользовательского ввода в HTML
@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    # УЯЗВИМОСТЬ: пользовательский ввод без экранирования
    html = f'''
    <html>
    <body>
        <h1>Результаты поиска: {query}</h1>
        <p>Вы искали: {query}</p>
    </body>
    </html>
    '''
    return render_template_string(html)

# Пример эксплуатации: 
# http://localhost:5000/search?q=<script>alert('XSS')</script>
# http://localhost:5000/search?q=<img src=x onerror=alert(document.cookie)>