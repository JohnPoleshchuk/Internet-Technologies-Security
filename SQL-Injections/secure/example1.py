import sqlite3

def get_user_balance_safe(user_id):
    """Безопасная функция с параметризованным запросом"""
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    
    # БЕЗОПАСНО: использование параметризованного запроса
    query = "SELECT balance FROM accounts WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None