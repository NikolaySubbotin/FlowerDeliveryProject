import unittest
import sqlite3
from bot import Database  # Убедись, что импорт правильный

class BotDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.db.cur.execute("DELETE FROM shop_order")
        self.db.conn.commit()

    def test_insert_order(self):
        self.db.add_order(user_id=1, status="new", delivery_address="ул. Ленина, 5", total_price=1000)
        self.db.conn.commit()  # Принудительно фиксируем изменения
        orders = self.db.get_orders()

        print("Список заказов:", orders)  # Выведем весь список

        if orders:  # Проверяем, есть ли хотя бы один заказ
            print("Первый заказ:", orders[0])
        else:
            print("Заказы не найдены!")

        self.assertGreater(len(orders), 0, "Список заказов пуст!")
        self.assertEqual(orders[0]["total_price"], 1000)

if __name__ == "__main__":
    unittest.main()
