import unittest
import sqlite3
from bot import Database  # Убедись, что импорт правильный

class BotDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.db.conn = sqlite3.connect(":memory:")  # Тест в памяти
        self.db.create_tables()

    def test_insert_order(self):
        self.db.add_order(user_id=1, status="new", delivery_address="ул. Ленина, 5", total_price=1000)
        orders = self.db.get_orders()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["total_price"], 1000)

if __name__ == "__main__":
    unittest.main()
