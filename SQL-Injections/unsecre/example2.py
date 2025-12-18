import psycopg2
from psycopg2 import sql

def search_products_unsafe(category, min_price):
    """Уязвимая функция поиска товаров с фильтрами"""
    conn = psycopg2.connect("dbname=shop user=postgres")
    cursor = conn.cursor()
    
    # УЯЗВИМОСТЬ: конкатенация SQL-фрагментов
    query = "SELECT * FROM products WHERE 1=1"
    
    if category:
        query += f" AND category = '{category}'"
    if min_price:
        query += f" AND price >= {min_price}"
    
    print(f"Выполняется запрос: {query}")
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    conn.close()
    return results

# Пример эксплуатации:
# search_products_unsafe("electronics' OR '1'='1", None) - вернет все товары
# search_products_unsafe("", "0; DELETE FROM products; --") - удалит все товары