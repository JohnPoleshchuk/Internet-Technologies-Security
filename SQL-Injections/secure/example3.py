import mysql.connector

def update_user_email_safe(user_id, new_email):
    """Безопасная функция с валидацией и параметризацией"""
    conn = mysql.connector.connect(
        host="localhost",
        user="admin",
        password="password",
        database="app_db"
    )
    cursor = conn.cursor()
    
    # БЕЗОПАСНО: параметризованный запрос без динамического SQL
    query = "UPDATE users SET email = %s WHERE id = %s"
    cursor.execute(query, (new_email, user_id))
    
    conn.commit()
    conn.close()