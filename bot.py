import logging
from aiogram import Bot, Dispatcher, types, executor
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET")
COMMISSION_PERCENT = 10

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("💸 Пополнение баланса Steam\n\nВведите сумму (в рублях):")

@dp.message_handler(lambda message: message.text and message.text.isdigit())
async def process_amount(message: types.Message):
    amount = int(message.text)
    final = round(amount * (1 + COMMISSION_PERCENT / 100))
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✉ Я оплатил", callback_data=f"paid:{amount}:{final}"))
    await message.answer(
        f"Вы хотите пополнить: {amount} ₽\nС комиссией {COMMISSION_PERCENT}%: {final} ₽\n\n"
        f"Переведите на ЮMoney: `{YOOMONEY_WALLET}`\nПосле перевода нажмите кнопку.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("paid:"))
async def confirm_payment(c: types.CallbackQuery):
    _, amount, final = c.data.split(":")
    user = c.from_user
    await bot.send_message(
        ADMIN_ID,
        f"📥 Новый заказ от @{user.username} (ID: {user.id}):\n"
        f"- Запрошено: {amount} ₽\n- Оплачено: {final} ₽\n- ЮMoney: {YOOMONEY_WALLET}"
    )
    await c.answer("Заявка отправлена!")
    await bot.send_message(user.id, "✅ Ваша заявка принята. Ожидайте.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
