import psycopg2
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from config import DB_CONFIG, TELEGRAM_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)

    def get_orders(self):
        with self.conn.cursor() as cursor:
            cursor.execute(GET_ORDERS_SQL)
            return cursor.fetchall()

    def update_status(self, order_id, status):
        with self.conn.cursor() as cursor:
            cursor.execute(UPDATE_STATUS_SQL, (status, order_id))
            self.conn.commit()


db = Database()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌸 Бот цветочного магазина\n"
        "Команды:\n"
        "/orders - список заказов\n"
        "/help - справка"
    )


async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = db.get_orders()

    keyboard = []
    for order in orders:
        btn = InlineKeyboardButton(
            f"Заказ #{order[0]} ({order[3]})",
            callback_data=f"order_{order[0]}"
        )
        keyboard.append([btn])

    await update.message.reply_text(
        "📦 Список заказов:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def order_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    order_id = query.data.split('_')[1]

    # Получаем данные заказа из БД
    orders = db.get_orders()
    order = next((o for o in orders if o[0] == int(order_id)), None)

    if order:
        text = (
            f"🛍️ Заказ #{order[0]}\n"
            f"📞 Телефон: {order[1]}\n"
            f"🏠 Адрес: {order[2]}\n"
            f"📦 Статус: {order[3]}\n"
            f"🌸 Товары: {', '.join(order[4])}"
        )

        keyboard = [
            [InlineKeyboardButton("✅ Выполнен", callback_data=f"complete_{order_id}")],
            [InlineKeyboardButton("❌ Отменен", callback_data=f"cancel_{order_id}")]
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def update_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action, order_id = query.data.split('_')
    status = 'completed' if action == 'complete' else 'cancelled'

    db.update_status(order_id, status)
    await query.answer(f"Статус заказа #{order_id} изменен на {status}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("orders", show_orders))
    app.add_handler(CallbackQueryHandler(order_detail, pattern=r"^order_"))
    app.add_handler(CallbackQueryHandler(update_status, pattern=r"^(complete|cancel)_"))

    app.run_polling()