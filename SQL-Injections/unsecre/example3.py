import mysql.connector

def update_user_email_unsafe(user_id, new_email):
    """Уязвимая функция обновления email пользователя"""
    conn = mysql.connector.connect(
        host="localhost",
        user="admin",
        password="password",
        database="app_db"
    )
    cursor = conn.cursor()
    
    # УЯЗВИМОСТЬ: динамическое построение SQL в хранимой процедуре
    query = f"""
    CREATE PROCEDURE IF NOT EXISTS UpdateEmail()
    BEGIN
        UPDATE users SET email = '{new_email}' WHERE id = {user_id};
    END
    """
    
    cursor.execute("DROP PROCEDURE IF EXISTS UpdateEmail")
    cursor.execute(query)
    cursor.callproc("UpdateEmail")
    conn.commit()
    
    print(f"Email обновлен для user_id={user_id}")
    
    conn.close()

# Пример эксплуатации:
# update_user_email_unsafe("1", "hacker@evil.com' WHERE id = 1 OR '1'='1")
# Обновит email всех пользователей