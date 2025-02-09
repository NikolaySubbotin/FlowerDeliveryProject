import sqlite3

DB_PATH = "your_database.db"


def get_user_telegram_id(order_id):
    """Получает Telegram ID клиента по ID заказа"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT users.telegram_id FROM orders
        JOIN users ON orders.user_id = users.id
        WHERE orders.id = ?
    """, (order_id,))

    result = cur.fetchone()
    conn.close()

    return result[0] if result else None

def update_order_status_in_db(order_id, new_status):
    """Обновляет статус заказа в базе данных"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(UPDATE_STATUS_SQL, (new_status, order_id))
    conn.commit()
    conn.close()

GET_ORDERS_SQL = """
SELECT 
    o.id, 
    u.phone, 
    o.delivery_address, 
    o.status, 
    GROUP_CONCAT(p.name, ', ') as products 
FROM 
    shop_order o
JOIN 
    main_customuser u ON o.user_id = u.id
JOIN 
    shop_orderitem oi ON o.id = oi.order_id
JOIN 
    flowers_bouquet p ON oi.product_id = p.id
GROUP BY 
    o.id;
"""

UPDATE_STATUS_SQL = """
UPDATE shop_order 
SET status = ? 
WHERE id = ?;
"""