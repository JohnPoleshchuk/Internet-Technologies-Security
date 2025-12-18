import sqlite3

def get_user_balance_unsafe(user_id):
    """Уязвимая функция для получения баланса пользователя"""
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    
    # УЯЗВИМОСТЬ: прямое включение user_id в запрос
    query = f"SELECT balance FROM accounts WHERE user_id = '{user_id}'"
    print(f"Выполняется запрос: {query}")  # Для отладки
    
    cursor.execute(query)
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else None

# Пример эксплуатации: 
# get_user_balance_unsafe("1' OR '1'='1") - вернет все балансы
# get_user_balance_unsafe("1'; DROP TABLE accounts; --") - уничтожит таблицу