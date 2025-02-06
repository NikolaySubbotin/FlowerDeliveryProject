GET_ORDERS_SQL = """
SELECT 
    o.id, 
    u.phone, 
    o.delivery_address, 
    o.status, 
    array_agg(p.name) as products 
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
SET status = %s 
WHERE id = %s;
"""