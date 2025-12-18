import psycopg2
from psycopg2 import sql

def search_products_safe(category, min_price):
    """Безопасная функция с параметризованными запросами"""
    conn = psycopg2.connect("dbname=shop user=postgres")
    cursor = conn.cursor()
    
    query_parts = ["SELECT * FROM products WHERE 1=1"]
    params = []
    
    if category:
        query_parts.append("AND category = %s")
        params.append(category)
    if min_price:
        query_parts.append("AND price >= %s")
        params.append(float(min_price))
    
    query = " ".join(query_parts)
    cursor.execute(query, params)
    
    results = cursor.fetchall()
    conn.close()
    return results