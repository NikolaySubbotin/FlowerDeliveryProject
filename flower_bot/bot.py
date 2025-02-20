import sqlite3
import logging
from queries import GET_ORDERS_SQL, UPDATE_STATUS_SQL, DB_PATH
from queries import update_order_status_in_db
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from config import DB_PATH, TELEGRAM_TOKEN
from aiogram import Bot
from queries import get_user_telegram_id


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()

    def get_orders(self):
        self.cur.execute(GET_ORDERS_SQL)
        orders = self.cur.fetchall()

        order_dict = {}
        for order in orders:
            order_id = order[0]
            if order_id not in order_dict:
                order_dict[order_id] = {
                    "id": order[0],
                    "phone": order[1],
                    "address": order[2],
                    "status": order[3],
                    "products": []
                }
            order_dict[order_id]["products"].append(order[4])

        return list(order_dict.values())

    def update_status(self, order_id, status):
        self.cur.execute(UPDATE_STATUS_SQL, (status, order_id))
        self.conn.commit()


db = Database()

async def update_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    order_id = int(query.data.split('_')[1])
    new_status = "completed" if "complete" in query.data else "canceled"

    db.update_status(order_id, new_status)
    await query.answer("Статус заказа обновлён!")

    # Обновляем сообщение
    await order_detail(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌸 Бот цветочного магазина\n"
        "Команды:\n"
        "/orders - список заказов\n"
        "/help - справка"
    )


async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = db.get_orders()

    if not orders:
        await update.message.reply_text("❌ Заказов пока нет.")
        return

    keyboard = []
    for order in orders:
        btn = InlineKeyboardButton(
            f"Заказ #{order['id']} ({order['status']})",
            callback_data=f"order_{order['id']}"
        )
        keyboard.append([btn])

    await update.message.reply_text(
        "📦 Список заказов:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def order_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    order_id = int(query.data.split('_')[1])

    orders = db.get_orders()
    order = next((o for o in orders if o["id"] == order_id), None)

    if order:
        text = (
            f"🛍️ Заказ #{order['id']}\n"
            f"📞 Телефон: {order['phone']}\n"
            f"🏠 Адрес: {order['address']}\n"
            f"📦 Статус: {order['status']}\n"
            f"🌸 Товары: {', '.join(order['products'])}"
        )

        keyboard = [
            [InlineKeyboardButton("✅ Выполнен", callback_data=f"complete_{order_id}")],
            [InlineKeyboardButton("❌ Отменен", callback_data=f"cancel_{order_id}")]
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )



async def update_order_status(order_id, new_status):
    """Обновляет статус заказа и уведомляет клиента"""

    # Обновляем статус заказа в БД
    update_order_status_in_db(order_id, new_status)

    # Получаем Telegram ID клиента
    user_telegram_id = get_user_telegram_id(order_id)

    if user_telegram_id:
        status_messages = {
            "pending": "Ваш заказ принят в обработку!",
            "processing": "Ваш заказ готовится.",
            "completed": "Ваш заказ доставлен! Спасибо за покупку! 🌸",
            "canceled": "Ваш заказ был отменён. Если это ошибка, свяжитесь с нами."
        }

        message_text = status_messages.get(new_status, "Статус заказа изменён.")

        # Отправляем уведомление клиенту
        await bot.send_message(chat_id=user_telegram_id, text=message_text)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("orders", show_orders))
    app.add_handler(CallbackQueryHandler(order_detail, pattern=r"^order_"))
    app.add_handler(CallbackQueryHandler(update_status, pattern=r"^(complete|cancel)_"))

    app.run_polling()